#import python standard libraries
import os
from datetime import datetime

#import third patry libraries

#import UCP libraries
from genutils import *
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


logger = logging.getLogger('vt_app')
def play_wave_file(p_uuid, p_dummy_prompt_name, p_file_name, p_dtmf_abort, p_call_instance):
  logger.info("uuid: {0}, prompt: {1}, file: {2}, dtmf:{3}".format( p_uuid, p_dummy_prompt_name, p_file_name, p_dtmf_abort))
  p_call_instance.curr_prompt_name = p_dummy_prompt_name
  p_call_instance.playback(p_file_name, p_dtmf_abort)

def play_wave_file_get_digits(p_uuid, p_dummy_prompt_name, p_file_name, p_dtmf_abort, p_silence, p_call_instance):
  logger.info("uuid: {0}, prompt: {1}, file: {2}, dtmf:{3}".format( p_uuid, p_dummy_prompt_name, p_file_name, p_dtmf_abort))
  p_call_instance.curr_prompt_name = p_dummy_prompt_name
  l_lang = UVCache().hget(p_uuid, "lang")
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_invalid_file_name = l_prompt_path+"/"+l_lang+"/"+p_dummy_prompt_name+"_invalid_option.wav"
  l_data = "1 1 0 "+" "+str(p_silence)+" #"+" "+p_file_name+ " "+l_invalid_file_name+" user_dtmf ["+ p_dtmf_abort +"]"
  p_call_instance.execute("play_and_get_digits", l_data)

def play_audio_prompt(p_uuid, p_prompt_name, p_call_instance):
  p_call_instance.curr_prompt_name = p_prompt_name
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action = UVAudioPrompts().get_file_name(p_prompt_name, UVCache().hget(p_uuid, "src_telcoid"))
  l_lang = UVCache().hget(p_uuid, "lang")
  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"
  p_call_instance.playback(l_abs_file_path, l_dtmf_abort)


def play_audio_prompt_and_get_digits(p_uuid, p_prompt_name, p_call_instance):
  p_call_instance.curr_prompt_name = p_prompt_name 
  l_src_telcoid = UVCache().hget(p_uuid, "src_telcoid")
  l_lang = UVCache().hget(p_uuid, "lang")
  l_invalid_options_prompt_name = p_prompt_name + "_invalid_option"
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action  = UVAudioPrompts().get_file_name(p_prompt_name, l_src_telcoid)
  l_found, l_invalid_filename, l_na_d, l_na_s, l_na_r, l_na_a  = UVAudioPrompts().get_file_name(l_invalid_options_prompt_name, l_src_telcoid)

  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"
  l_invalid_file_abspath = l_prompt_path+"/"+l_lang+"/"+l_invalid_filename+".wav"

  #refer http://wiki.freeswitch.org/wiki/Misc._Dialplan_Tools_play_and_get_digits
  l_data = "1 1 "+str(l_rep_count)+" "+str(l_silence)+" #"+" "+l_abs_file_path+ " "+l_invalid_file_abspath+" user_dtmf ["+ str(l_dtmf_abort) +"]"
  p_call_instance.execute("play_and_get_digits", l_data)

def play_audio_prompt_and_collect_digits(p_uuid, p_prompt_name, p_call_instance):
  p_call_instance.curr_prompt_name = p_prompt_name
  l_src_telcoid = UVCache().hget(p_uuid, "src_telcoid")
  l_lang = UVCache().hget(p_uuid, "lang")
  l_invalid_options_prompt_name = p_prompt_name + "_invalid_option"
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action  = UVAudioPrompts().get_file_name(p_prompt_name, l_src_telcoid)
  l_found, l_invalid_filename, l_na_d, l_na_s, l_na_r, l_na_a  = UVAudioPrompts().get_file_name(l_invalid_options_prompt_name, l_src_telcoid)

  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"
  l_invalid_file_abspath = l_prompt_path+"/"+l_lang+"/"+l_invalid_filename+".wav"

  #refer http://wiki.freeswitch.org/wiki/Misc._Dialplan_Tools_play_and_get_digits
  l_data = "1 15 "+str(l_rep_count)+" "+str(l_silence)+" #"+" "+l_abs_file_path+ " "+l_invalid_file_abspath+" user_dtmf \\d+"
  p_call_instance.execute("play_and_get_digits", l_data)

