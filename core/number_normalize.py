from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re
import sys

logger = logging.getLogger('ucp_core')

@singleton
class UVNormalizer:
  def __init__(self):
    self.init()
  
  def reload(self):
    self.normalize_rules = None
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core") 
    l_res, self.rowcount, self.normalize_rules = DBPool().execute_query("select id, in_pattern, out_pattern, telco_id, channel, remarks from tb_number_normalizer order by id desc", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "number normalizer failed to initiate. verify tb_number_normalizer table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("Normalized rules in search order top to bottom")
    logger.info("id	in_pattern	out_pattern	telco_id	channel		remarks")
    logger.info("-" * 70)
    for l_row in self.normalize_rules:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(l_row['id'], l_row['in_pattern'], l_row['out_pattern'], l_row['telco_id'], l_row['channel'], l_row['remarks']))

  def normalize(self, p_msisdn, p_telco_id = ".*", p_channel = ".*"):
    logger.debug("params - p_msisdn {0}, p_telco_id {1}, p_channel {2}".format(p_msisdn, p_telco_id, p_channel))
    for l_row in self.normalize_rules:
      if( (None != re.match(l_row['in_pattern'], p_msisdn)) and (None != re.match(l_row['telco_id'], p_telco_id)) and (None != re.match(l_row['channel'], p_channel))  ):
        l_norm_msisdn = re.sub(l_row['in_pattern'], l_row['out_pattern'], p_msisdn)
        logger.info("Matchfound. p_msisdn = {0}, l_norm_msisdn = {1}, id = {2}, in_pattern = {3}, out_pattern = {4}, telco_id = {5}, channel = {6}, p_telco_id = {7}. p_channel = {8}".format(p_msisdn, l_norm_msisdn, l_row['id'], l_row['in_pattern'], l_row['out_pattern'], l_row['telco_id'], l_row['channel'], p_telco_id, p_channel) )
        return True, l_norm_msisdn

    #End of for loop. No match found. So return False
    logger.warn("No normalizer match not found. p_msisdn = {0}, p_telco_id = {1}. p_channel = {2}".format(p_msisdn, p_telco_id, p_channel) )
    return False, p_msisdn

  def is_pattern_exists(self, pattern, inout="in"):
    logger.debug("params - pattern {0}, inout {1}".format(pattern, inout))
    if(inout == "in"):
      l_col = "in_pattern"
    else:
      l_col = "out_pattern"
    for l_row in self.normalize_rules:
      if( l_row[l_col] == pattern):
        logger.info("pattern {0} found in row id {1}".format(pattern, l_row['id']))
        return True
    logger.info("pattern {0} not found".format(pattern))
    return False
    
  def add(self, in_pattern, out_pattern, telco_id='.*', channel='.*', remarks=''):
    logger.debug("params - in_pattern {0}, out_pattern {1}, telco_id {2}, channel {3}, remarks {4}".format(in_pattern, out_pattern, telco_id, channel, remarks))
    l_query = "insert into tb_number_normalizer(in_pattern, out_pattern, telco_id, channel, remarks) values('{0}','{1}','{2}','{3}','{4}')".format(in_pattern, out_pattern, telco_id, channel, remarks)
    l_res, l_rc, _ = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logging.info("in_pattern {0}, out_pattern {1}, telco_id {2}, channel {3}, remarks {4} had been added in db".format(in_pattern, out_pattern, telco_id, channel, remarks))
      self.reload()
      return True
    else:
      logging.info("failed to add in_pattern {0}, out_pattern {1}, telco_id {2}, channel {3}, remarks {4} in db".format(in_pattern, out_pattern, telco_id, channel, remarks))
      return False
    
