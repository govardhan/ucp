from ConfigParser import SafeConfigParser
import os.path
import codecs
import logging
import logging.config
from genutils import *
from uv_decorators import *

logger = logging.getLogger('ucp_core')

@singleton
class UVConfig(object):
  """ This class used for initilizing the configuration parameters for UCP application """
  def __init__(self):
    """ 
    Constructior for UVConfig. It initilizes the class member m_initialized to zero.
    if m_initialized is "0" then no configuration parameters are initialized from configuration file.
    This variable would be made it to "1" after initializing the configuration parameters 
    """
    self.m_initialized = 0

  def init(self, p_filename='ucp.conf'):
    """
    Description : Method to initialize the configuration parameters from configuration file
    Input       : 
      p_filename - Configuration file name along with file path
    Output      : none
    Algoritham  :
      1) Initialize the member variable conf_filename with input file name. 
      2) Validate the file name. It should not be null. And path and file should be valid. 
         If it is invalid through an error and raise the exception.
      3) Initialize the member variable parser with object SafeConfigParser.
      4) Open the file in read mode and parse the content of file.
      5) Initialize the member variable m_initialized with "1".
    """
    self.conf_filename = p_filename
    try:
      assert (len(self.conf_filename) != 0 and os.path.isfile(self.conf_filename) ) , "config file {0} is not valid".format(self.conf_filename)
    except AssertionError:
      logger.exception("config file {0} is not valid".format(self.conf_filename))
      raise

    logger.info("config filename {0}".format(self.conf_filename)) 

    self.parser = SafeConfigParser()
    with codecs.open(self.conf_filename, 'r', encoding='utf-8') as file_des:
      self.parser.readfp(file_des)

    for section_name in self.parser.sections():
      logger.info("section {0}".format(section_name)) 
      for key, value in self.parser.items(section_name):
        logger.info("config key = {0}, value = {1}".format(key, value))
      logger.info("")

    self.m_initialized = 1


  def get_config_value(self, p_section_name, p_key):
    """
    Description : Method to get the configuration parameter value
    Input       : 
      p_section_name - Configuration section name
      p_key          - Configuration parameter name
    Output      :
      If input configuration parameter present rerutn configuration value else none.
    Algoritham  :
      1) Verify wether the configuration parameters are initilized or not. If not raise an error.
      2) Verify wether the configuration section and key present or not. If present return the 
         configuration parameter value. else return none.
    """
    try:
      assert self.m_initialized == 1, "UVConfig class has not yet initialized with config file"
    except AssertionError:
      logger.exception("UVConfig class has not yet initialized with config file")
      raise
        
    if self.parser.has_option(p_section_name, p_key):
      return self.parser.get(p_section_name, p_key)
    else:
      logger.warn("Config section {0}, key {1} not found in config file {2}".format(p_section_name, p_key, self.conf_filename))      
      return None


if __name__ == "__main__":
  #conf = UVConfig("/root/ucp/ucp/conf/ucp.conf")
  init_logger("voiceapp.log")
  conf = UVConfig()
  conf.init("/root/ucp/ucp/conf/ucp.conf")
  
  
  print "Start testing"
  print conf.get_config_value("core","logfile_name")
  print conf.get_config_value("database","db_user_name")
  print conf.get_config_value("database","logfile_path")
  print conf.get_config_value("database","db_name.core")
  print conf.get_config_value("database", "db_user")
 
