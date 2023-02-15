import sys, os.path
from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVContentProvider(object):
  def __init__(self):
    self.init()

  def reload(self):
    self.cps = None
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.cps = DBPool().execute_query("select id, cp_name, service_name from tb_content_provider order by id desc", self.db_name)
    assert (l_res == True ) , "no content providers or failed to initiate. verify tb_content_provider table result {0} rows (1)".format(l_res, self.rowcount)
    for l_row in self.cps:
      logger.info("{0}\t{1}".format(l_row['id'], l_row['cp_name'], l_row['service_name']))

  def is_cp_exists(self, cp_name):
    logger.debug("params - cp_name {0}".format(cp_name))
    for l_row in self.cps:
      if( l_row['cp_name'] ==  cp_name):
        logger.debug("Matchfound for cp_name {0}".format(cp_name))
        return True
      else:
        logger.warn("No Match found for cp_name {0}".format(cp_name))
    return False

  def get_cp_name(self, service_name):
    logger.debug("params - service_name {0}".format(service_name))
    for l_row in self.cps:
      if( l_row['service_name'] == service_name):
        logger.debug("Matchfound for service_name {0} - {1} cp_name {2}".format(service_name, l_row['service_name'], l_row["cp_name"]))
        return True, l_row["cp_name"]
      else:
        logger.warn("No Match found for service_name {0}".format(service_name))
        return False, None

  def add(self, cp_name, service_name):
    #TODO check whetehr service_name exists
    logger.debug("params cp_name {0}, service_name {1}".format(cp_name, service_name))
    l_query = "insert into tb_content_provider(cp_name, service_name) values('{0}', '{1}')".format(cp_name, service_name)
    l_res, l_rc, l_tmp = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logging.info("cp_name {0} service_name {1} added in db".format(cp_name, service_name))
      self.reload()
      return True
    else:
      logging.info("failed to add cp_name {0} service_name {1} in db".format(cp_name, service_name))
      return False

#Run unit tests
if __name__ == "__main__":
  try:
    UCPHOME=os.environ['UCPHOME']
  except:
    UCPHOME="/home/uvadmin/ucp/"
    print "UCPHOME set to /home/uvadmin/ucp/"
  sys.path.append(UCPHOME+"core")

  logging.config.fileConfig(UCPHOME+'conf/vt_logging.conf')
  conf = UVConfig()
  conf.init(UCPHOME+"/conf/ucp.conf")

  l_cp = UVContentProvider()
  print l_cp.is_cp_exists("vt")
  print l_cp.add("sony", "govi")
