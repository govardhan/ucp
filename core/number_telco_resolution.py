from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVNumberTelcoResolution:
  def __init__(self):
    self.init()
  
  def reload(self):
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core") 
    l_res, self.rowcount, self.num_telco_map = DBPool().execute_query("select id, num_pattern, telco_id, flags, remarks from tb_number_telco_map order by id desc", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "number telco map failed to initiate. verify tb_number_telco_map table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("Number mapping in search order")
    logger.info("id	num_pattern	telco_id	flags		remarks")
    logger.info("-" * 70)
    for l_row in self.num_telco_map:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}".format(l_row['id'], l_row['num_pattern'], l_row['telco_id'], l_row['flags'], l_row['remarks']))

  def get_telco_id(self, p_msisdn):
    logger.debug("params - p_msisdn {0} ".format(p_msisdn))
    for l_row in self.num_telco_map:
      if (None != re.match(l_row['num_pattern'], p_msisdn)):
        logger.info("Matchfound for p_msisdn = {0}, telco_id = {1}, flags = {2}, id = {3}".format(p_msisdn, l_row['telco_id'], l_row['flags'], l_row['id']) )
        return True, l_row['telco_id'], l_row['flags']

    #End of for loop. No match found. So return False
    logger.warn("None of the number pattern matched for p_msisdn = {0}".format(p_msisdn) )
    return False, None, None

#Run unit tests
if __name__ == "__main__":
  init_logging("voiceapp.log")
  conf = UVConfig()
  conf.init("/root/ucp/ucp/conf/ucp.conf")

  l_num_telco_mapper = UVNumberTelcoResolution()
  logger.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("5555")))
  logger.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("12345")))
  logger.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("919886161856")))
  logger.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("966551123728")))


