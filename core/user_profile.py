import time
import re

from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
from relations import UVRelations

logger = logging.getLogger('ucp_core')

class UVUserProfile:
  def __init__(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")

  def create_tweeter_profile(self, msisdn, lang, telco_id, user_name, user_type = "community", state = "active", channel = "ivr", notify_pref = "sms"):
    if ( self.create_profile(msisdn, lang, telco_id, user_name, user_type, state, channel, notify_pref) ):
      if( UVRelations().create_relation(msisdn, "vt", relation="tweet", state=state, channel=channel) ):
        logger.info("tweeter {0} profile created".format(msisdn))
        return True
    logger.error("failed to create tweeter {0} profile".format(msisdn))
    return False

  def create_follower_profile(self, msisdn, lang, telco_id, user_name, tweeter, user_type = "community", state = "active", channel = "ivr", notify_pref = "sms"):
    if ( self.create_profile(msisdn, lang, telco_id, user_name, user_type, state, channel, notify_pref) ):
      if( UVRelations().create_relation(msisdn, tweeter, relation="follow", state=state, channel=channel) ):
        logger.info("follower {0} profile created".format(msisdn))
        return True
    logger.error("failed to create follower {0} profile".format(msisdn))
    return False

  def create_profile(self, msisdn, lang, telco_id, user_name, user_type = "community", state = "active", channel = "ivr", notify_pref = "sms"):
    logger.debug("params msisdn {0}, lang {1} telco_id {2}, user_name {3}, user_type {4}, state = {5}, channel {6}, notify_pref {7}".format(msisdn, lang, telco_id, user_name, user_type, state, channel, notify_pref))
    l_res, _, _ = DBPool().execute_query("insert into tb_user_profile(msisdn, lang, telco_id, user_name, user_type, state, channel, notify_pref, created_ts) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', now())".format(msisdn, lang, telco_id, user_name, user_type, state, channel, notify_pref), self.db_name)
    if(l_res):
      logger.info("user profile created for {0} - telco_id {1}, user_name {2}, user_type {3}, channel {4}, notify_pref {5}".format(msisdn, lang, telco_id, user_name, user_type, channel, notify_pref))
      return True
    else:
      logger.error("failed to create user profile for 0} - telco_id {1}, user_name {2}, user_type {3}, channel {4}, notify_pref {5}".format(msisdn, lang, telco_id, user_name, user_type, channel, notify_pref))
      return False

  #TODO Improve efficiency while returning profile data
  #     check in cache if profile exists
  def get_profile(self, p_msisdn):
    logger.debug("param p_msisdn {0}".format(p_msisdn))
    l_res, l_rc, l_profile = DBPool().execute_query("select msisdn,lang, telco_id, state, user_type, created_ts, updated_ts, privacy, user_name, blog_box_size, new_inbox_size, heard_inbox_size, save_inbox_size, fwd_inbox_size, blog_box_ttl, new_inbox_ttl, heard_inbox_ttl, save_inbox_ttl, fwd_inbox_ttl, notify_pref, email, display_name, password, location, channel, device_id, user_desc, profile_url, intro_audio_url, image_url, current_location, facebook_id, facebook_username, facebook_screenname, twitter_username, facebook_token, twitter_id, twitter_token, twitter_token_secret, twitter_screenname, block_list from tb_user_profile where msisdn = '{0}'".format(p_msisdn), self.db_name)
    if(l_res and l_rc == 1):
      logger.info("User profile found l_found for {0}. profile {1}".format(p_msisdn, l_profile))
      return True, l_profile
    else:
      logger.info("User profile not found l_found for {0}".format(p_msisdn))
      return False, None

  def get_profile_by_user_name(self, user_name):
    logger.debug("param user_name {0}".format(user_name))
    l_res, l_rc, l_profile = DBPool().execute_query("select msisdn,lang, telco_id, state, user_type, created_ts, updated_ts, privacy, user_name, blog_box_size, new_inbox_size, heard_inbox_size, save_inbox_size, fwd_inbox_size, blog_box_ttl, new_inbox_ttl, heard_inbox_ttl, save_inbox_ttl, fwd_inbox_ttl, notify_pref, email, display_name, password, location, channel, device_id, user_desc, profile_url, intro_audio_url, image_url, current_location, facebook_id, facebook_username, facebook_screenname, twitter_username, facebook_token, twitter_id, twitter_token, twitter_token_secret, twitter_screenname, block_list from tb_user_profile where user_name = '{0}'".format(user_name), self.db_name)
    if(l_res and l_rc == 1):
      logger.info("User profile found for {0}. profile {1}".format(user_name, l_profile))
      return True, l_profile
    else:
      logger.info("User profile not found for {0}".format(user_name))
      return False, None

  #API update user profile parameters
  #TODO Try supporting multi key values to gain performance 
  def set(self, msisdn, key, value):
    logger.debug("param msisdn {0}, key {1}, value {2}".format(msisdn, key, value))
    l_query = "update tb_user_profile set {0} = '{1}' where msisdn = '{2}'".format(key, value, msisdn)
    l_res, l_rc, l_tmp = DBPool().execute_query(l_query, self.db_name)
    if(l_res):
      logger.info("{0} User's {1} set to {2}".format(msisdn, key, value))
    else:
      logger.error("Failed to set {0} user's {1} to {2}. query [{3}]".format(msisdn, key, value, l_query))
    return l_res

  def get(self, msisdn, key):
    logger.debug("param msisdn {0}, key {1}".format(msisdn, key))
    l_found, l_profile = self.get_profile(msisdn)
    if(l_found):
      try:
        l_val = l_profile[0][key]
      except KeyError, IndexError:
        logger.exception("msisdn {0} prokey key {1} is incorrect. Please check tb_user_profile table".format(msisdn, key))
        return False, None
      else:
        return l_found, l_val
    else:
      return l_found, None

  def create_premium_tweeter_profile(self, msisdn, lang, telco_id, user_name, display_name, user_type = "premium", state = "active", channel = "cli", notify_pref = "sms"):
    logger.debug("param msisdn {0}, lang {1}, telco_id {2}, user_name {3}, display_name {4}, user_type {5}, state {6}, channel {7}, notify_pref {8}".format(msisdn, lang, telco_id, user_name, display_name, user_type, state, channel, notify_pref))
    if ( self.create_profile(msisdn, lang, telco_id, user_name, user_type, state, channel, notify_pref) ):
      if( self.set(msisdn, "display_name", display_name) ):
        if( UVRelations().create_relation(msisdn, "vt", relation="tweet", state=state, channel=channel) ):
          logger.info("tweeter {0} profile and relation to vt created".format(msisdn))
          return True
        else:
          logger.error("user {0} profile created, display_name {1} set. but failed to create relation to vt".format(msisdn, display_name))
      else:
        logger.error("user {0} profile created but failed to update displayname {1}".format(msisdn, display_name))
    else:
      logger.error("failed to create user {0} profile".format(msisdn))
    return False

#Run unit tests
if __name__ == "__main__":
  init_logging("voiceapp.log")
  conf = UVConfig()
  conf.init("/root/ucp/ucp/conf/ucp.conf")

  l_user_profile = UVUserProfile()
  #l_user_profile.create_profile("919011223344", "arabic", "91.BH", "govi") 
  #l_user_profile.create_profile("919011226677", "hin", "91.BH", "ammar", "celeb", "cli") 

  l_found, l_profile = l_user_profile.get_profile("919011223345") 
  if(True == l_found):
    logger.info("Profile found for l_profile {0}".format(l_profile[0]['msisdn']))
  else:
    logger.info("Profile not found. Creating now")
    l_user_profile.create_profile("919011223345", "arabic", "91.BH", "govi5") 

