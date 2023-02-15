#import python standard libraries

#import third patry libraries
from fysom import Fysom

#import CUP libraries
from genutils import *
from cache_server import UVCache
from config import UVConfig
from number_normalize import UVNormalizer
from number_telco_resolution import UVNumberTelcoResolution
from service_finder import *
from user_profile import UVUserProfileHandler
from telco_profile import UVTelcoProfile
from cdr import CDR
from stats_recorder import UVStatsServer
from audio_prompts import UVAudioPrompts

import vt_allin1_fsm_states
#import vt_post_fsm_states
#import vt_listen_fsm_states
#import vt_follow_fsm_states
#import vt_disc_fsm_states

def onidle(e):
  logging.info("event: {0}, from: {1}, to:{2}".format(e.event, e.src, e.dst))  
 
def onvalidate_incall(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  logging.info("raw_src: {0}, raw_dst: {1}".format(e.raw_src_num, e.raw_dst_num))  
  #normalize, find telco id for src & dst, update stats
  l_src_norm_status, l_src_norm_num = UVNormalizer().normalize(e.raw_src_num)
  l_dst_norm_status, l_dst_norm_num = UVNormalizer().normalize(e.raw_dst_num)
  
  #Store data in redis  
  UVCache().hset(e.uuid, "raw_src", e.raw_src_num)
  UVCache().hset(e.uuid, "raw_dst", e.raw_dst_num)
  UVCache().hset(e.uuid, "norm_src", l_src_norm_num)
  UVCache().hset(e.uuid, "norm_dst", l_dst_norm_num)
  UVCache().hset(e.uuid, "channel","ivr")

  #Update stats
  UVStatsServer().update_stats_on_newcall()

  l_src_telcoid_found, l_src_telcoId, l_src_flags = UVNumberTelcoResolution().get_telco_id(l_src_norm_num) 
  if(False == l_src_telcoid_found):
    logging.critical("telco id not found for src msisdn {0}.".format(l_src_norm_num))
    #fire invalid_srcnum event
    e.fsm.invalid_srcnum(uuid=e.uuid, call_instance = e.call_instance)
  else:
    UVCache().hset(e.uuid, "src_telcoid", l_src_telcoId)
    #Fetch user profile if exists. Create if not exists
    l_profile_found, l_profile = UVUserProfileHandler().get_profile(l_src_norm_num)
    if(False == l_profile_found):
      #fire incall_src_prof_notfound event
      e.fsm.incall_src_prof_notfound(uuid=e.uuid, src_num = l_src_norm_num, src_telcoId = l_src_telcoId, call_instance = e.call_instance)
    else:
      #fire src_prof_found event
      e.fsm.src_prof_found(uuid=e.uuid, src_num = l_src_norm_num, src_telcoId = l_profile[0]['telco_id'], lang = l_profile[0]['lang'], call_instance = e.call_instance)
      UVCache().hset(e.uuid, "lang", l_profile[0]['lang'])
    
    
def oninvalidsrc_playing_welcome(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'welcome'
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('welcome')
  l_lang = UVConfig().get_config_value("core","default_lang")
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"

  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)

def onplaying_invalidsrc(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'invalidsrc'
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('invalidsrc')
  l_lang = UVConfig().get_config_value("core","default_lang")
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"

  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)


def onsrc_profile_creation(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  l_lang = UVTelcoProfile().get_lang(e.src_telcoId)[1]
  UVCache().hset(e.uuid, "lang", l_lang)
  UVUserProfileHandler().create_profile(e.src_num, l_lang, e.src_telcoId, e.src_num)
  UVStatsServer().update_stats_on_newuser(e.src_telcoId, "ivr")
  e.fsm.src_prof_created(uuid=e.uuid, src_telcoId = e.src_telcoId, lang = l_lang, call_instance = e.call_instance)

def onplaying_welcome(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'welcome'
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('welcome', e.src_telcoId)
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+e.lang+"/"+l_filename+".wav"
  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)

def onplaying_thankyou(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'thankyou'
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('thankyou', UVCache().hget(e.uuid, "src_telcoid"))
  l_lang = UVConfig().get_config_value("core","default_lang")
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"

  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)

def onreleasecall(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  #Update stats
  UVStatsServer().update_stats_on_callrelease()
  e.call_instance.hangup()

def onnew_user_playing_welcome(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'welcome'
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('welcome', e.src_telcoId)
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+e.lang+"/"+l_filename+".wav"
  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)

def onnew_user_playing_langselect(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'langselect'
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action  = UVAudioPrompts().get_file_name('langselect', UVCache().hget(e.uuid, "src_telcoid"))
  l_found, l_invalid_filename, l_na_d, l_na_s, l_na_r, l_na_a  = UVAudioPrompts().get_file_name('langselect_invalid_option', UVCache().hget(e.uuid, "src_telcoid"))

  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+UVCache().hget(e.uuid, "lang")+"/"+l_filename+".wav"
  l_invalid_file_abspath = l_prompt_path+"/"+UVCache().hget(e.uuid, "lang")+"/"+l_invalid_filename+".wav"

  #refer http://wiki.freeswitch.org/wiki/Misc._Dialplan_Tools_play_and_get_digits
  l_data = "1 1 "+str(l_rep_count)+" "+str(l_silence)+" #"+" "+l_abs_file_path+ " "+l_invalid_file_abspath+" user_dtmf ["+ str(l_dtmf_abort) +"]"
  #l_data = "1 1 "+str(l_rep_count)+" "+str(l_silence)+" "+l_dtmf_abort+" "+l_abs_file_path+ " "+l_invalid_file_abspath+" user_dtmf \\\\\\d"
  #e.call_instance.playback(l_abs_file_path, l_dtmf_abort)
  logging.info("uuid: {0}, language selection play_and_get_digits data {1}".format(e.uuid, l_data));
  e.call_instance.execute("play_and_get_digits", l_data)

def onplaycomplete_langselect(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  logging.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action  = UVAudioPrompts().get_file_name('langselect', UVCache().hget(e.uuid, "src_telcoid"))
  l_lang = UVCache().hget(e.uuid, "lang")
  if(e.reason == 'digit_abort'):
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_lang = l_opt.split('=')[1]

  UVCache().hset(e.uuid, "lang", l_lang)
  #update users language
  l_profile_updated  = UVUserProfileHandler().set_user_lang(UVCache().hget(e.uuid, "norm_src"), l_lang)



def onplaying_langset(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'langset'
  l_lang = UVCache().hget(e.uuid, "lang")
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('langset', UVCache().hget(e.uuid, "src_telcoid"))
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"
  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)


def onfinding_service(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  l_found, l_service_id, l_out_num = UVServiceMap().get_service_id(UVCache().hget(e.uuid, "norm_dst"), UVCache().hget(e.uuid, "src_telcoid"))
  if(True == l_found):
    UVCache().hset(e.uuid, "service_id", l_service_id)
    UVCache().hset(e.uuid, "dst_srvc_num", l_out_num)
    l_states = l_service_id + "_fsm_states.states"
    e.call_instance.current_fsm = Fysom(eval(l_states))
    e.call_instance.current_fsm.start_allin1_tweet(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.playing_service_notfound(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_service_notfound(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  e.call_instance.curr_prompt_name = 'invalidservice'
  l_lang = UVCache().hget(e.uuid, "lang")
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name('invalidservice', UVCache().hget(e.uuid, "src_telcoid"))
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"
  e.call_instance.playback(l_abs_file_path, l_dtmf_abort)

