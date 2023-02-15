#import python standard libraries

#import third patry libraries

#import CUP libraries
from genutils import *
from vt_utils import *
from cache_server import UVCache
from relations import *
from content import *
from postbox_api import PostBox

logger = logging.getLogger('vt_app')

def onvalidating_vt_follow(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  UVCache().hset(e.uuid, "txn_start_time", str(datetime.now()))
  e.call_instance.txn_start_time = datetime.now()

  if(e.call_instance.parent_fsm):
    logging.info("{0} transferred callflow. parent fsm {1} collect tweeter number".format(e.uuid, e.call_instance.parent_fsm))
    e.fsm.play_vt_follow_enter_tweeter_num(uuid=e.uuid, call_instance = e.call_instance)
  else:
    l_tweeter_msisdn = UVCache().hget(e.uuid, "dst_srvc_num")
    UVCache().hset(e.uuid, "vt_follow_tweeter_num", l_tweeter_msisdn)
    e.fsm.validate_tweeter(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_follow_enter_tweeter_num(e): 
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_collect_digits(e.uuid, "vt_follow_enter_tweeter_num", e.call_instance)

def onfetching_tweeter_num(e): 
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_norm_state, l_tweeter_norm_num = UVNormalizer().normalize(e.dtmf)
  UVCache().hset(e.uuid, "vt_follow_tweeter_num", l_tweeter_norm_num)
  e.fsm.validate_tweeter(uuid=e.uuid, call_instance = e.call_instance)


def onvalidating_tweeter(e): 
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_tweeter_msisdn = UVCache().hget(e.uuid, "vt_follow_tweeter_num")
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_tp_found, l_profile = UVUserProfile().get_profile(l_tweeter_msisdn)
  if( False == l_tp_found):
    l_telcoid_found, l_tweeter_telcoid, l_dst_flags = UVNumberTelcoResolution().get_telco_id(l_tweeter_msisdn)
    if(False == l_telcoid_found):
      logger.critical("telco id not found for tweeter msisdn {0}.".format(l_tweeter_msisdn))
      #fire invalid_tweeter event
      e.fsm.invalid_tweeter(uuid=e.uuid, call_instance = e.call_instance)
    else:
      UVCache().hset(e.uuid, "vt_follow_tweeter_telcoid", l_tweeter_telcoid)
      #fire dormant tweeter follow
      e.fsm.dormant_tweeter(uuid=e.uuid, call_instance = e.call_instance, tweeter_msisdn = l_tweeter_msisdn, dormant_tweeter_telcoid = l_tweeter_telcoid)
  else: #user profile found
    UVCache().hset(e.uuid, "vt_follow_tweeter_name", l_profile[0]['user_name'])
    l_user_type = l_profile[0]['user_type']
    UVCache().hset(e.uuid, "vt_follow_tweeter_user_type", l_user_type)
    #check whether follow relation exists
    l_exists, l_state = UVRelations().is_relation_exists(l_msisdn, l_tweeter_msisdn)
    if(l_exists):
      logger.info("{0} follow relation exists({1}) between {2} and {3}. state {4}".format(e.uuid, l_exists, l_msisdn, l_tweeter_msisdn, l_state) )
      UVCache().hset(e.uuid, "vt_follow_relation_exists",1)
      UVCache().hset(e.uuid, "vt_follow_relation_state",l_state)
    else:
      logger.info("{0} follow relation doesn't exists({1}) between {2} and {3}. state {4}".format(e.uuid, l_exists, l_msisdn, l_tweeter_msisdn, l_state) )
      UVCache().hset(e.uuid, "vt_follow_relation_exists",0)
      UVCache().hset(e.uuid, "vt_follow_relation_state","")

    if(l_exists and l_state == "active"):
    #playback tweeters tweets to user
      e.fsm.play_vt_follow_tweets(uuid=e.uuid, call_instance = e.call_instance, tweeter_msisdn = l_tweeter_msisdn, src_msisdn = l_msisdn)
    else:
      if(l_user_type == 'premium'):
        e.fsm.premium_tweeter(uuid=e.uuid, call_instance = e.call_instance)
      else:
        e.fsm.community_tweeter(uuid=e.uuid, call_instance = e.call_instance)
    

def onplaying_vt_follow_invalid_tweeter(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_follow_invalid_tweeter", e.call_instance)

def onplaying_vt_follow_dormant_tweeter(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  #create user profile for dormant user
  l_found, l_lang = UVTelcoProfile().get(e.dormant_tweeter_telcoid, "lang")
  assert (l_found == True) , "language setting not found for telco_id {0}".format(e.dormant_tweeter_telcoid)   

  UVCache().hset(e.uuid, "lang", l_lang)
  UVUserProfile().create_tweeter_profile(e.tweeter_msisdn, l_lang, e.dormant_tweeter_telcoid, e.tweeter_msisdn, state = "dormant")
  UVStatsServer().update_stats_on_newdormantuser(e.dormant_tweeter_telcoid, "ivr")

  #create follow relation
  l_tweeter_msisdn = UVCache().hget(e.uuid, "vt_follow_tweeter_num")
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  UVRelations().create_relation(l_msisdn, l_tweeter_msisdn)

  play_audio_prompt(e.uuid, "vt_follow_dormant_tweeter", e.call_instance)
  #TODO SMS notification for dormant blogger
  PostBox().sendsms(e.uuid, "5555", e.dormant_tweeter_telcoid, "vt_follow_dormant_tweeter", l_tweeter_msisdn, sms_type = "template", lang = l_lang)

def onabort_vt_follow(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  if(e.call_instance.parent_fsm):
    logging.info("{0} Transferring call back to parent callflow {1}. resume event {2}".format(e.uuid, e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event))
    l_txn_duration = datetime.now() - e.call_instance.txn_start_time
    UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
    vt_cdr_gen(e.uuid, "txn", "vt_follow_abort")
    del e.fsm
    e.call_instance.current_fsm = e.call_instance.parent_fsm
    getattr(e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    logging.info("{0} Parent callflow not found. Proceed to release call now".format(e.uuid))
    e.fsm.play_thankyou(uuid=e.uuid, call_instance = e.call_instance)
    #TODO add call transfer to vt_disc feature

def ontransit_vt_follow_fetching_tweets(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_tweeter_msisdn = UVCache().hget(e.uuid, "vt_follow_tweeter_num")
  l_size, l_content = UVContent().get_content(l_tweeter_msisdn, "selftweet")
  if(l_size):
    #TODO quick hack. Storing all tweets in call_instance. Try storing in cache if possible
    e.call_instance.tweets = list(l_content)
    e.fsm.play_vt_follow_tweets_intro(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_follow_notweets(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_follow_notweets(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_follow_notweets", e.call_instance)

def onplaying_vt_follow_tweets_intro(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_follow_tweets_intro", e.call_instance)

def onplaying_vt_follow_tweets(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  if(e.src == "playing_vt_follow_tweets"):
    del e.call_instance.tweets[0]
  if(len(e.call_instance.tweets) > 0):
    play_wave_file(e.uuid, "vt_follow_tweets", e.call_instance.tweets[0]['content'], '0123456789*#')
  else:
    e.fsm.play_vt_follow_nomore_tweets(uuid=e.uuid, call_instance = e.call_instance)

def onplaying_vt_follow_nomore_tweets(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_follow_nomore_tweets", e.call_instance)

def onplaying_vt_follow_community_tweeter(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_follow_community_tweeter", e.call_instance)

def ontransit_vt_follow_community_tweeter_confirm(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_tweeter_msisdn = UVCache().hget(e.uuid, "vt_follow_tweeter_num")
  l_tweeter_name = UVCache().hget(e.uuid, "vt_follow_tweeter_name")
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_act = ""
  if(e.reason == 'digit_abort'):
    l_action  = UVAudioPrompts().get_prompt_action('vt_follow_community_tweeter', UVCache().hget(e.uuid, "src_telcoid"))
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_act = l_opt.split('=')[1]
    logger.info("uuid: {0}, dtmf: {1}, action: {2}".format(e.uuid, e.dtmf, l_act))

  l_relation_exists = int(UVCache().hget(e.uuid, "vt_follow_relation_exists"))
  l_state = UVCache().hget(e.uuid, "vt_follow_relation_state")
  if(l_act == "follow"):
    if(l_relation_exists):
        if( l_state == "barred" ):
          logger.info("uuid: {0} follower {1} barred to follow tweeter {2}/{3}".format(e.uuid, l_msisdn, l_tweeter_msisdn, l_tweeter_name))
          play_audio_prompt(e.uuid, "vt_follow_community_tweeter_barred", e.call_instance)
        else: #l_state == "barred"
          UVRelations().update_relation(l_msisdn, l_tweeter_msisdn, relation="follow", state="active")
    else: #l_relation_exists
      UVRelations().create_relation(l_msisdn, l_tweeter_msisdn, state="active")
      play_audio_prompt(e.uuid, "vt_follow_community_tweeter_confirm", e.call_instance)
  else: #user didn't input DTMF
    play_audio_prompt(e.uuid, "vt_follow_community_tweeter_trylater", e.call_instance)

def onplaying_vt_follow_premium_tweeter_intro(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_intro_path = UVConfig().get_config_value("vt","premium_tweeter_intro_path")
  try:
    assert l_intro_path is not None, "premium_tweeter_intro_path not configured in vt section in ucp.conf"
  except AssertionError:
    logger.exception("premium_tweeter_intro_path not configured in vt section in ucp.conf")
  l_intro_file = l_intro_path + UVCache().hget(e.uuid, "vt_follow_tweeter_name") + "_intro.wav"
  play_wave_file(e.uuid, "vt_follow_premium_tweeter_intro", l_intro_file, "0123456789*#", e.call_instance)

def onplaying_vt_follow_premium_tweeter(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_follow_premium_tweeter", e.call_instance)

def ontransit_vt_follow_premium_tweeter(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_tweeter_msisdn = UVCache().hget(e.uuid, "vt_follow_tweeter_num")
  l_tweeter_name = UVCache().hget(e.uuid, "vt_follow_tweeter_name")
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_act = ""
  if(e.reason == 'digit_abort'):
    l_action  = UVAudioPrompts().get_prompt_action('vt_follow_premium_tweeter', UVCache().hget(e.uuid, "src_telcoid"))
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_act = l_opt.split('=')[1]
    logger.info("uuid: {0}, dtmf: {1}, action: {2}".format(e.uuid, e.dtmf, l_act))

  l_relation_exists = UVCache().hget(e.uuid, "vt_follow_relation_exists")
  l_state = UVCache().hget(e.uuid, "vt_follow_relation_state")
  if(l_act == "follow"):
    if(l_relation_exists):
        if( l_state == "barred" ):
          logger.info("uuid: {0} follower {1} barred to follow tweeter {2}/{3}".format(e.uuid, l_msisdn, l_tweeter_msisdn, l_tweeter_name))
          play_audio_prompt(e.uuid, "vt_follow_premier_tweeter_barred", e.call_instance)
        else: #l_state == "barred"
          #TODO initiate subscription/renewal request
          UVRelations().update_relation(l_msisdn, l_tweeter_msisdn, relation="follow", state="preactive")
    else: #l_relation_exists
      UVRelations().create_relation(l_msisdn, l_tweeter_msisdn, state="preactive")
      #TODO initiate subscription request
      play_audio_prompt(e.uuid, "vt_follow_premium_tweeter_confirm_tentative", e.call_instance)
  else:
    logger.info("uuid: {0} NO DTMF. user {1} not choosen to follow premium tweeter {2}".format(e.uuid, l_msisdn, l_tweeter_name))
    play_audio_prompt(e.uuid, "vt_follow_premium_tweeter_trylater", e.call_instance)


def onplaying_vt_follow_premium_tweeter_confirm_tentative(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_follow_premium_tweeter_confirm_tentative", e.call_instance)

def onplaying_vt_follow_premium_tweeter_trylater(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_follow_premium_tweeter_trylater", e.call_instance)

def oncompleted_vt_follow(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_user_type = UVCache().hget(e.uuid, "vt_follow_tweeter_user_type")
  if(l_user_type == "premium"):
    l_txn = "vt_follow_premium"
  else:
    l_txn = "vt_follow_community"

  if(e.call_instance.parent_fsm):
    logging.info("{0} Transferring call back to parent callflow {1}. resume event {2}".format(e.uuid, e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event))
    l_txn_duration = datetime.now() - e.call_instance.txn_start_time
    UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
    vt_cdr_gen(e.uuid, "txn", l_txn)
    #TODO clean this statemachine object
    del e.fsm
    e.call_instance.current_fsm = e.call_instance.parent_fsm
    getattr(e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    logging.info("{0} Parent callflow not found. Proceed to release call now".format(e.uuid))
    e.fsm.play_thankyou(uuid=e.uuid, call_instance = e.call_instance)
    #TODO add call transfer to vt_disc feature
    
def onplaying_thankyou(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "thankyou", e.call_instance)

def onreleasecall(e):
  logging.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  """
    Description : Release call handler
    Input       : statemachine event. Additional parameters will be members of event 'e' 
    Output&Algo : Write CDR, deletes redis cache, update stats and hangup the call
  """
  l_txn_duration = datetime.now() - e.call_instance.txn_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "txn", "vt_follow")
  l_txn_duration = datetime.now() - e.call_instance.call_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "call", "release")
  logger.info("uuid: {0} deleting call cache".format(e.uuid))
  UVCache().delete(e.uuid)

