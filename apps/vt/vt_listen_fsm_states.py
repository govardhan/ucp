from vt_listen_fsm_handlers import *

states = {
  'initial': 'starting_vt_services',
  'events': [

    {'name': 'start_vt_listen',  'src': 'starting_vt_services',  'dst': 'validate_vt_listen'},
    {'name': 'play_vt_listen_notweets',  'src': 'validate_vt_listen',  'dst': 'playing_vt_listen_no_tweets'},
    {'name': 'playcomplete_vt_listen_no_tweets',  'src': 'playing_vt_listen_no_tweets',  'dst': 'completed_vt_listen'},

    #while playing voice tweet press 1 to like 2 to comment 3 to listen commens from all users 4 to share 5 to next 6 to save 7 to delete
    {'name': 'play_vt_listen_intro',  'src': 'validate_vt_listen',  'dst': 'playing_vt_listen_intro'},
    {'name': 'playcomplete_vt_listen_intro',  'src': 'playing_vt_listen_intro',  'dst': 'playing_vt_listen_tweet'},
    {'name': 'playcomplete_vt_listen_tweet',  'src': 'playing_vt_listen_tweet',  'dst': 'transit_playcomplete_vt_listen_tweet'},
    {'name': 'play_vt_listen_tweet',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'playing_vt_listen_tweet'},
    {'name': 'play_vt_listen_nomore_tweets',  'src': 'playing_vt_listen_tweet',  'dst': 'playing_vt_listen_nomore_tweets'},
    {'name': 'playcomplete_vt_listen_nomore_tweets',  'src': 'playing_vt_listen_nomore_tweets',  'dst': 'completed_vt_listen'},

    #option - like
    {'name': 'vt_listen_like',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'playing_vt_liked'},
    {'name': 'playcomplete_vt_liked',  'src': 'playing_vt_liked',  'dst': 'playing_vt_listen_tweet'},

    #option - reply
    {'name': 'vt_listen_reply',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'playing_vt_listen_reply_intro'}, #record your commend after beep
    {'name': 'playcomplete_vt_listen_reply_intro',  'src': 'playing_vt_listen_reply_intro',  'dst': 'playing_vt_listen_reply_beep'},
    {'name': 'playcomplete_vt_listen_reply_beep',  'src': 'playing_vt_listen_reply_beep',  'dst': 'recording_vt_listen_reply'},
    {'name': 'recordcomplete_vt_listen_reply',  'src': 'recording_vt_listen_reply',  'dst': 'playing_vt_listen_reply_confirm'},
    {'name': 'playcomplete_vt_listen_reply_confirm',  'src': 'playing_vt_listen_reply_confirm',  'dst': 'playing_vt_listen_tweet'},

    #option - listen others comments
    {'name': 'vt_listen_comments',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'transit_playing_vt_listen_comments'},
    {'name': 'play_vt_listen_nocomments',  'src': 'transit_playing_vt_listen_comments',  'dst': 'playing_vt_listen_nocomments'},
    {'name': 'playcomplete_vt_listen_nocomments',  'src': 'playing_vt_listen_nocomments',  'dst': 'playing_vt_listen_tweet'},
    {'name': 'play_vt_listen_comments_intro',  'src': 'transit_playing_vt_listen_comments',  'dst': 'playing_vt_listen_comments_intro'},
    {'name': 'playcomplete_vt_listen_comments_intro',  'src': 'playing_vt_listen_comments_intro',  'dst': 'playing_vt_listen_comment'},

    {'name': 'play_vt_listen_comment',  'src': 'transit_playing_vt_listen_comments',  'dst': 'playing_vt_listen_comment'},
    {'name': 'playcomplete_vt_listen_comment',  'src': 'playing_vt_listen_comment',  'dst': 'transit_playcomplete_vt_listen_comment'},
    {'name': 'play_vt_listen_comment',  'src': 'transit_playcomplete_vt_listen_comment',  'dst': 'playing_vt_listen_comment'},
    {'name': 'play_vt_listen_comments_aborted',  'src': 'transit_playcomplete_vt_listen_comment',  'dst': 'playing_vt_listen_comments_aborted'},
    {'name': 'play_vt_listen_tweet',  'src': 'playing_vt_listen_comments_aborted',  'dst': 'playing_vt_listen_tweet'},
    {'name': 'play_vt_listen_nomore_comments',  'src': 'transit_playcomplete_vt_listen_comment',  'dst': 'playing_vt_listen_nomore_comments'},
    {'name': 'playcomplete_vt_listen_nomore_comments',  'src': 'playing_vt_listen_nomore_comments',  'dst': 'playing_vt_listen_tweet'},

    #option - share
    {'name': 'vt_listen_share',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'playing_vt_listen_enterphnum2share'},
    {'name': 'playcomplete_vt_enterphnum2share',  'src': 'playing_vt_listen_enterphnum2share',  'dst': 'transit_playcomplete_vt_enterphnum2share'},
    {'name': 'play_vt_listen_invalid_phnum',  'src': 'transit_playcomplete_vt_enterphnum2share',  'dst': 'playing_vt_listen_invalid_phnum'},
    {'name': 'play_vt_listen_tweet_shared',  'src': 'transit_playcomplete_vt_enterphnum2share',  'dst': 'playing_vt_listen_tweet_shared'},

    {'name': 'playcomplete_vt_listen_invalid_phnum',  'src': 'playing_vt_listen_invalid_phnum',  'dst': 'playing_vt_listen_tweet'},
    {'name': 'playcomplete_vt_listen_tweet_shared',  'src': 'playing_vt_listen_tweet_shared',  'dst': 'playing_vt_listen_tweet'},

    #option - save
    {'name': 'vt_listen_save',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'transit_vt_listen_save'},
    {'name': 'vt_listen_save',  'src': 'transit_vt_listen_save',  'dst': 'playing_vt_saved'},
    {'name': 'playcomplete_vt_saved',  'src': 'playing_vt_saved',  'dst': 'playing_vt_listen_tweet'},

    #option - delete
    {'name': 'vt_listen_del',  'src': 'transit_playcomplete_vt_listen_tweet',  'dst': 'transit_vt_listen_del'},
    {'name': 'vt_listen_del',  'src': 'transit_vt_listen_del',  'dst': 'playing_vt_deleted'},
    {'name': 'playcomplete_vt_deleted',  'src': 'playing_vt_deleted',  'dst': 'playing_vt_listen_tweet'},

    {'name': 'play_thankyou',  'src': 'completed_vt_listen',  'dst': 'playing_thankyou'},
    {'name': 'playcomplete_thankyou',  'src': 'playing_thankyou',  'dst': 'vt_listen_releasecall'},
    {'name': 'calldisconnect',  'src': ['completed_vt_listen','playing_thankyou','playing_vt_deleted','playing_vt_liked','playing_vt_listen_comment','playing_vt_listen_comments_aborted','playing_vt_listen_comments_intro','playing_vt_listen_enterphnum2share','playing_vt_listen_intro','playing_vt_listen_invalid_phnum','playing_vt_listen_nocomments','playing_vt_listen_nomore_comments','playing_vt_listen_nomore_tweets','playing_vt_listen_no_tweets','playing_vt_listen_reply_beep','playing_vt_listen_reply_confirm','playing_vt_listen_reply_intro','playing_vt_listen_tweet','playing_vt_listen_tweet_shared','playing_vt_saved','recording_vt_listen_reply','starting_vt_services','transit_playcomplete_vt_enterphnum2share','transit_playcomplete_vt_listen_comment','transit_playcomplete_vt_listen_tweet','transit_playing_vt_listen_comments','transit_vt_listen_del','transit_vt_listen_save','validate_vt_listen','vt_listen_releasecall'],  'dst': 'calldisconnected'}, #<when user disconnects the call>

  ],

  'callbacks': {
    'onvalidate_vt_listen':   onvalidate_vt_listen,
    'onplaying_vt_listen_no_tweets':   onplaying_vt_listen_no_tweets,
    'oncompleted_vt_listen':   oncompleted_vt_listen,
    'onplaying_vt_listen_intro':   onplaying_vt_listen_intro,
    'onplaying_vt_listen_tweet':   onplaying_vt_listen_tweet,
    'ontransit_playcomplete_vt_listen_tweet':   ontransit_playcomplete_vt_listen_tweet,
    'onplaying_vt_listen_nomore_tweets':   onplaying_vt_listen_nomore_tweets,
    'onplaying_vt_liked':   onplaying_vt_liked,

    'onplaying_vt_listen_reply_intro':   onplaying_vt_listen_reply_intro,
    'onplaying_vt_listen_reply_beep':   onplaying_vt_listen_reply_beep,
    'onrecording_vt_listen_reply':   onrecording_vt_listen_reply,
    'onplaying_vt_listen_reply_confirm':   onplaying_vt_listen_reply_confirm,

    'ontransit_playing_vt_listen_comments':   ontransit_playing_vt_listen_comments,
    'onplaying_vt_listen_nocomments':   onplaying_vt_listen_nocomments,
    'onplaying_vt_listen_comments_intro':   onplaying_vt_listen_comments_intro,
    'ontransit_playcomplete_vt_listen_comment':   ontransit_playcomplete_vt_listen_comment,
    'onplaying_vt_listen_comment':   onplaying_vt_listen_comment,
    'onplaying_vt_listen_comments_aborted':   onplaying_vt_listen_comments_aborted,
    'onplaying_vt_listen_nomore_comments':   onplaying_vt_listen_nomore_comments,

    'onplaying_vt_listen_enterphnum2share':   onplaying_vt_listen_enterphnum2share,
    'ontransit_playcomplete_vt_enterphnum2share':   ontransit_playcomplete_vt_enterphnum2share,
    'onplaying_vt_listen_tweet_shared':   onplaying_vt_listen_tweet_shared,
    'onplaying_vt_listen_invalid_phnum':   onplaying_vt_listen_invalid_phnum,

    'ontransit_vt_listen_save':   ontransit_vt_listen_save,
    'onplaying_vt_saved':   onplaying_vt_saved,

    'ontransit_vt_listen_del':   ontransit_vt_listen_del,
    'onplaying_vt_deleted':   onplaying_vt_deleted,

    'onplaying_thankyou':   onplaying_thankyou,
    'onvt_listen_releasecall':   onvt_listen_releasecall,

  }
}

