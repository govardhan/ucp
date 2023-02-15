#import python standard libraries
from datetime import datetime

#import third patry libraries

#import UCP libraries
from genutils import *
from vt_utils import *
from content import UVContent 
from cache_server import UVCache
from relations import UVRelations

logger = logging.getLogger('vt_app')

def onplaying_vt_post_instruction(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format( e.uuid, e.event, e.src, e.dst))
  UVCache().hset(e.uuid, "txn_start_time", str(datetime.now()))
  e.call_instance.txn_start_time = datetime.now()

  l_found, l_max_rerecords = UVFeatureProfile().get_profile_value('vt_post', 'MAX_RERECORDS')
  if(l_found == False):
    logger.info("uuid: {0}, MAX_RERECORDS not defined for service vt_post. Set default value to 2".format(e.uuid))
    #TODO possibility of previous re-recorded file. Need to be deleted?

  if( UVCache().hexists(e.uuid, "newuser") and (not UVCache().hexists(e.uuid, "newtweeter"))):
    l_norm_src = UVCache().hget(e.uuid, "norm_src")
    UVRelations().create_relation(l_norm_src, "vt", relation="tweet" )
    UVCache().hset(e.uuid, "newtweeter", 1)

  if(int(UVCache().hget(e.uuid, "vt_post_rerecords") or "0") > int(l_max_rerecords)):
    logger.info("uuid: {0}, MAX_RERECORDS {1} exceeded".format(e.uuid, l_max_rerecords))
    #resetting incase if this callflow triggred from mainmenu
    UVCache().hset(e.uuid, "vt_post_rerecords",0)
    e.fsm.play_vt_post_max_retires(uuid=e.uuid, call_instance = e.call_instance)
  else:
    play_audio_prompt(e.uuid, "vt_post_instruction", e.call_instance)

def onplaying_vt_post_beep(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_post_beep", e.call_instance)

def onrecording_vt_post(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_norm_src = UVCache().hget(e.uuid, "norm_src")
  l_rec_file_path = prepare_rec_file_name(l_norm_src)
  UVCache().hset(e.uuid, "vt_post_rec_file", l_rec_file_path)
  l_found, l_max_duration = UVFeatureProfile().get_profile_value('vt_post', 'MAX_RECORD_DURATION')
  l_found, l_silence_duration = UVFeatureProfile().get_profile_value('vt_post', 'MAX_SILENCE_DURATION')
  l_found, l_dtmf_abort = UVFeatureProfile().get_profile_value('vt_post', 'RECORD_DTMF_ABORT')
  e.call_instance.curr_prompt_name = 'vt_post'
  record_audio_file(e.uuid, l_rec_file_path, l_max_duration, l_silence_duration, l_dtmf_abort, e.call_instance)
  
def onrecordcomplete_vt_post(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, rec_duration: {1}, rec_file: {2}, dtmf:{3}".format(e.uuid, e.rec_duration, e.rec_file, e.dtmf))
  UVCache().hset(e.uuid, "txn_duration", e.rec_duration)
  UVCache().hset(e.uuid, "vt_post_rec_com_dtmf", e.dtmf)
  
def onplaying_vt_post_hint(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_post_hint", e.call_instance)
  
def ontransit_state_vt_post_hint(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_act = "post"
  if(e.reason == 'digit_abort'):
    l_action  = UVAudioPrompts().get_prompt_action('vt_post_hint', UVCache().hget(e.uuid, "src_telcoid"))
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_act = l_opt.split('=')[1]
    logger.info("uuid: {0}, dtmf: {1}, action: {2}".format(e.uuid, e.dtmf, l_act))

  if(l_act == "post"):
    e.fsm.play_vt_post_tagging(uuid=e.uuid, call_instance = e.call_instance)
  elif (l_act == "cancel"):
    e.fsm.play_vt_post_cancelled(uuid=e.uuid, call_instance = e.call_instance)
  elif (l_act == "preview"):
    l_found, l_max_previews = UVFeatureProfile().get_profile_value('vt_post', 'MAX_PREVIEWS')
    if(l_found == False):
      logger.info("uuid: {0}, MAX_PREVIEWS not defined for service vt_post. Set default value to 2".format(e.uuid))

    UVCache().hincrby(e.uuid, "vt_post_previews")
    if( int( UVCache().hget(e.uuid, "vt_post_previews"))  > int(l_max_previews)):
      logger.info("uuid: {0}, MAX_PREVIEWS {1} exceeded".format(e.uuid, l_max_previews))
      #resetting incase if this callflow triggred from mainmenu
      UVCache().hset(e.uuid, "vt_post_previews",0)
      e.fsm.play_vt_post_max_retires(uuid=e.uuid, call_instance = e.call_instance)
    else:
      e.fsm.play_vt_post(uuid=e.uuid, call_instance = e.call_instance)
  else: #re-record
    UVCache().hincrby(e.uuid, "vt_post_rerecords")
    e.fsm.play_vt_post_instruction(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_post_tagging(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_post_tagging", e.call_instance)
  
def onplaying_vt_post_tagged(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_post_tagged", e.call_instance)
  
def oncompleted_vt_post(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_telco_id = UVCache().hget(e.uuid, "src_telcoid")
  l_recfile = UVCache().hget(e.uuid, "vt_post_rec_file")
  l_recduration = UVCache().hget(e.uuid, "txn_duration")
  UVContent().add_content(l_msisdn, l_telco_id, "selftweet", l_recfile, l_recduration)
  #TODO notify to all followers

  if(e.call_instance.parent_fsm):
    logging.info("{0} Transferring call back to parent callflow {1}. resume event {2}".format(e.uuid, e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event))
    l_txn_duration = datetime.now() - e.call_instance.txn_start_time
    UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
    vt_cdr_gen(e.uuid, "txn","vt_post")
    #TODO clean this statemachine object
    del e.fsm
    e.call_instance.current_fsm = e.call_instance.parent_fsm
    getattr(e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    logging.info("{0} Parent callflow not found. Proceed to release call now".format(e.uuid))
    e.fsm.play_thankyou(uuid=e.uuid, call_instance = e.call_instance)
    #TODO add call transfer to vt_disc feature

def onplaying_vt_post(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_wave_file(e.uuid, "vt_post", UVCache().hget(e.uuid, "vt_post_rec_file"), "0123456789*#", e.call_instance)
  
def onplaying_vt_post_cancelled(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  #TODO don't save audio file
  l_txn_duration = datetime.now() - e.call_instance.txn_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "txn","vt_post_cancel")
  play_audio_prompt(e.uuid, "vt_post_cancelled", e.call_instance)
  
def onplaying_vt_post_max_retires(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_post_max_retires", e.call_instance)
  
def onplaying_thankyou(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "thankyou", e.call_instance)
  
def onreleasecall(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  """
    Description : Release call handler
    Input       : statemachine event. Additional parameters will be members of event 'e' 
    Output&Algo : Write CDR, deletes redis cache, update stats and hangup the call
  """
  l_src_telcoid = UVCache().hget(e.uuid, "src_telcoid")
  UVStatsServer().update_stats_on_callrelease(l_src_telcoid)
  l_txn_duration = datetime.now() - e.call_instance.txn_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "txn","release")
  l_txn_duration = datetime.now() - e.call_instance.call_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "call","release")
  logger.info("uuid: {0} deleting call cache".format(e.uuid))
  UVCache().delete(e.uuid)
  e.call_instance.hangup()
  
def oncall_released(e):
  """
    Description : Release call confirmation handler
    Input       : statemachine event. Additional parameters will be members of event 'e' 
    Output&Algo : Check if cache still exists
  """
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  #check cache existance
