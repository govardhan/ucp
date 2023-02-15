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


import vt_post_fsm_states
import vt_listen_fsm_states
import vt_follow_fsm_states
import vt_disc_fsm_states


logger = logging.getLogger('vt_app')
def onfinding_service(e):
  logger.info("event: {0}, from: {1}, to:{2}".format(e.event, e.src, e.dst))
  #logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("event attributes: ".format(dir(e)))
  #e.fsm.start_allin1_tweet()

def onplaying_vt_allin1_mainmenu(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  play_audio_prompt_and_get_digits(e.uuid, "vt_allin1_mainmenu", e.call_instance)


def onplaycomplete_vt_allin1_mainmenu(e):
  logger.info("uuid: {0}, event: {1}, from: {2}, to:{3}".format(e.uuid, e.event, e.src, e.dst))
  logger.info("uuid: {0}, event: {1}, reason {2}, dtmf {3}".format(e.uuid, e.event, e.reason, e.dtmf))
  l_action  = UVAudioPrompts().get_prompt_action('vt_allin1_mainmenu', UVCache().hget(e.uuid, "src_telcoid"))
  #If user dont choose - default is discovery feature
  l_option = "vt_disc"
  if(e.reason == 'digit_abort'):
    for l_opt in l_action.split(','):
      if(l_opt.split('=')[0] == e.dtmf):
        l_option = l_opt.split('=')[1]

  l_states = l_option + "_fsm_states.states"
  logger.info("uuid: {0}, loading {1} statemachine".format(e.uuid, l_states))
  e.call_instance.parent_fsm = e.fsm
  e.call_instance.parent_fsm_resume_event = "start_vt_allin1"
  e.call_instance.current_fsm = Fysom(eval(l_states))
  #prepare event and fire
  l_event_name = "start_"+l_option
  getattr(e.call_instance.current_fsm, l_event_name)(uuid=e.uuid, call_instance = e.call_instance)
 
