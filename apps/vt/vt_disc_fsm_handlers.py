#import python standard libraries

#import third patry libraries

#import CUP libraries
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
from vt_utils import *
from vt_disc_tweeters import VTDiscTweeters
from subscription import UVSubscription


def oninit_vt_disc_tweeters(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  UVCache().hset(e.uuid, "txn_start_time", str(datetime.now()))
  e.call_instance.txn_start_time = datetime.now()

  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_telco_id = UVCache().hget(e.uuid, "src_telcoid")
  l_tweeters = VTDiscTweeters().get(e.uuid, l_telco_id)
  e.call_instance.premium_tweeters = VTDiscTweeters().filter(l_msisdn) 

  l_found, l_wait_time = UVFeatureProfile().get_profile_value('vt_disc', 'wait_time_after_prompt')
  if(False == l_found):
    l_wait_time = 0
  else:
    l_wait_time = int(l_wait_time)
  UVCache().hset(e.uuid, "vt_disc_wait_time_after_prompt", l_wait_time)
  UVCache().hset(e.uuid, "vt_disc_dtmf", ''.join([str(i) for i in range(1,len(e.call_instance.premium_tweeters)+1)]))

  if( len(e.call_instance.premium_tweeters) == 0):
    e.fsm.play_vt_disc_no_tweeters(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_disc_intro(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_disc_intro(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_disc_intro", e.call_instance)
  UVCache().hincrby(e.uuid, "vt_disc_curr_index")

def onplaying_vt_disc_no_tweeters(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_disc_no_tweeters", e.call_instance)

def oncompleted_vt_disc(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_telco_id = UVCache().hget(e.uuid, "src_telcoid")

  if(e.call_instance.parent_fsm):
    logging.info("{0} Transferring call back to parent callflow {1}. resume event {2}".format(e.uuid, e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event))
    l_txn_duration = datetime.now() - e.call_instance.txn_start_time
    UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
    vt_cdr_gen(e.uuid, "txn","vt_disc_notweeters")
    del e.fsm
    e.call_instance.current_fsm = e.call_instance.parent_fsm
    getattr(e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    logging.info("{0} Parent callflow not found. Proceed to release call now".format(e.uuid))
    e.fsm.play_thankyou(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_disc_press_digit(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_curr_index = UVCache().hget(e.uuid, "vt_disc_curr_index")
  l_dtmf = UVCache().hget(e.uuid, "vt_disc_dtmf")
  play_audio_prompt_and_get_digits_custom_dtmf(e.uuid, "vt_disc_press_digit", "vt_disc_press_digit_"+l_curr_index, l_dtmf, e.call_instance)

def ontransit_playcomplete_vt_disc_press_digit(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  if(e.reason == 'digit_abort'):
    if( int(e.dtmf) > 0 and int(e.dtmf) <= len(e.call_instance.premium_tweeters) ):
      l_msisdn = UVCache().hget(e.uuid, "norm_src")
      l_curr_index = int(UVCache().hget(e.uuid, "vt_disc_curr_index"))
      UVSubscription().subscribe_byname(e.uuid, l_msisdn, e.call_instance.premium_tweeters[l_curr_index-1])
      e.fsm.play_vt_disc_follow_confirm_tentative(uuid=e.uuid, call_instance = e.call_instance)
    else:
      logger.debug("{0} invalid dtmf {1}".format(e.uuid, e.dtmf))
      e.fsm.play_vt_disc_tweeter(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_disc_tweeter(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_disc_tweeter(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_curr_index = int(UVCache().hget(e.uuid, "vt_disc_curr_index"))
  try:
    l_wait_time = UVCache().hget(e.uuid, "vt_disc_wait_time_after_prompt")
    l_dtmf = UVCache().hget(e.uuid, "vt_disc_dtmf")
    l_tweeter_name_file = "name_"+e.call_instance.premium_tweeters[l_curr_index-1]
    l_lang = UVCache().hget(e.uuid, "lang")
    l_prompt_path = UVConfig().get_config_value("core","prompts_path")
    l_tweeter_name_file = l_prompt_path+"/"+l_lang+"/"+l_tweeter_name_file+".wav"
    play_wave_file_get_digits(e.uuid, "vt_disc_tweeter", l_tweeter_name_file, l_dtmf, l_wait_time, e.call_instance)
  except IndexError:
    log.error("{0} invalid index {1} while selecting premium tweeter. Terminating callflow".format(e.uuid,l_curr_index-1))
    e.fsm.play_vt_disc_nomore_tweeters(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_disc_follow_confirm_tentative(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  #remove recent subscribed tweeter from list
  l_curr_index = int(UVCache().hget(e.uuid, "vt_disc_curr_index"))
  del e.call_instance.premium_tweeters[l_curr_index-1]
  UVCache().hset(e.uuid, "vt_disc_curr_index",0)
  play_audio_prompt(e.uuid, "vt_disc_follow_confirm_tentative", e.call_instance)

def ontransit_playcomplete_vt_disc_follow_confirm_tentative(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  if( len(e.call_instance.premium_tweeters) == 0):
    e.fsm.play_vt_disc_no_more_tweeters(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_disc_intro(uuid=e.uuid, call_instance = e.call_instance)


def ontransit_playcomplete_vt_disc_tweeter(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_continue = False
  l_curr_index = int(UVCache().hget(e.uuid, "vt_disc_curr_index"))
  if(e.reason == 'digit_abort'):
    if( int(e.dtmf) > 0 and int(e.dtmf) <= len(e.call_instance.premium_tweeters) ):
      l_msisdn = UVCache().hget(e.uuid, "norm_src")
      UVSubscription().subscribe_byname(e.uuid, l_msisdn, e.call_instance.premium_tweeters[l_curr_index-1])
      e.fsm.play_vt_disc_follow_confirm_tentative(uuid=e.uuid, call_instance = e.call_instance)
    else:
      logger.debug("{0} invalid dtmf {1}".format(e.uuid, e.dtmf))
      l_continue = True
  else:
    l_continue = True
  if(True == l_continue):
    if( len(e.call_instance.premium_tweeters) == l_curr_index):
      e.fsm.play_vt_disc_no_more_tweeters(uuid=e.uuid, call_instance = e.call_instance)
    else:
      UVCache().hincrby(e.uuid, "vt_disc_curr_index")
      e.fsm.play_vt_disc_press_digit(uuid=e.uuid, call_instance = e.call_instance) 

def onplaying_vt_disc_nomore_tweeters(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_disc_nomore_tweeters", e.call_instance)

def onplaying_vt_disc_try_again(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_disc_try_again", e.call_instance)

def onplaying_thankyou(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "thankyou", e.call_instance)

def onreleasecall(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
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

