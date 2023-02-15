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


def oninit_vt_settings_menu(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  UVCache().hset(e.uuid, "txn_start_time", str(datetime.now()))
  e.call_instance.txn_start_time = datetime.now()
  e.fsm.play_vt_settings_menu(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_settings_menu(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  UVCache().hincrby(e.uuid, "vt_settings_menu_visit")
  l_found, l_max_visits = UVFeatureProfile().get_profile_value('vt_settings','max_menu_visits')
  if(False == l_found):
    l_max_visits = 3
  l_visits = int( UVCache().hget(e.uuid, "vt_settings_menu_visit") )
  if(l_visits <= int(l_max_visits) ):
    play_audio_prompt_and_get_digits(e.uuid, "vt_settings_menu", e.call_instance)
  else:
    play_audio_prompt(e.uuid, "vt_settings_max_retries", e.call_instance)

def ontransit_vt_settings_menu(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_act = ""
  if(e.reason == 'digit_abort'):
    l_action  = UVAudioPrompts().get_prompt_action('vt_settings_menu', UVCache().hget(e.uuid, "src_telcoid"))
    if l_action is None:
      l_action = ""
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_act = l_opt.split('=')[1]
    logger.info("uuid: {0}, dtmf: {1}, action: {2}".format(e.uuid, e.dtmf, l_act))
  else:
    e.fsm.play_vt_settings_try_again(uuid=e.uuid, call_instance = e.call_instance)
    return

  #1=owntweet,2=name,3=privacy,4=lang
  if(l_act == "owntweet"):
    e.fsm.start_vt_setting_owntweet(uuid=e.uuid, call_instance = e.call_instance)
  elif (l_act == "name"):
    e.fsm.start_vt_setting_name(uuid=e.uuid, call_instance = e.call_instance)
  elif (l_act == "privacy"):
    e.fsm.start_vt_setting_privacy(uuid=e.uuid, call_instance = e.call_instance)
  elif (l_act == "lang"):
    e.fsm.start_vt_setting_lang(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_settings_try_again(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_settings_try_again(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_try_again", e.call_instance)


def oncompleted_vt_settings(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  if(e.call_instance.parent_fsm):
    logger.info("{0} Transferring call back to parent callflow {1}. resume event {2}".format(e.uuid, e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event))
    l_txn_duration = datetime.now() - e.call_instance.txn_start_time
    UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
    vt_cdr_gen(e.uuid, "txn", "vt_settings")
    del e.fsm
    e.call_instance.current_fsm = e.call_instance.parent_fsm
    getattr(e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    logger.info("{0} Parent callflow not found. Proceed to release call now".format(e.uuid))
    e.fsm.play_thankyou(uuid=e.uuid, call_instance = e.call_instance)


def oninit_vt_settings_owntweet(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src") 
  l_count, e.call_instance.owntweets = UVContent().get_content(l_msisdn, "selftweet") 
  if(0 == l_count):
    e.fsm.play_vt_setting_owntweet_notweets(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_setting_owntweet_menu(uuid=e.uuid, call_instance = e.call_instance)
    
def onplaying_vt_settings_owntweet_intro(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_settings_owntweet_menu", e.call_instance)

def onplaying_vt_settings_owntweet_notweets(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  #TODO try transferring call to vt_post
  play_audio_prompt(e.uuid, "vt_settings_owntweet_notweets", e.call_instance)

def onplaying_vt_settings_owntweet(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  if(e.src != "playing_vt_settings_owntweet_intro"):
    del e.call_instance.owntweets[0]
  if(len(e.call_instance.owntweets) > 0):
    l_found, l_dtmf = UVFeatureProfile().get_profile_value('vt_settings', 'owntweet_option_dtmf')
    if(False == l_found):
      logger.error("uuid: {0} feature profile key vt_settings:owntweet_options not found. use default value 123")
      l_dtmf = "123"
    l_found, l_silence = UVFeatureProfile().get_profile_value('vt_settings', 'wait_time_after_playing_owntweet')
    if(False == l_found):
      logger.error("uuid: {0} feature profile key vt_settings:wait_time_after_playing_owntweet not found. use default value 2000")
      l_silence = "2000"
    play_wave_file_get_digits(e.uuid, "vt_settings_owntweet", e.call_instance.owntweets[0]['content'], l_dtmf, l_silence, e.call_instance)
    l_msisdn = UVCache().hget(e.uuid, "norm_src")
    UVContentActivity().onread(e.uuid, l_msisdn, e.call_instance.tweets[0])
  else:
    e.fsm.play_vt_settings_owntweet_nomore(uuid=e.uuid, call_instance = e.call_instance)


def ontransit_playcomplete_vt_settings_owntweet(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  if(e.reason == 'digit_abort'):
    l_found, l_action = UVFeatureProfile().get_profile_value('vt_settings', 'owntweet_option_dtmf_action')
    if(False == l_found):
      logger.error("{0} feature profile key vt_settings:owntweet_option_dtmf_action not found. fallback to no option mode".format(e.uuid))
      e.fsm.play_vt_settings_owntweet(uuid=e.uuid, call_instance = e.call_instance)
    else:
      l_act = ""
      for l_opt in l_action.split(','):
        if(l_opt.split('=')[0] == e.dtmf):
          l_act = l_opt.split('=')[1]
      logger.info("uuid: {0}, dtmf: {1}, action: {2}".format(e.uuid, e.dtmf, l_act))
      l_event = l_act+"_vt_settings_owntweet"
      try:
        getattr(e.fsm, l_event)(uuid=e.uuid, call_instance = e.call_instance)
      except:
        logger.error("{0} action {1} not being implemented. please check vt_settings:owntweet_option_dtmf_action in feature profile. fallback to no option mode".format(e.uuid, l_act))
        e.fsm.play_vt_settings_owntweet(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_listen_tweet(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_settings_owntweet_nomore(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_owntweet_notweets_nomore", e.call_instance)


def onvt_settings_owntweet_sharing(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_found, l_howmany = UVFeatureProfile().get_profile_value('vt_settings', 'owntweet_share_count')
  if(False == l_found):
    logger.error("uuid: {0} feature profile key vt_settings:owntweet_share_count not found. use default value 10".format(e.uuid))
    l_howmany = "10"
  l_msisdn = UVCache().hget(e.uuid, "norm_src") 
  l_count, l_f_list = UVRelations().get_non_direct(l_msisdn, "follow", l_howmany)
  if(l_count > 0):
    for l_f in l_f_list:
      l_t_found, l_telco_id, _ = UVNumberTelcoResolution().get_telco_id(l_f)
      if(True == l_t_found):
        UVContent().add_content(l_f, l_telco_id, "share", e.call_instance.owntweets[0]['content'], e.call_instance.owntweets[0]['length'], "1",e.call_instance.tweets[0]['content_id'])
        #send sms notifications
        #[ UVSMSServer().send_sms(l_f, ) for l_f in l_f_list ]
  else: #if no users found to share
    logger.info("{0} No users found to share voice tweet for {1}".format(e.uuid, l_msisdn))
 
  
def onplaying_vt_settings_owntweet_shared(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_owntweet_shared", e.call_instance)


def playing_vt_settings_owntweet_update_tag_menu(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_settings_owntweet_update_tag_menu", e.call_instance)


def ontransit_playcomplete_vt_settings_owntweet_upda(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  if(e.reason == 'digit_abort'):
    l_tag = UVContent().tags[int(e.dtmf)]
    UVContent().set_by_content_id(e.call_instance.tweets[0]['content_id'], "tags", l_tag)
    #TODO send sms to required users to inform about this
    e.fsm.play_vt_settings_owntweet_tag_updated(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_settings_owntweet_update_tag_later(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_settings_owntweet_update_tag_later(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_owntweet_update_tag_later", e.call_instance)


def onplaying_vt_settings_owntweet_tag_updated(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_owntweet_tag_updated", e.call_instance)


def onplaying_vt_settings_owntweet_delete(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_settings_owntweet_delete", e.call_instance)


def ontransit_playcomplete_vt_settings_owntweet_delete(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  if(e.reason == 'digit_abort'):
    l_action  = UVAudioPrompts().get_prompt_action('vt_settings_owntweet_delete', UVCache().hget(e.uuid, "src_telcoid"))
    if l_action is None:
      l_action = ""
    l_opt=""
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_act = l_opt.split('=')[1]
    if(l_opt == "del"):
      UVContent().set_by_content_id(e.call_instance.tweets[0]['content_id'], "status", l_opt)
      e.fsm.play_vt_settings_owntweet_deleted(uuid=e.uuid, call_instance = e.call_instance)
    else:
      e.fsm.play_vt_settings_owntweet_delete_later(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_settings_owntweet_delete_later(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_settings_owntweet_delete_later(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_owntweet_delete_later", e.call_instance)


def onplaying_vt_settings_owntweet_deleted(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_owntweet_deleted", e.call_instance)


def oninit_vt_settings_name(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_howmany, l_content = UVContent().get_content(l_msisdn, "name")
  if(0 == l_howmany):
    e.fsm.play_vt_settings_name_notfound(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.call_instance.voicename = l_content[0]['content']    
    e.call_instance.content_id = l_content[0]['content_id']    
    e.fsm.play_vt_settings_name(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_settings_name(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_wave_file(e.uuid, "vt_settings_name", e.call_instance.voicename, "0123456789*#", e.call_instance)


def onplaying_vt_settings_name_notfound(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_name_notfound", e.call_instance)


def onplaying_vt_settings_name_rerecord(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_settings_name_rerecord", e.call_instance)


def ontransit_playcomplete_vt_settings_name_rerecord(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  if(e.reason == 'digit_abort'):
    UVContent().set_state(e.call_instance.content_id, "del")
    e.fsm.play_vt_settings_name_rerecord_intro(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_settings_name_try_later(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_settings_name_record_try_later(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_name_record_try_later", e.call_instance)


def onplaying_vt_settings_name_rerecord_intro(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_name_rerecord_intro", e.call_instance)


def onplaying_vt_settings_name_beep(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_name_beep", e.call_instance)


def onvt_settings_record_name(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_norm_src = UVCache().hget(e.uuid, "norm_src")
  l_rec_file_path = prepare_rec_file_name(l_norm_src)
  UVCache().hset(e.uuid, "vt_settings_name", l_rec_file_path)
  l_found, l_max_duration = UVFeatureProfile().get_profile_value('vt_settings', 'name_max_record_duration')
  l_found, l_silence_duration = UVFeatureProfile().get_profile_value('vt_settings', 'name_max_silence_duration')
  l_found, l_dtmf_abort = UVFeatureProfile().get_profile_value('vt_settings', 'name_dtmf_abort')
  e.call_instance.curr_prompt_name = 'vt_settings_record_name'
  record_audio_file(e.uuid, l_rec_file_path, l_max_duration, l_silence_duration, l_dtmf_abort, e.call_instance)

def ontransit_recordcomplete_vt_settings_record_name(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, rec_duration: {1}, rec_file: {2}, dtmf:{3}".format(e.uuid, e.rec_duration, e.rec_file, e.dtmf))
  #TODO check for silence detection
  l_norm_src = UVCache().hget(e.uuid, "norm_src")
  l_telco_id = UVCache().hget(e.uuid, "src_telcoid")
  l_recfile = UVCache().hget(e.uuid, "vt_settings_name")
  UVContent().add_content(l_msisdn, l_telco_id, "name", l_recfile, e.rec_duration)


def onplaying_vt_settings_record_name_set(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_record_name_set", e.call_instance)


def oninit_vt_settings_privacy(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_found, l_profile = UVUserProfile().get_profile(l_msisdn)
  if(False == l_found):
    logger.error("{0} user {1} profile not found. This should n't happen".format(e.uuid, l_msisdn))
    play_audio_prompt(e.uuid, "play_vt_settings_privacy_try_again", e.call_instance)
  elif(l_profile['privacy'] == 'public'):
    play_audio_prompt_and_get_digits(e.uuid, "play_vt_settings_privacy_2_private", e.call_instance)
  else:
    play_audio_prompt_and_get_digits(e.uuid, "play_vt_settings_privacy_2_public", e.call_instance)
   

def onplaying_vt_settings_privacy_set_private(e): 
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  if(e.reason == 'digit_abort'):
    l_msisdn = UVCache().hget(e.uuid, "norm_src")
    UVUserProfile().set(l_msisdn, "privacy", "private")
    play_audio_prompt(e.uuid, "play_vt_settings_privacy_set_private", e.call_instance)
  else:
    play_audio_prompt(e.uuid, "play_vt_settings_privacy_try_again", e.call_instance)


def onplaying_vt_settings_privacy_set_public(e): 
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  if(e.reason == 'digit_abort'):
    l_msisdn = UVCache().hget(e.uuid, "norm_src")
    UVUserProfile().set(l_msisdn, "privacy", "public")
    play_audio_prompt(e.uuid, "play_vt_settings_privacy_set_public", e.call_instance)
  else:
    play_audio_prompt(e.uuid, "play_vt_settings_privacy_try_again", e.call_instance)


def oninit_vt_settings_lang(e): 
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  

def onplaying_vt_settings_langselect(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "play_vt_settings_langselect", e.call_instance)


def ontransit_playcomplete_vt_settings_langselect(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_lang = UVCache().hget(e.uuid, "lang")
  if(e.reason == 'digit_abort'):
    l_action  = UVAudioPrompts().get_prompt_action('vt_settings_langselect', UVCache().hget(e.uuid, "src_telcoid"))
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_lang = l_opt.split('=')[1]

    UVCache().hset(e.uuid, "lang", l_lang)
    l_msisdn = UVCache().hget(e.uuid, "norm_src")
    l_profile_updated  = UVUserProfile().set(l_msisdn, "lang", l_lang)
    e.fsm.play_vt_settings_langset(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_settings_langselect_try_again(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_settings_langselect_try_again(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_langselect_try_again", e.call_instance)


def onplaying_vt_settings_langset(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_settings_langset", e.call_instance)


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

