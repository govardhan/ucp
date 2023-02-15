# -*- coding: utf-8 -*-
#import python standard libraries

#import third patry libraries
from fysom import Fysom

#import CUP libraries
from genutils import *
from vt_utils import *
from cache_server import UVCache
from config import UVConfig
from number_normalize import UVNormalizer
from number_telco_resolution import UVNumberTelcoResolution
from feature_profile import *
from user_profile import UVUserProfile
from telco_profile import UVTelcoProfile
from cdr import CDR
from stats_recorder import UVStatsServer
from audio_prompts import UVAudioPrompts

import vt_allin1_fsm_states
import vt_post_fsm_states
import vt_listen_fsm_states
import vt_follow_fsm_states
#import vt_disc_fsm_states

logger = logging.getLogger('vt_app')
def onidle(e):
  logger.info("event: {0}, from: {1}, to:{2}".format(e.event, e.src, e.dst))  
 
def onvalidate_incall(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  logger.info("raw_src: {0}, raw_dst: {1}".format(e.raw_src_num, e.raw_dst_num))  
  #normalize, find telco id for src & dst, update stats
  l_src_norm_status, l_src_norm_num = UVNormalizer().normalize(e.raw_src_num)
  l_dst_norm_status, l_dst_norm_num = UVNormalizer().normalize(e.raw_dst_num)
  
  #Store data in redis  
  UVCache().hset(e.uuid, "raw_src", e.raw_src_num)
  UVCache().hset(e.uuid, "raw_dst", e.raw_dst_num)
  UVCache().hset(e.uuid, "norm_src", l_src_norm_num)
  UVCache().hset(e.uuid, "norm_dst", l_dst_norm_num)
  UVCache().hset(e.uuid, "channel","ivr")
  UVCache().hset(e.uuid, "call_start_time", str(datetime.now()) )
  e.call_instance.call_start_time = datetime.now()
  #temp lang for prompts until lang resolve
  UVCache().hset(e.uuid, "lang", UVConfig().get_config_value("core", "default_lang"))


  l_src_telcoid_found, l_src_telcoId, l_src_flags = UVNumberTelcoResolution().get_telco_id(l_src_norm_num) 
  if(False == l_src_telcoid_found):
    logger.critical("telco id not found for src msisdn {0}.".format(l_src_norm_num))
    UVStatsServer().update_stats_on_newcall("unknown")
    #fire invalid_srcnum event
    e.fsm.invalid_srcnum(uuid=e.uuid, call_instance = e.call_instance)
  else:
    UVStatsServer().update_stats_on_newcall(l_src_telcoId)
    UVCache().hset(e.uuid, "src_telcoid", l_src_telcoId)
    UVCache().hset(e.uuid, "dst_telcoid", l_src_telcoId)
    #Fetch user profile if exists. Create if not exists
    l_profile_found, l_profile = UVUserProfile().get_profile(l_src_norm_num)
    if(False == l_profile_found):
      #fire incall_src_prof_notfound event
      e.fsm.incall_src_prof_notfound(uuid=e.uuid, src_num = l_src_norm_num, src_telcoId = l_src_telcoId, call_instance = e.call_instance)
    else:
      #fire src_prof_found event
      e.fsm.src_prof_found(uuid=e.uuid, src_num = l_src_norm_num, src_telcoId = l_profile[0]['telco_id'], lang = l_profile[0]['lang'], call_instance = e.call_instance)
      UVCache().hset(e.uuid, "lang", l_profile[0]['lang'])
    
    
def oninvalidsrc_playing_welcome(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "welcome", e.call_instance)


def onplaying_invalidsrc(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "invalidsrc", e.call_instance)


def onsrc_profile_creation(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  l_found, l_lang = UVTelcoProfile().get(e.src_telcoId, "lang")
  assert (l_found == True) , "language setting not found for telco_id {0}".format(e.dormant_tweeter_telcoid)   
  UVCache().hset(e.uuid, "lang", l_lang)
  UVUserProfile().create_profile(e.src_num, l_lang, e.src_telcoId, e.src_num)
  UVCache().hset(e.uuid, "newuser", 1)
  UVStatsServer().update_stats_on_newuser(e.src_telcoId, "ivr")
  e.fsm.src_prof_created(uuid=e.uuid, src_telcoId = e.src_telcoId, lang = l_lang, call_instance = e.call_instance)


def onplaying_welcome(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "welcome", e.call_instance)


def onplaying_thankyou(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "thankyou", e.call_instance)


def onreleasecall(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  

  l_src_telcoid = UVCache().hget(e.uuid, "src_telcoid")
  if(l_src_telcoid is None):
    l_src_telcoid = "unknown"
  UVStatsServer().update_stats_on_callrelease(l_src_telcoid)
  l_txn_duration = datetime.now() - e.call_instance.call_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "call","release")
  logger.info("uuid: {0} deleting call cache and hangup call".format(e.uuid))
  UVCache().delete(e.uuid)
  e.call_instance.hangup()

def onnew_user_playing_welcome(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "welcome", e.call_instance)


def onnew_user_playing_langselect(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt_and_get_digits(e.uuid, "langselect", e.call_instance)


def onplaycomplete_langselect(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_action  = UVAudioPrompts().get_prompt_action('langselect', UVCache().hget(e.uuid, "src_telcoid"))
  l_lang = UVCache().hget(e.uuid, "lang")
  if(e.reason == 'digit_abort'):
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_lang = l_opt.split('=')[1]

  UVCache().hset(e.uuid, "lang", l_lang)
  #update users language
  l_profile_updated  = UVUserProfile().set(UVCache().hget(e.uuid, "norm_src"), "lang", l_lang)


def onplaying_langset(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "langset", e.call_instance)


def onfinding_service(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  l_found, l_feature_name, l_out_num = UVFeatureMap().get_feature_name(UVCache().hget(e.uuid, "norm_dst"), UVCache().hget(e.uuid, "src_telcoid"), UVCache().hget(e.uuid, "channel"))
  if(True == l_found):
    UVCache().hset(e.uuid, "feature_name", l_feature_name)
    UVCache().hset(e.uuid, "dst_srvc_num", l_out_num)
    l_states = l_feature_name + "_fsm_states.states"
    e.call_instance.current_fsm = Fysom(eval(l_states))
    l_start_event = "start_"+l_feature_name
    getattr(e.call_instance.current_fsm, l_start_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    UVCache().hset(e.uuid, "feature_name", "unknown")
    e.fsm.service_notfound(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_invaliddialednum(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))  
  play_audio_prompt(e.uuid, "invaliddialednum", e.call_instance)

