import os, sys
import logging

try:
  UCPHOME=os.environ['UCPHOME']
except:
  UCPHOME="/home/uvadmin/ucp/"
  print "UCPHOME set to /home/uvadmin/ucp/"
sys.path.append(UCPHOME+"core")

from config import UVConfig
from dbpool import DBPool
from uv_decorators import *
from user_profile import UVUserProfile
from relations import UVRelations
from feature_profile import UVFeatureProfile

logger = logging.getLogger('vt_app')

@singleton
class VTDiscTweeters(object):
  def __init__(self):
    self.init()
  def reload():
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
  
  def get(self, uuid, telco_id = '.*', channel = 'ivr'):
    l_query = "select tweeter_list from tb_premium_tweeter_discovery where telco_id REGEXP '^{0}$' and channel REGEXP '^{1}$' and now() > start_ts and now() <= end_ts".format(telco_id, channel)  
    l_res, self.rowcount, l_tweeters = DBPool().execute_query(l_query, self.db_name)
    assert (l_res == True) , "premium tweeters failed to initialize. verify tb_premium_tweeter_discovery table result {0} rows (1)".format(l_res, self.rowcount)

    if(self.rowcount == 0):
      logger.warn("{0} no tweeters found to discover. query [{1}]".format(uuid, l_query) )
      return False, None
    
    if(self.rowcount > 1):
      logger.warn("{0} more than one set of tweeters found to discover. query [{1}]".format(uuid, l_query) )

    self.tweeters = [t for t in l_tweeters[0]['tweeter_list'].split(',') if len(t.strip()) > 0]
    if( len(self.tweeters) == 0):
      logger.warn("{0} Empty tweeter list in discovery. query [{1}]".format(uuid, l_query) )
      return False, None

    return True, self.tweeters

  def filter(self, msisdn):
    """
    This method filter tweeter list self.tweeters with those tweeters msisdn following actively  
    """
    l_found, l_menu_size = UVFeatureProfile().get_profile_value('vt_disc', 'tweeter_menu_size')
    if(False == l_found):
      l_menu_size = 0
    else:
      l_menu_size = int(l_menu_size)
    logger.debug("msisdn {0}, l_menu_size {1}".format(msisdn, l_menu_size))

    l_exists, l_f_msisdns = UVRelations().get(msisdn, "follow", "active")
    if(l_exists):
      logger.debug("follower {0} actively following {1}".format(msisdn, l_f_msisdns))
      l_f_names = [ UVUserProfile().get(l_msisdn, "user_name")[1] for l_msisdn in l_f_msisdns ]
      logger.debug("follower {0} actively following {1}".format(msisdn, l_f_names))
      l_remain = list(set(self.tweeters) - set(l_f_names))
      logger.info("follower {0} can follow {1}".format(msisdn, l_remain))
      return l_remain[:l_menu_size]
    else:
      logger.info("follower {0} can follow {1}".format(msisdn, self.tweeters[:l_menu_size]))
      return self.tweeters[:l_menu_size]


#Run unit tests
if __name__ == "__main__":
  try:
    UCPHOME=os.environ['UCPHOME']
  except:
    UCPHOME="/home/uvadmin/ucp/"
    print "UCPHOME set to /home/uvadmin/ucp/"
  sys.path.append(UCPHOME+"core")

  sys.path.append(UCPHOME+"core")
  logging.config.fileConfig(UCPHOME+'conf/vt_logging.conf')
  conf = UVConfig()
  conf.init(UCPHOME+"/conf/ucp.conf")

  l_found, l_tweeters = VTDiscTweeters().get('1234')
  print l_tweeters
  print VTDiscTweeters().filter("919999900705")
  
