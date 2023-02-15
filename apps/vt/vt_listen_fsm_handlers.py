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


def onvalidate_vt_listen(e):
  logger.info("event: {0}, from: {1}, to:{2}".format( e.event, e.src, e.dst))
  UVCache().hset(e.uuid, "txn_start_time", str(datetime.now()))
  e.call_instance.txn_start_time = datetime.now()

  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  l_tc, l_tweets = UVContent().get_content(l_msisdn, "tweet")
  #TODO play shared messages
  #l_sc, e.call_instance.share = UVContent().get_content(l_msisdn, "share")

  if( l_tc == 0 and l_rc == 0 and l_r2rc == 0 and l_sc == 0):
    e.fsm.playing_vt_listen_no_tweets(uuid = e.uuid, call_instance = e.call_instance)
  else:
    e.call_instance.tweets = list(l_tweets)
    e.fsm.play_vt_listen_intro(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_listen_no_tweets(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_notweets", e.call_instance)


def oncompleted_vt_listen(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))

  if(e.src == "playing_vt_listen_no_tweets"):
    l_txn = "vt_listen_notweets"
  else:
    l_txn = "vt_listen"

  if(e.call_instance.parent_fsm):
    logger.info("{0} Transferring call back to parent callflow {1}. resume event {2}".format(e.uuid, e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event))
    l_txn_duration = datetime.now() - e.call_instance.txn_start_time
    UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
    vt_cdr_gen(e.uuid, "txn", l_txn)
    #TODO clean this statemachine object
    del e.fsm
    e.call_instance.current_fsm = e.call_instance.parent_fsm
    getattr(e.call_instance.parent_fsm, e.call_instance.parent_fsm_resume_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    logger.info("{0} Parent callflow not found. Proceed to release call now".format(e.uuid))
    e.fsm.play_thankyou(uuid=e.uuid, call_instance = e.call_instance)
    #TODO add call transfer to vt_disc feature


def onplaying_vt_listen_intro(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_intro", e.call_instance)


def ontransit_playcomplete_vt_listen_tweet(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  if(e.reason == 'digit_abort'):
    l_found, l_action = UVFeatureProfile().get_profile_value('vt_listen', 'tweet_options')
    if(False == l_found):
      logger.error("uuid: {0} feature profile key vt_listen:tweet_options not found. fallback to no option mode")
      e.fsm.play_vt_listen_tweet(uuid=e.uuid, call_instance = e.call_instance)
    else:
      l_act = ""
      for l_opt in l_action.split(','):
        if(l_opt.split('=')[0] == e.dtmf):
          l_act = l_opt.split('=')[1]
      logger.info("uuid: {0}, dtmf: {1}, action: {2}".format(e.uuid, e.dtmf, l_act))
      l_event = "vt_listen_"+l_act
      getattr(e.fsm, l_event)(uuid=e.uuid, call_instance = e.call_instance)
  else:
    e.fsm.play_vt_listen_tweet(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_listen_tweet(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  if(e.src != "playing_vt_listen_intro"):
    del e.call_instance.tweets[0]
  if(len(e.call_instance.tweets) > 0):
    l_found, l_dtmf = UVFeatureProfile().get_profile_value('vt_listen', 'tweet_option_dtmf')
    if(False == l_found):
      logger.error("uuid: {0} feature profile key vt_listen:tweet_options not found. use default value 1234567")
      l_dtmf = "1234567"
    l_found, l_silence = UVFeatureProfile().get_profile_value('vt_listen', 'wait_time_after_play')
    if(False == l_found):
      logger.error("uuid: {0} feature profile key vt_listen:wait_time_after_play not found. use default value 2000")
      l_silence = "2000"
    play_wave_file_get_digits(e.uuid, "vt_listen_tweet", e.call_instance.tweets[0]['content'], l_dtmf, l_silence, e.call_instance)
    l_msisdn = UVCache().hget(e.uuid, "norm_src")
    UVContentActivity().onread(e.uuid, l_msisdn, e.call_instance.tweets[0])
  else:
    #TODO play shared msgs, rep2rep
    e.fsm.play_vt_listen_nomore_tweets(uuid=e.uuid, call_instance = e.call_instance)


def onplaying_vt_listen_nomore_tweets(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_nomore_tweets", e.call_instance)


def onplaying_vt_liked(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_liked", e.call_instance)


def onplaying_vt_listen_reply_intro(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  e.call_instance.reply_start_time = datetime.now()
  play_audio_prompt(e.uuid, "vt_listen_reply_intro", e.call_instance)


def onplaying_vt_listen_reply_beep(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_reply_beep", e.call_instance)


def onrecording_vt_listen_reply(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_norm_src = UVCache().hget(e.uuid, "norm_src")
  l_rep_file_path = prepare_rec_file_name(l_norm_src)
  UVCache().hset(e.uuid, "vt_listen_rep_file", l_rep_file_path)
  l_found, l_max_duration = UVFeatureProfile().get_profile_value('vt_listen', 'max_reply_duration')
  l_found, l_silence_duration = UVFeatureProfile().get_profile_value('vt_listen', 'max_reply_silence_duration')
  l_found, l_dtmf_abort = UVFeatureProfile().get_profile_value('vt_listen', 'reply_dtmf_abort')
  e.call_instance.curr_prompt_name = 'vt_listen_reply'
  record_audio_file(e.uuid, l_rep_file_path, l_max_duration, l_silence_duration, l_dtmf_abort, e.call_instance)


def onplaying_vt_listen_reply_confirm(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, rec_duration: {1}, rec_file: {2}, dtmf:{3}".format(e.uuid, e.rec_duration, e.rec_file, e.dtmf))

  l_msisdn = UVCache().het(e.uuid, "norm_src")
  l_telco_id = UVCache().hget(e.uuid, "src_telcoid")
  l_recfile = UVCache().hget(e.uuid, "vt_listen_rep_file")

  l_recduration = UVCache().hget(e.uuid, "txn_duration")
  UVContent().add_content(l_msisdn, l_telco_id, "rep2tweet", l_recfile, e.rec_duration, e.call_instance.tweets[0]['content_id'])
  
  l_od_val = UVCache().hget(e.uuid, "txn_start_time")
  UVCache().hset(e.uuid, "txn_start_time", e.call_instance.reply_start_time)
  l_txn_duration = datetime.now() - e.call_instance.reply_start_time
  UVCache().hset(e.uuid, "txn_duration", l_txn_duration.seconds)
  vt_cdr_gen(e.uuid, "txn", "vt_listen_reply")
  UVCache().hset(e.uuid, "txn_start_time", l_od_val)

  #TODO SMS notification to the content owner
  play_audio_prompt(e.uuid, "vt_listen_reply_confirm", e.call_instance)


def ontransit_playing_vt_listen_comments(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_rc, e.call_instance.comments2tweet = UVContent().get_content_by_ref_id(e.call_instance.tweets[0]['content_id'], "rep2tweet")
  if(l_rc == 0):
    logger.info("{0} no comments for content id {1} type rep2tweet".format(e.call_instance.tweets[0]['content_id']))
    e.fsm.play_vt_listen_nocomments(e.uuid, e.call_instance)
  else:
    e.fsm.play_vt_listen_comments_intro(e.uuid, e.call_instance)


def onplaying_vt_listen_nocomments(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_nocomments", e.call_instance)


def onplaying_vt_listen_comments_intro(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_comments_intro", e.call_instance)


def onplaying_vt_listen_comment(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_comment = e.call_instance.comments2tweet[0]

  l_found, l_dtmf = UVFeatureProfile().get_profile_value('vt_listen', 'comment_abort_dtmf')
  if(False == l_found):
    logger.error("uuid: {0} feature profile key vt_listen:comment_abort_dtmf not found. use default value #")
    l_dtmf = "#"
  l_found, l_silence = UVFeatureProfile().get_profile_value('vt_listen', 'wait_time_after_comment')
  if(False == l_found):
    logger.error("uuid: {0} feature profile key vt_listen:wait_time_after_play not found. use default value 1000")
    l_silence = "1000"
  play_wave_file_get_digits(e.uuid, "vt_listen_comment", l_comment['content'], l_dtmf, l_silence, e.call_instance)
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  UVContentActivity().onread(e.uuid, l_comment)


def ontransit_playcomplete_vt_listen_comment(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  if(e.reason == 'digit_abort'):
    logger.error("{0} user aborted to listen comments".format(e.uuid))
    e.fsm.play_vt_listen_comments_aborted(uuid=e.uuid, call_instance = e.call_instance)
  else:
    del e.call_instance.comments2tweet[0]
    if ( len(e.call_instance.comments2tweet) > 0 ):
      e.fsm.play_vt_listen_comment(uuid=e.uuid, call_instance = e.call_instance)
    else:
      e.fsm.play_vt_listen_nomore_comments(uuid=e.uuid, call_instance = e.call_instance)
      

def onplaying_vt_listen_comments_aborted(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_comments_aborted", e.call_instance)


def onplaying_vt_listen_nomore_comments(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_nomore_comments", e.call_instance)

#TODO write txn cdr after listening to comments

def onplaying_vt_listen_enterphnum2share(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_collect_digits(e.uuid, "vt_listen_enterphnum2share", e.call_instance)


def ontransit_playcomplete_vt_enterphnum2share(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))

  _, l_norm_num = UVNormalizer().normalize(e.dtmf)
  l_up_found, l_profile = UVUserProfile().get_profile(l_norm_num)
  l_telcoid = ""
  l_state = "active"
  if( False == l_up_found):
    l_telcoid_found, l_telcoid, l_dst_flags = UVNumberTelcoResolution().get_telco_id(l_norm_num)
    if(False == l_telcoid_found):
      logger.info("{0} telco id not found for the normalized number {1}.".format(e.uuid, l_norm_num))
      #fire invalid_tweeter event
      e.fsm.play_vt_listen_invalid_phnum(uuid=e.uuid, call_instance = e.call_instance)
      return
    else:
      l_lang_found, l_lang = UVTelcoProfile().get(l_telcoid, "lang")
      UVStatsServer().update_stats_on_newdormantuser(l_telcoid, "ivr")
      create_profile(msisdn=l_norm_num, lang=l_lang, telco_id=l_telcoid, user_name=l_norm_num, user_type = "community", state = "dormant")
      l_state = "dormant"
  else:
    l_telcoid = l_profile['telco_id']

  if(l_telcoid_found == True or l_up_found == True):
    UVContent().add_content(l_norm_num, l_telco_id, "retweet", e.call_instance.tweets[0]['content'], e.call_instance.tweets[0]['length'], e.call_instance.tweets[0]['content_id'])
    l_msisdn = UVCache().hget(e.uuid, "norm_src")
    UVRelations().create_relation(l_msisdn, l_norm_num, relation="share", state=l_state)
    UVContentActivity().onshare(e.uuid, l_msisdn, e.call_instance.tweets[0])
    #TODO Send content share SMS to l_norm_num 
    #TODO Send product introduction SMS to l_norm_num in case of dormant user


def onplaying_vt_listen_tweet_shared(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_tweet_shared", e.call_instance)


def onplaying_vt_listen_invalid_phnum(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_invalid_phnum", e.call_instance)


def ontransit_vt_listen_save(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  UVContentActivity().onsave(e.uuid, l_msisdn, e.call_instance.tweets[0])


def onplaying_vt_saved(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_saved", e.call_instance)


def ontransit_vt_listen_del(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  l_msisdn = UVCache().hget(e.uuid, "norm_src")
  UVContentActivity().ondel(e.uuid, l_msisdn, e.call_instance.tweets[0])


def onplaying_vt_deleted(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "vt_listen_deleted", e.call_instance)


def onplaying_thankyou(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt(e.uuid, "thankyou", e.call_instance)


def onvt_listen_releasecall(e):
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


