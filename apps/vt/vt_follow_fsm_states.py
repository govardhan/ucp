from vt_follow_fsm_handlers import *

states = {
  'initial': 'starting_vt_services',
  'events': [

    {'name': 'start_vt_follow',  'src': 'starting_vt_services',  'dst': 'validating_vt_follow'}, #check whether tweeternum available
    {'name': 'play_vt_follow_enter_tweeter_num',  'src': 'validating_vt_follow',  'dst': 'playing_vt_follow_enter_tweeter_num'}, #enter tweeter num
    {'name': 'playcomplete_vt_follow_enter_tweeter_num',  'src': 'playing_vt_follow_enter_tweeter_num',  'dst': 'fetching_tweeter_num'}, #normalize tweeter num
    {'name': 'validate_tweeter',  'src': 'fetching_tweeter_num',  'dst': 'validating_tweeter'}, #normalize tweeter num

    {'name': 'validate_tweeter',  'src': 'validating_vt_follow',  'dst': 'validating_tweeter'}, #validate tweeter

    {'name': 'invalid_tweeter',  'src': 'validating_tweeter',  'dst': 'playing_vt_follow_invalid_tweeter'},
    {'name': 'playcomplete_vt_follow_invalid_tweeter',  'src': 'playing_vt_follow_invalid_tweeter',  'dst': 'abort_vt_follow'},

    {'name': 'play_vt_follow_tweets',  'src': 'validating_tweeter',  'dst': 'transit_vt_follow_fetching_tweets'},
    {'name': 'play_vt_follow_notweets',  'src': 'transit_vt_follow_fetching_tweets',  'dst': 'playing_vt_follow_notweets'},
    {'name': 'playcomplete_vt_follow_notweets',  'src': 'playing_vt_follow_notweets',  'dst': 'completed_vt_follow'},

    {'name': 'play_vt_follow_tweets_intro',  'src': 'transit_vt_follow_fetching_tweets',  'dst': 'playing_vt_follow_tweets_intro'},
    {'name': 'playcomplete_vt_follow_tweets_intro',  'src': 'playing_vt_follow_tweets_intro',  'dst': 'playing_vt_follow_tweets'},
    {'name': 'playcomplete_vt_follow_tweets',  'src': 'playing_vt_follow_tweets',  'dst': 'playing_vt_follow_tweets'},
    {'name': 'play_vt_follow_nomore_tweets',  'src': 'playing_vt_follow_tweets',  'dst': 'playing_vt_follow_nomore_tweets'},
    {'name': 'playcomplete_vt_follow_nomore_tweets',  'src': 'playing_vt_follow_nomore_tweets',  'dst': 'completed_vt_follow'},

    {'name': 'dormant_tweeter',  'src': 'validating_tweeter',  'dst': 'playing_vt_follow_dormant_tweeter'},
    {'name': 'playcomplete_vt_follow_dormant_tweeter',  'src': 'playing_vt_follow_dormant_tweeter',  'dst': 'abort_vt_follow'},

    {'name': 'community_tweeter',  'src': 'validating_tweeter',  'dst': 'playing_vt_follow_community_tweeter'},
    {'name': 'playcomplete_vt_follow_community_tweeter',  'src': 'playing_vt_follow_community_tweeter',  'dst': 'transit_vt_follow_community_tweeter_confirm'},
    {'name': 'playcomplete_vt_follow_community_tweeter_barred',  'src': 'transit_vt_follow_community_tweeter_confirm',  'dst': 'completed_vt_follow'},
    {'name': 'playcomplete_vt_follow_community_tweeter_confirm',  'src': 'transit_vt_follow_community_tweeter_confirm',  'dst': 'completed_vt_follow'},
    {'name': 'playcomplete_vt_follow_community_tweeter_trylater',  'src': 'transit_vt_follow_community_tweeter_confirm',  'dst': 'completed_vt_follow'},

    {'name': 'premium_tweeter',  'src': 'validating_tweeter',  'dst': 'playing_vt_follow_premium_tweeter_intro'},
    {'name': 'playcomplete_vt_follow_premium_tweeter_intro',  'src': 'playing_vt_follow_premium_tweeter_intro',  'dst': 'playing_vt_follow_premium_tweeter'},
    {'name': 'playcomplete_vt_follow_premium_tweeter',  'src': 'playing_vt_follow_premium_tweeter',  'dst': 'transit_vt_follow_premium_tweeter'},
    {'name': 'play_vt_follow_premium_tweeter_confirm_tentative',  'src': 'transit_vt_follow_premium_tweeter',  'dst': 'playing_vt_follow_premium_tweeter_confirm_tentative'},
    {'name': 'play_vt_follow_premium_tweeter_trylater',  'src': 'transit_vt_follow_premium_tweeter',  'dst': 'playing_vt_follow_premium_tweeter_trylater'},
    {'name': 'playcomplete_vt_follow_premium_tweeter_confirm_tentative',  'src': 'playing_vt_follow_premium_tweeter_confirm_tentative',  'dst': 'completed_vt_follow'},
    {'name': 'playcomplete_vt_follow_premium_tweeter_trylater',  'src': 'playing_vt_follow_premium_tweeter_trylater',  'dst': 'completed_vt_follow'},


    {'name': 'play_thankyou',  'src': 'completed_vt_follow',  'dst': 'playing_thankyou'},
    {'name': 'playcomplete_thankyou',  'src': 'playing_thankyou',  'dst': 'releasecall'},
    {'name': 'call_released',  'src': 'releasecall',  'dst': 'idle'},

    {'name': 'calldisconnect',  'src': ['starting_vt_services', 'validating_vt_follow', 'playing_vt_follow_enter_tweeter_num', 'fetching_tweeter_num', 'validating_tweeter', 'playing_vt_follow_invalid_tweeter', 'transit_vt_follow_fetching_tweets', 'playing_vt_follow_notweets', 'playing_vt_follow_tweets_intro', 'playing_vt_follow_tweets', 'completed_vt_follow', 'playing_vt_follow_nomore_tweets', 'playing_vt_follow_dormant_tweeter', 'abort_vt_follow', 'playing_vt_follow_community_tweeter', 'transit_vt_follow_community_tweeter_confirm', 'playing_vt_follow_premium_tweeter_intro', 'playing_vt_follow_premium_tweeter', 'transit_vt_follow_premium_tweeter', 'playing_vt_follow_premium_tweeter_confirm_tentative', 'playing_vt_follow_premium_tweeter_trylater', 'playing_thankyou' ],  'dst': 'calldisconnected'}, #<when user disconnects the call>
  ],

  'callbacks': {
    'onvalidating_vt_follow':   onvalidating_vt_follow,
    'onplaying_vt_follow_enter_tweeter_num':   onplaying_vt_follow_enter_tweeter_num,
    'onfetching_tweeter_num':   onfetching_tweeter_num,
    'onvalidating_tweeter':   onvalidating_tweeter,
    'onplaying_vt_follow_invalid_tweeter':  onplaying_vt_follow_invalid_tweeter,
    'onplaying_vt_follow_dormant_tweeter':  onplaying_vt_follow_dormant_tweeter,

    'ontransit_vt_follow_fetching_tweets':  ontransit_vt_follow_fetching_tweets,
    'onplaying_vt_follow_tweets_intro':  onplaying_vt_follow_tweets_intro,
    'onplaying_vt_follow_notweets':  onplaying_vt_follow_notweets,
    'onplaying_vt_follow_tweets':  onplaying_vt_follow_tweets,
    'onplaying_vt_follow_nomore_tweets':  onplaying_vt_follow_nomore_tweets,
    
    'onabort_vt_follow':   onabort_vt_follow,
    'onplaying_vt_follow_community_tweeter':   onplaying_vt_follow_community_tweeter,
    'ontransit_vt_follow_community_tweeter_confirm':   ontransit_vt_follow_community_tweeter_confirm,
    'onplaying_vt_follow_premium_tweeter_intro':   onplaying_vt_follow_premium_tweeter_intro,
    'onplaying_vt_follow_premium_tweeter':   onplaying_vt_follow_premium_tweeter,
    'ontransit_vt_follow_premium_tweeter':   ontransit_vt_follow_premium_tweeter,
    'onplaying_vt_follow_premium_tweeter_confirm_tentative':   onplaying_vt_follow_premium_tweeter_confirm_tentative,
    'onplaying_vt_follow_premium_tweeter_trylater':   onplaying_vt_follow_premium_tweeter_trylater,
    'onplaying_thankyou':   onplaying_thankyou,
    'oncompleted_vt_follow':   oncompleted_vt_follow,
    'onreleasecall':   onreleasecall,
    'oncalldisconnected':   oncalldisconnected,
  }
}

