from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

@singleton
class UVAudioPrompts:
  def __init__(self):
    self.init()
  def reload():
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.prompts = DBPool().execute_query("select id, telco_id, prompt_name, file_name, dtmf_abort, silence, rep_count, action, remarks from tb_audio_prompts order by id", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "audio prompts failed to initiate. verify tb_audio_prompts table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("id     telco_id    prompt_name	file_name	 dtmf_abort	silence		rep_count      action 	remarks")
    logger.info("-" * 70)
    for l_row in self.prompts:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(l_row['id'], l_row['telco_id'], l_row['prompt_name'], l_row['file_name'], l_row['dtmf_abort'], l_row['silence'], l_row['rep_count'], l_row['action'], l_row['remarks']))
    
  def get_file_name(self, p_prompt_name, p_telco_id = ".*" ):
    if(p_telco_id == None):
      p_telco_id = ".*"

    for l_row in self.prompts:
      if( l_row['prompt_name'] == p_prompt_name and (None != re.match(l_row['telco_id'], p_telco_id)) ):
        logger.debug("Match found in tb_audio_prompts for the prompt = {0}, telco_id = {1}. id = {2}, file_name = {3}, dtmf_abort = {4} silence = {5} rep_count = {6} action = {7}".format(p_prompt_name, p_telco_id, l_row['id'], l_row['file_name'], l_row['dtmf_abort'], l_row['silence'], l_row['rep_count'], l_row['action']))
        return True, l_row['file_name'], l_row['dtmf_abort'], l_row['silence'], l_row['rep_count'], l_row['action']

    logger.error("No prompt entry found in tb_audio_prompts for the prompt = {0}, telco_id = {1}".format(p_prompt_name, p_telco_id))
    return False, None, None, None, None, None

  def get_prompt_action(self, p_prompt_name, p_telco_id = ".*" ):
    l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action  = self.get_file_name(p_prompt_name, p_telco_id) 
    return l_action
  
#Run unit tests
if __name__ == "__main__":
  init_logging("voiceapp.log")
  conf = UVConfig()
  conf.init("/home/rup/ucp/conf/ucp.conf")

  l_prompts = UVAudioPrompts()
  l_prompts.get_file_name("welcome")
  l_prompts.get_file_name("welcome", "91.BH")
  l_prompts.get_file_name("thankyou", "91.BH")
  l_prompts.get_file_name("THANKYOU", "91.BH")
  l_prompts.get_file_name("")
  l_prompts.get_file_name("welcome", None)

