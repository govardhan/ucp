from vt_disc_fsm_handlers import *

states = {
  'initial': 'starting_vt_services',
  'events': [

    #choose premier tweeter to follow any time during message play
    {'name': 'start_vt_disc',  'src': 'starting_vt_services',  'dst': 'init_vt_disc_tweeters'},
    {'name': 'play_vt_disc_intro',  'src': 'init_vt_disc_tweeters',  'dst': 'playing_vt_disc_intro'},

    {'name': 'play_vt_disc_no_tweeters',  'src': 'init_vt_disc_tweeters',  'dst': 'playing_vt_disc_no_tweeters'},
    {'name': 'playcomplete_vt_disc_no_tweeters',  'src': 'playing_vt_disc_no_tweeters',  'dst': 'completed_vt_disc'},
    {'name': 'playcomplete_vt_disc_intro',  'src': 'playing_vt_disc_intro',  'dst': 'playing_vt_disc_press_digit'},

    {'name': 'playcomplete_vt_disc_press_digit',  'src': 'playing_vt_disc_press_digit',  'dst': 'transit_playcomplete_vt_disc_press_digit'},
    {'name': 'play_vt_disc_tweeter',  'src': 'transit_playcomplete_vt_disc_press_digit',  'dst': 'playing_vt_disc_tweeter'},
    {'name': 'play_vt_disc_follow_confirm_tentative',  'src': 'transit_playcomplete_vt_disc_press_digit',  'dst': 'playing_vt_disc_follow_confirm_tentative'},
    {'name': 'playcomplete_vt_disc_tweeter',  'src': 'playing_vt_disc_tweeter',  'dst': 'transit_playcomplete_vt_disc_tweeter'},
    {'name': 'play_vt_disc_follow_confirm_tentative',  'src': 'transit_playcomplete_vt_disc_tweeter',  'dst': 'playing_vt_disc_follow_confirm_tentative'},
    {'name': 'play_vt_disc_press_digit',  'src': 'transit_playcomplete_vt_disc_tweeter',  'dst': 'playing_vt_disc_press_digit'},
    {'name': 'playcomplete_vt_disc_follow_confirm_tentative',  'src': 'playing_vt_disc_follow_confirm_tentative',  'dst': 'transit_playcomplete_vt_disc_follow_confirm_tentative'},
    {'name': 'play_vt_disc_no_tweeters',  'src': 'transit_playcomplete_vt_disc_follow_confirm_tentative',  'dst': 'playing_vt_disc_no_tweeters'},
    {'name': 'play_vt_disc_intro',  'src': 'transit_playcomplete_vt_disc_follow_confirm_tentative',  'dst': 'playing_vt_disc_intro'},

    {'name': 'play_vt_disc_nomore_tweeters',  'src': 'transit_playcomplete_vt_disc_tweeter',  'dst': 'playing_vt_disc_nomore_tweeters'},
    {'name': 'playcomplete_vt_disc_nomore_tweeters',  'src': 'playing_vt_disc_nomore_tweeters',  'dst': 'playing_vt_disc_try_again'},
    {'name': 'playcomplete_vt_disc_try_again',  'src': 'playing_vt_disc_try_again',  'dst': 'playing_thankyou'},

    {'name': 'playcomplete_thankyou',  'src': 'playing_thankyou',  'dst': 'releasecall'},
    {'name': 'calldisconnect',  'src': ['starting_vt_services', 'init_vt_disc_tweeters', 'playing_vt_disc_intro', 'playing_vt_disc_no_tweeters', 'vt_disc_nomore', 'playing_vt_disc_press_digit', 'transit_playcomplete_vt_disc_press_digit', 'playing_vt_disc_tweeter', 'transit_vt_disc_follow', 'transit_playcomplete_vt_disc_tweeter', 'playing_vt_disc_follow_confirm_tentative', 'transit_playcomplete_vt_disc_follow_confirm_tentative', 'playing_vt_disc_nomore_tweeters', 'playing_vt_disc_try_again', 'playing_thankyou'],  'dst': 'calldisconnected'}, #<when user disconnects the call>

  ],

  'callbacks': {
    'oninit_vt_disc_tweeters':   oninit_vt_disc_tweeters,
    'onplaying_vt_disc_intro':  onplaying_vt_disc_intro,
    'onplaying_vt_disc_no_tweeters':   onplaying_vt_disc_no_tweeters,
    'oncompleted_vt_disc':   oncompleted_vt_disc,
    'onplaying_vt_disc_press_digit':   onplaying_vt_disc_press_digit,
    'ontransit_playcomplete_vt_disc_press_digit':   ontransit_playcomplete_vt_disc_press_digit,
    'onplaying_vt_disc_tweeter':   onplaying_vt_disc_tweeter,
    'onplaying_follow_vt_disc_confirm_tentative':   onplaying_vt_disc_follow_confirm_tentative,
    'ontransit_playcomplete_follow_vt_disc_confirm_tentative':   ontransit_playcomplete_vt_disc_follow_confirm_tentative,
    'ontransit_playcomplete_vt_disc_tweeter':   ontransit_playcomplete_vt_disc_tweeter,
    'onplaying_vt_disc_nomore_tweeters':   onplaying_vt_disc_nomore_tweeters,
    'onplaying_vt_disc_try_again':   onplaying_vt_disc_try_again,
    'onplaying_thankyou':   onplaying_thankyou,
    'onreleasecall':   onreleasecall,
    'oncalldisconnected':   oncalldisconnected,
  }
}

