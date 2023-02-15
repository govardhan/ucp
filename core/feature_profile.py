from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVFeatures(object):
  """ Calss for maintaining the feature details """
  def __init__(self):
    """
    Constructor for the class UVFeatures. It calls self.init() method which loads the feature name and feature name details from database.
    """
    self.init()
  def reload():
    """
    Description : Function to reload the feature name details from database.
                  This would be used when new feature added to database.
    Input       : none
    Output      : none
    Algoritham  : call the function self.init()
    """
    self.init()

  def init(self):
    """
    Description : Function to load the feature name details from database.
    Input       : none
    Output      : none
    Algoritham  : 
      1) Get the configured database values 
      2) Execute the query on table tb_features to get the feature name details
      3) Store the details in self.features and number of features in self.rowcount 
    """
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.features = DBPool().execute_query("select id, feature_name, feature_group, remarks from tb_features order by id", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "features failed to initiate. verify tb_features table result {0} rows (1)".format(l_res, self.rowcount)

    print self.features
    for l_row in self.features:
      logger.info("{0}\t{1}\t{2}\t{3}".format(l_row['id'], l_row['feature_name'], l_row['feature_group'], l_row['remarks']))
    
  def get_feature_group(self, p_feature_name):
    """
    Description : Function to get the Feature name and Feature group details
    Input       : feature name 
    Output      : returns Feature group on success , else returns none
    Algoritham  : 
      1) Loop through all the features
      2) If input serivce id is matching then retrun feature name and feature group
      3) If loop is completed then return none
    """
    for l_srvc_row in self.features:
      if( l_srvc_row['feature_name'] == p_feature_name):
        return l_srvc_row['feature_group']
    return None


@singleton
class UVFeatureMap(object):
  """ Class to derive the feature name for the request/call """
  def __init__(self):
    """    
    Constructor for the class UVFeatureMap. It calls self.init() method which loads the feature derivation rules from database.
    """
    self.init()

  def reload(self):
    """
    Function Name : reload
    Description   : Function to reload the feature derivation rules from database.
                  This would be used when new feature derivation rule added to database.
    Input         : none
    Output        : none
    Algoritham    : call the function self.init()
    """
    self.init()

  def init(self):
    """
    Function Name : init
    Description   : Function to load the feature derivation rules from database.
    Input         : none
    Output        : none
    Algoritham    :
      1) Get the configured database values
      2) Execute the query on table tb_feature_map to get the serivce details
      3) Store the details in self.feature_map and number of serivces in self.rowcount
    """
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.feature_map = DBPool().execute_query("select id, in_pattern, out_pattern, telco_id, channel, feature_name, remarks from tb_feature_map order by id desc", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "feature map failed to initiate. verify tb_feature_map table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("Feature map list in search order top to bottom")
    logger.info("id    in_pattern      out_pattern     telco_id        channel        feature_name	 remarks")
    logger.info("-" * 70)
    for l_row in self.feature_map:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(l_row['id'], l_row['in_pattern'], l_row['out_pattern'], l_row['telco_id'], l_row['channel'], l_row['feature_name'], l_row['remarks']))


  def get_feature_name(self, p_msisdn, p_telco_id = ".*", p_channel = ".*"):
    """
    Function Name : get_feature_name
    Description   : Function to derive feature name 
    Input         :   
        p_msisdn    - Mobile Number 
        p_telco_id  - Telco Id
        p_channel   - Channel 
    Output        : 
        Feature Identification flag - True on success or False on un identified feature 
        Feature name    - Feature name on success or None on un identified feature                 
        Mobile number - Mobile number in feature specific pattren or None on un identified feature
    Algoritham    :
      1) Loop through all the feature derivation rules
      2) Validate the input Mobile number , Telco Id and Channel against each rule
      3) On successful validation get the feature name and feature specific pattern mobile number 
      4) Return True, Feature name and feature specific pattern mobile number 
      5) If loop is completed without deriving the feature then return False, None , None
    """
    logger.debug("params - p_msisdn {0}, p_telco_id {1}, p_channel {2}".format(p_msisdn, p_telco_id, p_channel))
    for l_row in self.feature_map:
      if( (None != re.match(l_row['in_pattern'], p_msisdn)) and (None != re.match(l_row['telco_id'], p_telco_id)) and (None != re.match(l_row['channel'], p_channel))  ):
        l_feature_name = l_row['feature_name']
        l_out_num = re.sub(l_row['in_pattern'], l_row['out_pattern'], p_msisdn)
        logger.info("Matchfound. p_msisdn = {0}, l_feature_name = {1}, id = {2}, in_pattern = {3}, out_pattern = {4}, telco_id = {5}, channel = {6}, p_telco_id = {7}. p_channel = {8}l_out_num = {9}".format(p_msisdn, l_feature_name, l_row['id'], l_row['in_pattern'], l_row['out_pattern'], l_row['telco_id'], l_row['channel'], p_telco_id, p_channel, l_out_num) )
        return True, l_feature_name, l_out_num
    #End of for loop. No match found. So return False
    logger.error("No feature found for p_msisdn = {0}, p_telco_id = {1}, p_channel = {2}".format(p_msisdn, p_telco_id, p_channel) )
    return False, None, None


@singleton
class UVFeatureProfile(object):
  """ Class to derive the feature profile properties For Ex :  MAX_POST_DURATION , MAX_CALL_DURATION """
  def __init__(self):
    """
    Constructor for the class UVFeatureProfile. It calls self.init() method which loads the feature profile properties from database.
    """
    self.init()

  def reload(self):
    """
    Function Name : reload
    Description   : Function to reload the feature profile properties from database.
                    This would be used when new feature  profile property added to database.
    Input         : none
    Output        : none
    Algoritham    : call the function self.init()
    """
    self.init()

  def init(self):
    """
    Function Name : init
    Description   : Function to load the feature profile properties from database.
    Input         : none
    Output        : none
    Algoritham    :
      1) Get the configured database values
      2) Execute the query on table tb_feature_profile to get the serivce details
      3) Store the details in self.srvc_profiles and number of serivce properties in self.rowcount
    """
    self.db_name = UVConfig().get_config_value("database","db_name.core")    
    l_res, self.rowcount, self.srvc_profiles = DBPool().execute_query("select id, feature_name, profile_key, profile_value, remarks from tb_feature_profile order by id", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "feature profile failed to initiate. verify tb_feature_profile table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("{0} Feature profiles found".format(self.rowcount)) 
    logger.info("id    feature_name      profile_key     profile_value     remarks")
    logger.info("-" * 70)
    for l_row in self.srvc_profiles:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}".format(l_row['id'], l_row['feature_name'], l_row['profile_key'], l_row['profile_value'], l_row['remarks']))

  def get_profile_value(self, p_feature_name, p_profile_key):
    """
    Function Name : get_profile_value
    Description   : Function to derive feature name
    Input         :
        p_feature_name  - Feature name 
        p_telco_id    - Telco Id
        p_profile_key - Profile Key
    Output        :
        Profile property identification flag - True on success or False if un identified 
        Profile property value  - Profile property value on success or None if un identified 
    Algoritham    :
      1) Loop through all the profile property configured values
      2) Validate the input Feature name , Telco Id and Profile Key against each row
      3) On successful validation get the Profile property value
      4) Return True and Profile property value
      5) If loop is completed without finding the profile key then return False, Emptry value 
    """
    logger.debug("params - p_feature_name {0}, p_profile_key {1}".format(p_feature_name, p_profile_key))
    for l_row in self.srvc_profiles:
      if( (None != re.match(l_row['feature_name'], p_feature_name)) and (p_profile_key == l_row['profile_key']) ):
        l_profile_val = l_row['profile_value']
        logger.info("Feature profile value for p_feature_name {0}, p_profile_key {1} = {2}".format(p_feature_name, p_profile_key, l_profile_val))
        return True, l_profile_val
    logger.error("No feature profile value found for p_feature_name {0}, p_profile_key {1}".format(p_feature_name, p_profile_key))
    return False, ""



#Run unit tests
if __name__ == "__main__":
  conf = UVConfig()
  conf.init("/home/uvadmin/ucp/conf/ucp.conf")

  l_features = UVFeatures()
  print("feature & groupname - {0}".format(l_features.get_feature_group('vt_post')))

  l_feature_map = UVFeatureMap()
  print("feature_name - {0}".format(l_feature_map.get_feature_name("*9886161856", p_telco_id = "91.*")))

  l_feature_profiles = UVFeatureProfile()
  print("feature profile value - {0}".format(l_feature_profiles.get_profile_value('vt_post', 'MAX_RECORD_DURATION')))
  print("feature profile value - {0}".format(l_feature_profiles.get_profile_value('.*', 'MAX_POST_DURATION')))

