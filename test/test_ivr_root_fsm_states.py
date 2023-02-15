from ivr_root_fsm_handlers import *

states = {
  'initial': 'idle',
  'events': [
    #<src&dst normalization,opid, update channel, fetch src profile, raise event if src num invalid, if src profile not found or found, >
    {'name': 'incall',  'src': 'idle',  'dst': 'validate_incall'},
    {'name': 'invalid_srcnum',  'src': 'validate_incall',  'dst': 'invalidsrc_playing_welcome'},
    {'name': 'incall_src_prof_notfound',  'src': 'validate_incall',  'dst': 'src_profile_creation'},   #<create profile and raise src_prof_created event>
    {'name': 'src_prof_found',  'src': 'validate_incall',  'dst': 'playing_welcome'},
    {'name': 'playcomplete_welcome',  'src': 'playing_welcome',  'dst': 'finding_service'},

    {'name': 'playcomplete_welcome',  'src': 'invalidsrc_playing_welcome',  'dst': 'playing_invalidsrc'},
    {'name': 'playcomplete_invalidsrc',  'src': 'playing_invalidsrc',  'dst': 'playing_thankyou'},
    {'name': 'playcomplete_thankyou',  'src': 'playing_thankyou',  'dst': 'releasecall'},
    {'name': 'call_released',  'src': 'releasecall',  'dst': 'idle'},

    {'name': 'src_prof_created',  'src': 'src_profile_creation',  'dst': 'new_user_playing_welcome'},
    {'name': 'playcomplete_welcome',  'src': 'new_user_playing_welcome',  'dst': 'new_user_playing_langselect'},
    {'name': 'playcomplete_langselect',  'src': 'new_user_playing_langselect',  'dst': 'playing_langset'},
    {'name': 'playcomplete_langset',  'src': 'playing_langset',  'dst': 'finding_service'},

    {'name': 'service_notfound',  'src': 'finding_service',  'dst': 'playing_service_notfound'},
    {'name': 'playcomplete_service_notfound',  'src': 'playing_service_notfound',  'dst': 'playing_thankyou'}, #<here it continue to release call>

  ],

  'callbacks': {
    'onidle':    onidle,
    'onvalidate_incall':  onvalidate_incall,
    'oninvalidsrc_playing_welcome':   oninvalidsrc_playing_welcome,
    'onplaying_invalidsrc':   onplaying_invalidsrc,
    'onsrc_profile_creation': onsrc_profile_creation,
    'onplaying_welcome': onplaying_welcome,
    'onplaying_thankyou': onplaying_thankyou,
    'onreleasecall':    onreleasecall,
    'onnew_user_playing_welcome':    onnew_user_playing_welcome,
    'onnew_user_playing_langselect':    onnew_user_playing_langselect,
    'onplaycomplete_langselect':    onplaycomplete_langselect,
    'onplaying_langset':    onplaying_langset,
    'onfinding_service':    onfinding_service,
    'onplaying_service_notfound':    onplaying_service_notfound,
  }
}

