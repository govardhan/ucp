# -*- coding: utf-8 -*-
from vt_allin1_fsm_handlers import *

states = {
  'initial': 'finding_service',
  'events': [

    #<press 1 to find new tweeters, 2 to listen to tweets, 3 to record your own tweet  , 4 to follow friend, 5 for settings/more options - 3 times>
    {'name': 'start_vt_allin1',  'src': 'finding_service',  'dst': 'playing_vt_allin1_mainmenu'},
    {'name': 'playcomplete_vt_allin1_mainmenu',  'src': 'playing_vt_allin1_mainmenu',  'dst': 'starting_vt_services'}, #<for digit 1>
    {'name': 'start_vt_allin1',  'src': 'starting_vt_services',  'dst': 'playing_vt_allin1_mainmenu'}, #<after completing submenu>
    {'name': 'calldisconnect',  'src': ['playing_vt_allin1_mainmenu', 'starting_vt_services', 'playcomplete_vt_allin1_mainmenu'],  'dst': 'calldisconnected'}, #<when user disconnects the call>

  ],

  'callbacks': {
    'onfinding_service':   onfinding_service,
    'onplaying_vt_allin1_mainmenu':  onplaying_vt_allin1_mainmenu,
    'onplaycomplete_vt_allin1_mainmenu':   onplaycomplete_vt_allin1_mainmenu,
    'oncalldisconnected':   oncalldisconnected,
  }
}

