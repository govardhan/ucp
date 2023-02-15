from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVContent:
  def __init__(self):
    self.init()
    self.tags = {"all":1, "friends":2, "family":4, "friends_family":6}

  def reload():
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    #TODO load and cache most recent premium tweeter content
  
  def add_content(self, msisdn, telco_id, type, content, length, tags=1, ref_content_id=0):
    logger.debug("params msisdn {0}, telco_id {1}, type {2}, content {3}, length {4}, tags {5}, ref_content_id {6}".format(msisdn, telco_id, type, content, length, tags, ref_content_id))
    l_query = "insert into tb_content(msisdn, telco_id, type, content, length, tags, ref_content_id) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(msisdn, telco_id, type, content, length, tags, ref_content_id)
    l_res, l_rc, l_tmp = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logging.info("{0} type {1} added in db for {2} - telco_id {3}, length {4}".format(content, type, msisdn, telco_id,  length))
      return True
    else:
      logging.error("Failed to add content for {0} - telco_id {1}, length {2}, query [{3}]".format(msisdn, msisdn, length, l_query))
      return False

 
  def get_content(self, msisdn, type, media_type="audio"):
    logger.debug("params msisdn {0}, tyoe {1}".format(self, msisdn, type))
    #TODO this query performance shall be improved just by using msisdn in where clause
    # and apply remaining filters in logic instead in query
    l_query = "select content_id, media_type, content, length, tags, ref_content_id from  tb_content where msisdn='{0}' and type='{1}' and media_type='{2}' and state != 'del' or state != 'abuse' order by create_ts desc".format(msisdn, type, media_type)
    l_res, l_size, l_content = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      return l_size, l_content
    else:
      return 0, None

  def get_content_byid(self, content_id):
    logger.debug("params content_id {0}".format(self, content_id))
    l_query = "select msisdn, telco_id, media_type, state, type, content, create_ts, ttl, channel, length, tags, ref_content_id from  tb_content where content_id='{0}'".format(content_id)
    logger.debug(l_query)
    l_res, l_size, l_content = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      return True, l_content
    else:
      return False, None

  def get_content_by_ref_id(self, ref_content_id, content_type="rep2tweet"):
    logger.debug("params content_id {0}".format(self, content_id))
    l_query = "select msisdn, telco_id, media_type, state, type, content, create_ts, ttl, channel, length, tags, ref_content_id from  tb_content where ref_content_id='{0}' and type = '{1}'".format(ref_content_id, content_type)
    logger.debug(l_query)
    l_res, l_size, l_content = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      return True, l_content
    else:
      return False, None

  def set_state(self, content_id, state):
    logger.debug("params content_id {0} state {1}".format(self, content_id, state))
    l_query = "update tb_content set state = '{0}' where content_id='{1}'".format(state, content_id)
    logger.debug(l_query)
    l_res, l_size = DBPool().execute_query(l_query, self.db_name)
    return l_res

  def set_by_content_id(self, content_id, key, val):
    logger.debug("params content_id {0} key {1} val {2}".format(self, content_id, key, val))
    l_query = "update tb_content set {0} = '{1}' where content_id = '{2}'".format(key, val, content_id)
    l_res, l_rc, l_tmp = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logger.info("{0} content_id's {1} set to {2}".format(msisdn, key, val))
    else:
      logger.error("Failed to set {0} content_id's {1} to {2}. query [{3}]".format(content_id, key, val, l_query))
    return l_res

@singleton
class UVContentActivity:
  def __init__(self):
    self.init()

  def reload():
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")

  def onread(self, uuid, msisdn, content):
    self.add(uuid, msisdn, "read", content['content_id'], content['ref_content_id'])

  def onlike(self, uuid, msisdn, content):
    self.add(uuid, msisdn, "like", content['content_id'], content['ref_content_id'])

  def onshare(self, uuid, msisdn, content):
    self.add(uuid, msisdn, "share", content['content_id'], content['ref_content_id'])

  def onreply(self, uuid, msisdn, content):
    self.add(uuid, msisdn, "reply", content['content_id'])

  def ondel(self, uuid, msisdn, content):
    UVContent().set_state(content['content_id'], "del")
    self.add(uuid, msisdn, "del", content['content_id'])

  def onsave(self, uuid, msisdn, content):
    UVContent().set_state(content['content_id'], "save")
    self.add(uuid, msisdn, "save", content['content_id'])

  def onabuse(self, uuid, msisdn, content):
    self.add(uuid, msisdn, "abuse", content['content_id'])

  def add(self, uuid, msisdn, activity, content_id):
    self.add(uuid, msisdn, activity, content_id, 0)

  def add(self, uuid, msisdn, activity, content_id, ref_content_id):
    l_query = "insert into tb_content_activity(content_id, msisdn, activity, activity_ts) values('{0}', '{1}', '2', now() )".format(content_id, msisdn, activity)
    l_res, l_size, _ = DBPool().execute_query(l_query, self.db_name)
    if(l_res or l_size != 1):
      logger.warn("{0} unable to insert {1} activity into content activity. query {2}".format(uuid, activity, l_query))

    #TODO can this be done/evaluate with Neo4j with more depth?
    if(int(ref_content_id) > 0):
      l_query = "insert into tb_content_activity(content_id, msisdn, activity, activity_ts) values('{0}', '{1}', '{2}', now() )".format(ref_content_id, msisdn, activity)
      l_res, l_size, _ = DBPool().execute_query(l_query, self.db_name)
      if(l_res or l_size != 1):
        logger.warn("{0} unable to insert {1} activity into content activity. query {2}".format(uuid, activity, l_query))
    else:
      logger.debug("{0} ref_content_id not found for content_id {1}. Ignoring {2} activity".format(uuid, content['content_id'], activity))

#Run unit tests
if __name__ == "__main__":
  conf = UVConfig()
  l_ucphome = "/home/uvadmin/ucp/"
  conf.init(l_ucphome+"conf/ucp.conf")

