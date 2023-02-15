from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVRelations:
  """
    'one2one','follow','invite','barred','friend','family' ... are some of the relations
  """
  def __init__(self):
    self.init()

  def reload():
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    #TODO load and cache most active relations
  
  def create_relation(self, who, whom, relation="follow", state="active", channel="ivr"):
    logger.debug("params who {0}, whom {1}, relation {2}, state {3}, channel {4}".format(who, whom, relation, state, channel))
    l_query = "insert into tb_relations (who, whom, relation, state, channel, create_ts) values('{0}', '{1}', '{2}', '{3}', '{4}', now())".format(who, whom, relation, state, channel)
    logger.debug(l_query)
    l_res, l_rowcount, l_tmp = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logger.info("{0} relation created between {1} and {2} iva {3} channel with state {4}".format(relation, who, whom, channel, state ))
      return True
    else:
      logger.error("failed to create relation between {1} and {2} iva {3} channel with state {4}".format(relation, who, whom, channel, state ))
      return False
    
  def get_simplex_relation(self, who, whom, relation="follow"):
    logger.debug("params who {0}, whom {1}, relation {2}".format(who, whom, relation))
    l_res, l_rc, l_row = DBPool().execute_query("select state, channel, create_ts, update_ts from  tb_relations where who='{0}' and whom='{1}' and relation='{2}'".format(who, whom, relation), self.db_name)
    if(l_res and l_rc > 0):
      l_state = l_row[0]['state']
      l_channel = l_row[0]['channel']
      l_create_ts = l_row[0]['create_ts']
      l_update_ts = l_row[0]['update_ts']
      return True, l_state, l_channel, l_create_ts, l_update_ts
    else:
      return False, None, None, None, None
  def is_relation_exists(self, who, whom, relation="follow"):
    l_yesorno, l_state, _, _, _ = self.get_simplex_relation(who, whom, relation)
    return l_yesorno, l_state

  def update_relation(self, who, whom, relation, state):
    logger.debug("params who {0}, whom {1}, relation {2} state {3}".format(who, whom, relation, state))
    l_query = "update tb_relations set state = '{0}' where who='{1}' and whom='{2}' and relation='{3}'".format(state, who, whom, relation)
    l_res, _, _ = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logger.debug("{0} relation updated to {1} between {2} and {3}".format(relation, state, who, whom))
    else:
      logger.error("failed to update {0} relation to {1} between {2} and {3}. query {4}".format(relation, state, who, whom, l_query))


  def get(self, who, relation = "follow", state="active"):
    """
    Returns 'whom' list with the given relation and state
    """
    logger.debug("params who {0}, relation {1} state {2}".format(who, relation, state))
    l_query = "select whom from tb_relations where who = '{0}' and relation = '{1}' and state = '{2}'".format(who, relation, state)
    l_res, l_rc, l_rows = DBPool().execute_query(l_query, self.db_name)
    if(l_res == True):
      if(l_rc == 0):
        logger.debug("{0} do not have any {1} relation with {2} status".format(who, relation, state))
        return False, []
      else:
        logger.debug("{0} have {1} {2} relation with {3} status".format(who, l_rc, relation, state))
        return True, [ l_row['whom'] for l_row in l_rows]
    else:
      log.error("Query execution failed [{0}]".format(l_query))
      return False, []

  def get_non_direct(self, who, relation="follow", howmany=10):
    #TODO take advanatage of neo4j
    pass    
 
#Run unit tests
if __name__ == "__main__":
  conf = UVConfig()
  #l_ucphome = UVCache().get("UCPHOME")
  l_ucphome = "/home/uvadmin/ucp/"
  conf.init(l_ucphome+"conf/ucp.conf")
  UVRelations().create_relation("a", "b")
  l_found, l_state, l_channel, l_create_ts, l_update_ts = UVRelations().get_simplex_relation("a", "b")
  if(l_found):
    print("relation found. l_state = {0}, l_channel = {1}, l_create_ts = {2}, l_update_ts = {3}".format(l_found, l_state, l_channel, l_create_ts, l_update_ts))
  else:
    print("relaton not found for {0} & {1}".format("a", "b"))

  l_found, l_state, l_channel, l_create_ts, l_update_ts = UVRelations().get_simplex_relation("x", "y")
  if(l_found):
    print("relation found. l_state = {0}, l_channel = {1}, l_create_ts = {2}, l_update_ts = {3}".format(l_found, l_state, l_channel, l_create_ts, l_update_ts))
  else:
    print("relaton not found for {0} & {1}".format("x", "y"))

  l_found, l_li = UVRelations().get("919999900705", "follow", "active")
  print l_found
  print l_li
