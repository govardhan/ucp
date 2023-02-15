from vt_post_fsm_handlers import *

states = {
  'initial': 'starting_vt_services',
  'events': [

    {'name': 'start_vt_post',  'src': 'starting_vt_services',  'dst': 'playing_vt_post_instruction'}, #record after beep
    {'name': 'playcomplete_vt_post_instruction',  'src': 'playing_vt_post_instruction',  'dst': 'playing_vt_post_beep'},
    {'name': 'play_vt_post_max_retires',  'src': 'playing_vt_post_instruction',  'dst': 'playing_vt_post_max_retires'}, #if more num of re-records
    {'name': 'playcomplete_vt_post_beep',  'src': 'playing_vt_post_beep',  'dst': 'recording_vt_post'},
    #TODO silence detection
    {'name': 'recordcomplete_vt_post',  'src': 'recording_vt_post',  'dst': 'playing_vt_post_hint'}, #if no dtmf press 1 to post, 2 to preview, 3 to re-record, 4 to cancel
    {'name': 'playcomplete_vt_post_hint',  'src': 'playing_vt_post_hint',  'dst': 'transit_state_vt_post_hint'},

    {'name': 'play_vt_post_tagging',  'src': 'transit_state_vt_post_hint',  'dst': 'playing_vt_post_tagging'}, #press 1 to tag friends, 2 to family 3 to fans 0 to all
    {'name': 'playcomplete_vt_post_tagging',  'src': 'playing_vt_post_tagging',  'dst': 'playing_vt_post_tagged'},
    {'name': 'playcomplete_vt_post_tagged',  'src': 'playing_vt_post_tagged',  'dst': 'completed_vt_post'},

    {'name': 'play_vt_post',  'src': 'transit_state_vt_post_hint',  'dst': 'playing_vt_post'}, #dtmf 2 to preview
    {'name': 'play_vt_post_instruction',  'src': 'transit_state_vt_post_hint',  'dst': 'playing_vt_post_instruction'}, #dtmf 3 to re-record
    {'name': 'play_vt_post_cancelled',  'src': 'transit_state_vt_post_hint',  'dst': 'playing_vt_post_cancelled'}, #dtmf 4 to cancel
    {'name': 'play_vt_post_max_retires',  'src': 'transit_state_vt_post_hint',  'dst': 'playing_vt_post_max_retires'}, #if more num of previews, re-records

    {'name': 'playcomplete_vt_post',  'src': 'playing_vt_post',  'dst': 'playing_vt_post_hint'}, #after preview repeate post_hint. limit number of previews

    {'name': 'playcomplete_vt_post_max_retires',  'src': 'playing_vt_post_max_retires',  'dst': 'playing_vt_post_tagging'}, 
    {'name': 'playcomplete_vt_post_cancelled',  'src': 'playing_vt_post_cancelled',  'dst': 'completed_vt_post'}, 


    {'name': 'play_thankyou',  'src': 'completed_vt_post',  'dst': 'playing_thankyou'},
    {'name': 'playcomplete_thankyou',  'src': 'playing_thankyou',  'dst': 'releasecall'},
    {'name': 'call_released',  'src': 'releasecall',  'dst': 'idle'},

    {'name': 'calldisconnect',  'src': ['starting_vt_services', 'playing_vt_post_instruction', 'playing_vt_post_beep', 'playing_vt_post_max_retires', 'recording_vt_post', 'playing_vt_post_hint', 'transit_state_vt_post_hint', 'playing_vt_post', 'playing_vt_post_tagging', 'playing_vt_post_cancelled', 'completed_vt_post', 'playing_thankyou', 'playing_vt_post_tagged'],  'dst': 'calldisconnected'}, #<when user disconnects the call>

  ],

  'callbacks': {
    'onplaying_vt_post_instruction':   onplaying_vt_post_instruction,
    'onplaying_vt_post_beep':  onplaying_vt_post_beep,
    'onrecording_vt_post':   onrecording_vt_post,
    'onrecordcomplete_vt_post':   onrecordcomplete_vt_post,
    'onplaying_vt_post_hint':   onplaying_vt_post_hint,
    'ontransit_state_vt_post_hint':   ontransit_state_vt_post_hint,
    'onplaying_vt_post_tagging':   onplaying_vt_post_tagging,
    'onplaying_vt_post_tagged':   onplaying_vt_post_tagged,
    'oncompleted_vt_post':   oncompleted_vt_post,
    'onplaying_vt_post':   onplaying_vt_post,
    'onplaying_vt_post_cancelled':   onplaying_vt_post_cancelled,
    'onplaying_vt_post_max_retires':   onplaying_vt_post_max_retires,
    'onplaying_thankyou':   onplaying_thankyou,
    'onreleasecall':   onreleasecall,
    'oncall_released':   oncall_released,
    'oncalldisconnected':   oncalldisconnected,
  }
}

