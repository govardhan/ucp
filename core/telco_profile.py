import sys, os.path
from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVTelcos(object):
  def __init__(self):
    self.init()

  def reload(self):
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.telcos = DBPool().execute_query("select id, telco_id from tb_telcos", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "telcos ids failed to initiate. verify tb_telcos table result {0} rows (1)".format(l_res, self.rowcount)
    for l_row in self.telcos:
      logger.info("{0}\t{1}".format(l_row['id'], l_row['telco_id']))

  def is_telco_id_exists(self, p_telco_id):
    """ is_telco_id_exists returns true if p_telco_id found in the list.
        A generator expression in conjuction with python built in construct any will do this job
        any(iterable) -> Return True if any element of the iterable is true
    """
    any(l_row['telco_id'] for l_row in self.telcos if p_telco_id == l_row['telco_id'])
    
@singleton
class UVTelcoProfile(object):
  def __init__(self):
    self.init()
  
  def reload(self):
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core") 
    l_res, self.rowcount, self.telco_profiles = DBPool().execute_query("select id, telco_id, profile_key, profile_value from tb_telco_profile", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "telco profile failed to initiate. verify tb_telco_profile table result {0} rows (1)".format(l_res, self.rowcount)

    for l_row in self.telco_profiles:
      logger.info("{0}\t{1}\t{2}\t{3}".format(l_row['id'], l_row['telco_id'], l_row['profile_key'], l_row['profile_value']))


  def get(self, telco_id, key ):
    logger.debug("params - telco_id {0}, key {1}".format(telco_id, key))
    for l_row in self.telco_profiles:
      if( (None != re.match(l_row['telco_id'], telco_id)) and (None != re.match(l_row['profile_key'], key)) ):
        logger.debug("Matchfound for telco_id {0}, key {1} val {2}".format(telco_id, key, l_row["profile_value"]))
        return True, l_row["profile_value"]
      else:
        logger.warn("No Match found for telco_id {0}, key {1}".format(telco_id, key))
        return False, None

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

  l_tp = UVTelcoProfile()
  print l_tp.get("91.BH", "lang")
  print l_tp.get("91.BH", "what")