@singleton
class UVDeNormalizer:
  def __init__(self):
    self.init()

  def reload(self):
    self.denormalize_rules = None
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.denormalize_rules = DBPool().execute_query("select id, in_pattern, out_pattern, telco_id, channel, remarks from tb_number_denormalizer order by id desc", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "number denormalizer failed to initiate. verify tb_number_normalizer table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("DeNormalized rules in search order top to bottom")
    logger.info("id     in_pattern      out_pattern     telco_id        channel         remarks")
    logger.info("-" * 70)
    for l_row in self.denormalize_rules:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(l_row['id'], l_row['in_pattern'], l_row['out_pattern'], l_row['telco_id'], l_row['channel'], l_row['remarks']))

  def denormalize(self, p_msisdn, p_telco_id = ".*", p_channel = ".*"):
    logger.debug("params - p_msisdn {0}, p_telco_id {1}, p_channel {2}".format(p_msisdn, p_telco_id, p_channel))
    for l_row in self.denormalize_rules:
      if( (None != re.match(l_row['in_pattern'], p_msisdn)) and (None != re.match(l_row['telco_id'], p_telco_id)) and (None != re.match(l_row['channel'], p_channel))  ):
        l_norm_msisdn = re.sub(l_row['in_pattern'], l_row['out_pattern'], p_msisdn)
        logger.info("Matchfound. p_msisdn = {0}, l_norm_msisdn = {1}, id = {2}, in_pattern = {3}, out_pattern = {4}, telco_id = {5}, channel = {6}, p_telco_id = {7}. p_channel = {8}".format(p_msisdn, l_norm_msisdn, l_row['id'], l_row['in_pattern'], l_row['out_pattern'], l_row['telco_id'], l_row['channel'], p_telco_id, p_channel) )
        return True, l_norm_msisdn

    #End of for loop. No match found. So return False
    logger.warn("No normalizer match not found. p_msisdn = {0}, p_telco_id = {1}. p_channel = {2}".format(p_msisdn, p_telco_id, p_channel) )
    return False, p_msisdn


  def is_pattern_exists(self, pattern, inout="in"):
    logger.debug("params - pattern {0}, inout {1}".format(pattern, inout))
    if(inout == "in"):
      l_col = "in_pattern"
    else:
      l_col = "out_pattern"
    for l_row in self.denormalize_rules:
      if( l_row[l_col] == pattern):
        logger.info("pattern {0} found in row id {1}".format(pattern, l_row['id']))
        return True
    logger.info("pattern {0} not found".format(pattern))
    return False
    
  def add(self, in_pattern, out_pattern, telco_id='.*', channel='.*', remarks=''):
    logger.debug("params - in_pattern {0}, out_pattern {1}, telco_id {2}, channel {3}, remarks {4}".format(in_pattern, out_pattern, telco_id, channel, remarks))
    l_query = "insert into tb_number_denormalizer(in_pattern, out_pattern, telco_id, channel, remarks) values('{0}','{1}','{2}','{3}','{4}')".format(in_pattern, out_pattern, telco_id, channel, remarks)
    l_res, l_rc, _ = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logging.info("in_pattern {0}, out_pattern {1}, telco_id {2}, channel {3}, remarks {4} had been added in db".format(in_pattern, out_pattern, telco_id, channel, remarks))
      self.reload()
      return True
    else:
      logging.info("failed to add in_pattern {0}, out_pattern {1}, telco_id {2}, channel {3}, remarks {4} in db".format(in_pattern, out_pattern, telco_id, channel, remarks))
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

  l_normalizer = UVNormalizer()
  l_found, l_result = l_normalizer.normalize("9886161856")
  print l_result,l_result
  l_found, l_result = l_normalizer.normalize("9886161856", p_telco_id = "91.*")
  print l_result, l_result
  
  print l_normalizer.is_pattern_exists("440")
  print l_normalizer.is_pattern_exists("444")
  print l_normalizer.is_pattern_exists("4444")
  print l_normalizer.add("4444", '1', '91.BH', 'sms', "test")
  print l_normalizer.is_pattern_exists("4444")

  l_denormalizer = UVDeNormalizer()
  print l_denormalizer.is_pattern_exists("1")
  print l_denormalizer.is_pattern_exists("4444")
  print l_denormalizer.add("4444", '1', '91.BH', 'sms', "test")
  print l_denormalizer.is_pattern_exists("4444")
