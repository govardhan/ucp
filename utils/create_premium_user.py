
#Setup application home path
import sys, os, shutil, os.path
import uuid
import logging
import getopt

try:
  UCPHOME=os.environ['UCPHOME']
except:
  UCPHOME="/home/uvadmin/ucp/"
  print "UCPHOME set to /home/uvadmin/ucp/"
sys.path.append(UCPHOME+"core")

from config import UVConfig
from number_normalize import UVNormalizer,UVDeNormalizer
from feature_profile import *
from user_profile import UVUserProfile
from telco_profile import UVTelcoProfile
from content_provider import UVContentProvider


#Setup application logging
logging.config.fileConfig(UCPHOME+'conf/utils_logging.conf')
logger = logging.getLogger('ucp_utils')


class CreatePremiumUser(object):
  
  def usage(self):
    logger.error("usage")
    logger.error("{0} -h".format(__file__))
    logger.error("{0} -u <user name> -d <display_name> -s <short code> -i <intro> -v <voice name> -c <cp name> -m <phone num without country code>".format(__file__))
    logger.error("{0} --user_name <user name> --display_name <display name> --short_code <short code> --intro <intro> --voice_name <voice name> --cp_name <cp name> --msisdn <phonenum without country code>".format(__file__))

  def init(self, argv):
    self.uid=uuid.uuid4()
    UVConfig().init(UCPHOME+"/conf/ucp.conf")
    self.prompt_path = UVConfig().get_config_value("core","prompts_path")
    if(False == os.path.exists(self.prompt_path)):
      logger.error("{0} prompt path {1} doesnt exists. Aborting. Internal configuration problem. Please contact platform admin".format(self.uid, self.prompt_path))
      sys.exit(2)

    self.telco_id = UVConfig().get_config_value("core","default_telco_id")
    l_lang_found, self.lang = UVTelcoProfile().get(self.telco_id, "lang")
    if(False == l_lang_found):
      logger.error("{0} language setting not found for the telco id {1}. Aborting. Internal configuration problem. Please contact platform admin".format(self.uid, self.telco_id))
      sys.exit(2)
    self.country_code = self.telco_id.split('.')[0]

    self.msisdn=""
    self.user_name=""
    self.display_name=""
    self.short_code=""
    self.intro=""
    self.voice_name=""
    self.cp_name=""

    try:
      #TODO use argparse if python we use python 2.7
      opts, args = getopt.getopt(argv,"hm:u:d:s:i:v:c:",["msisdn=","user_name=","display_name=","short_code=","intro=","voice_name=","cp_name="])
    except getopt.GetoptError:
      self.usage()
      sys.exit(2)

    for opt,arg in opts:
      if(opt == "-h"):
        self.usage()
        sys.exit(2)
      elif opt in ("-m", "--msisdn"):
        self.msisdn = arg
      elif opt in ("-u", "--user_name"):
        self.user_name = arg
      elif opt in ("-d", "--display_name"):
        self.display_name = arg
      elif opt in ("-s", "--short_code"):
        self.short_code = arg
      elif opt in ("-i", "--intro"):
        self.intro = arg
      elif opt in ("-v", "--voice_name"):
        self.voice_name = arg
      elif opt in ("-c", "--cp_name"):
        self.cp_name = arg
      else:
        self.usage()
        sys.exit(2)
    #parsing completed. Start validation now
    self.validate_input_data()

  def validate_input_data(self):
    #validate short_code msisdn, user_name, intro, voice files and cp_name 
    #sanity check on arguments
    if(self.user_name == "" or self.display_name == "" or self.short_code == "" or self.intro == "" or self.voice_name == "" or self.cp_name == ""):
      self.usage()
      sys.exit(2)

    #user_name validation
    l_found, l_profile = UVUserProfile().get_profile_by_user_name(self.user_name)   
    if(l_found):
      logger.error("{0} user_name {1} has taken by {2}. Aborting. Try with different user_name".format(self.uid, self.user_name, l_profile['msisdn']))
    else:
      logger.info("{0} user_name {1} validation passed".format(self.uid, self.user_name))

    #short_code validation
    l_found, l_profile = UVUserProfile().get_profile(self.short_code)   
    if(l_found):
      logger.error("{0} short_code {1} has taken by {2}. Aborting. Try with different short code".format(self.uid, self.short_code, l_profile['user_name']))
    else:
      logger.info("{0} short_code {1} validation passed".format(self.uid, self.short_code))

    #intro & voice name file validation
    #TODO check wave file format
    if(not os.path.exists(self.intro)):
      logger.error("{0} premium user intro file {1} doesn't exists. Aborting please check the file path".format(self.uid, self.intro))
      sys.exit(2)

    if(not os.path.exists(self.voice_name)):
      logger.error("{0} premium user voice name file {1} doesn't exists. Aborting please check the file path".format(self.uid, self.voice_name))
      sys.exit(2)

    #check cpname
    l_cp = UVContentProvider().get_cp_name(self.user_name)
    if(l_cp == True):
      logger.error("{0} premium user {1} already mapped to cp_name {2}. Aborting please contact platform administrator".format(self.uid, self.user_name, l_cp))
      sys.exit(2)

    #msisdn validation
    if(self.msisdn != ""):
      l_found = UVNormalizer().is_pattern_exists(self.msisdn, "in")
      if(l_found):
        logger.error("{0} msisdn {1} entry found in normalizer rules. Aborting. Please contact platform administrator".format(self.uid, self.msisdn))
        sys.exit(2)
      l_found = UVDeNormalizer().is_pattern_exists(self.msisdn, "out")
      if(l_found):
        logger.error("{0} msisdn {1} entry found in de-normalizer rules. Aborting. Please contact platform administrator".format(self.uid, self.msisdn))
        sys.exit(2)
      
      logger.info("{0} msisdn {1} mapped to short_code {2}".format(self.uid, self.msisdn, self.short_code))
    else:
      logger.info("{0} msisdn not configured for premium user {1}".format(self.uid, self.user_name))
    
    logger.info("{0} parameter validation completed".format(self.uid))
    return True
      

  def execute(self):
    #create user profile
    l_created = UVUserProfile().create_premium_tweeter_profile(self.short_code, self.lang, self.telco_id, self.user_name, self.display_name)
    if(l_created == True):
      logger.info("{0} premium user {1} added to user profile".format(self.uid, self.user_name))
    else:
      logger.error("{0} failed to add premium user {1} to user profiles. Internal configuration problem. Aborting. Please contact platform administrator".format(self.uid, self.user_name))
      sys.exit(2)
    #add rules in normalizer & de-normalizer
    l_added = UVDeNormalizer().add("^"+self.short_code+"$", self.country_code+self.msisdn)
    if(l_added == False):
      logger.errorr("{0} failed to add premium user msisdn {1} to number normalizerde-normalizer tables. Aborring. Please contact platform administrator".format(self.uid, self.msisdn))
      sys.exit(2)

    l_added = UVNormalizer().add(self.country_code+self.msisdn, self.short_code)
    if(l_added == False):
      logger.errorr("{0} failed to add premium user msisdn {1} to number normalizerde-normalizer tables. Aborring. Please contact platform administrator".format(self.uid, self.msisdn))
      sys.exit(2)

    l_added = UVNormalizer().add(self.msisdn, self.short_code)
    if(l_added == False):
      logger.errorr("{0} failed to add premium user msisdn {1} to number normalizerde-normalizer tables. Aborring. Please contact platform administrator".format(self.uid, self.msisdn))
      sys.exit(2)

    l_added = UVNormalizer().add("0"+self.msisdn, self.short_code)
    if(l_added == False):
      logger.errorr("{0} failed to add premium user msisdn {1} to number normalizerde-normalizer tables. Aborring. Please contact platform administrator".format(self.uid, self.msisdn))
      sys.exit(2)
    logger.info("{0} premium user msisdn {1} added to number normalizerde-normalizer tables".format(self.uid, self.msisdn))
    
    #copy intro & voice files
    l_intro = self.prompt_path+"/intro_"+self.user_name+".wav"
    l_vname = self.prompt_path+"/name_"+self.user_name+".wav"
    shutil.copy2(self.intro, l_intro)
    shutil.copy2(self.voice_name, l_vname)

    logger.info("{0} intro file {1} voice name file {2} have been copied to {3}".format(self.uid, l_intro, l_vname, self.prompt_path))
   
    #add entry in content provider
    l_added = UVContentProvider().add(self.cp_name, self.user_name)
    if(l_added == False):
      logger.errorr("{0} failed to map premium premium user {1} cp_name {2} Aborring. Please contact platform administrator".format(self.uid, self.user_name, self.cp_name))
      sys.exit(2)
    logger.info("{0} service {1}, cp_name {2} mapped".format(self.uid, self.user_name, self.cp_name))
    logger.info("{0} premium user {1} created successfully".format(self.uid, self.user_name, self.cp_name))

#msisdn, lang, telco_id, user_name, user_type = "premium", status = "active", channel = "cli", notify_pref = "sms", display_name
#msisdn, lang, telco_id, user_name, display_name, short_code, ++intro, ++voice_name, ++cp_name, 
if __name__ == "__main__":
  l_user = CreatePremiumUser()
  l_user.init(sys.argv[1:])
  l_user.execute()