def play_audio_prompt_and_get_digits_custom_dtmf(p_uuid, p_dummy_prompt_name, p_prompt_name, p_dtmf, p_call_instance):
  p_call_instance.curr_prompt_name = p_dummy_prompt_name
  l_src_telcoid = UVCache().hget(p_uuid, "src_telcoid")
  l_lang = UVCache().hget(p_uuid, "lang")
  l_invalid_options_prompt_name = p_dummy_prompt_name + "_invalid_option"
  l_found, l_filename, l_dtmf_abort, l_silence, l_rep_count, l_action  = UVAudioPrompts().get_file_name(p_prompt_name, l_src_telcoid)
  l_found, l_invalid_filename, l_na_d, l_na_s, l_na_r, l_na_a  = UVAudioPrompts().get_file_name(l_invalid_options_prompt_name, l_src_telcoid)

  l_prompt_path = UVConfig().get_config_value("core","prompts_path")
  l_abs_file_path = l_prompt_path+"/"+l_lang+"/"+l_filename+".wav"
  l_invalid_file_abspath = l_prompt_path+"/"+l_lang+"/"+l_invalid_filename+".wav"

  #refer http://wiki.freeswitch.org/wiki/Misc._Dialplan_Tools_play_and_get_digits
  l_data = "1 1 0 "+str(l_silence)+" #"+" "+l_abs_file_path+ " "+l_invalid_file_abspath+" user_dtmf ["+ str(p_dtmf) +"]"
  p_call_instance.execute("play_and_get_digits", l_data)


def record_audio_file(p_uuid, p_rec_file_name, p_max_duration, p_silence_duration, p_dtmf_abort, p_call_instance):
  l_rec_abort_str = "playback_terminators=" + p_dtmf_abort
  p_call_instance.set(l_rec_abort_str)
  l_rec_samp_rate="record_sample_rate=8000"
  p_call_instance.set(l_rec_samp_rate)
  l_data = p_rec_file_name + " " + str(p_max_duration) + " " + str(p_silence_duration)
  p_call_instance.execute("record", l_data)


def prepare_rec_file_name(p_key):
  l_level1_path = RSHash(p_key)%255
  l_level1_path = "%0.2X"%(int(l_level1_path))

  l_level2_path = BKDRHash(p_key)%255
  l_level2_path = "%0.2X"%(int(l_level2_path))

  l_rec_path = UVConfig().get_config_value("core","record_file_path")
  l_dir = l_rec_path + "/" + l_level1_path + "/" + l_level2_path
  if not os.path.isdir(l_dir):
    logging.info("recording directory: {0} doesn't exists. Creating now".format(l_dir))
    os.makedirs(l_dir)

  l_file_path = l_dir + "/" + p_key + "_" +  str(time.time()).replace(".", "_") + ".wav"
  return l_file_path

vt_cdrlogger = logging.getLogger('vtcdr')

def vt_cdr_gen(uuid, cdrtype, p_completion):
  """
    Write transaction/call CDR
    cdrtype = call/txn
    completion = if cdrtype is txn then values will be feature names otherwise, release or disconnect
  """
  l_norm_src = UVCache().hget(uuid, "norm_src")
  l_norm_dst = UVCache().hget(uuid, "norm_dst")
  l_raw_dst = UVCache().hget(uuid, "raw_dst")
  l_src_telcoid = UVCache().hget(uuid, "src_telcoid")
  l_dst_telcoid = UVCache().hget(uuid, "dst_telcoid")
  l_channel = UVCache().hget(uuid, "channel")
  l_feature_name = UVCache().hget(uuid, "feature_name")
  if(cdrtype == "txn"):
    l_start_time = UVCache().hget(uuid, "txn_start_time")
  else:
    l_start_time = UVCache().hget(uuid, "call_start_time")
  l_txnduration = UVCache().hget(uuid, "txn_duration")
  vt_cdrlogger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}".format( uuid, l_norm_src, l_src_telcoid, l_raw_dst, l_norm_dst, l_dst_telcoid, l_channel, l_feature_name, l_start_time, str(datetime.now()), l_txnduration, p_completion ))
  logger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}".format( uuid, l_norm_src, l_src_telcoid, l_raw_dst, l_norm_dst, l_dst_telcoid, l_channel, l_feature_name, l_start_time, str(datetime.now()), l_txnduration, p_completion ))

def oncalldisconnected(e):
  """
    Description : User disconnect call handler
    Input       : statemachine event. Additional parameters will be members of event 'e' 
    Output&Algo : Write CDR, deletes redis cache, update stats and hangup the call
  """
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, callduration: {1}".format(e.uuid, e.callduration))

  l_src_telcoid = UVCache().hget(e.uuid, "src_telcoid")
  UVStatsServer().update_stats_on_calldisconnected(l_src_telcoid)
  #TODO do we have to write txn cdr for the current feature/service
  UVCache().hset(e.uuid, "txn_duration", e.callduration)
  vt_cdr_gen(e.uuid, "call", "disconnected")
  logger.info("uuid: {0} deleting call cache".format(e.uuid))
  UVCache().delete(e.uuid)
  #TODO delete fsm here
  #del e.fsm

