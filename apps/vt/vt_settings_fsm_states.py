from vt_settings_fsm_handlers import *

states = {
  'initial': 'starting_vt_services',
  'events': [

    #press 1 to listen to your own tweets, 2 to preview & re-record your name 3 to change privacy 4 to change lang
    {'name': 'start_vt_settings',  'src': 'starting_vt_services',  'dst': 'init_vt_settings_menu'},
    {'name': 'play_vt_settings_menu',  'src': 'init_vt_settings_menu',  'dst': 'playing_vt_settings_menu'},
    {'name': 'playcomplete_vt_settings_menu',  'src': 'playing_vt_settings_menu',  'dst': 'transit_vt_settings_menu'},
    {'name': 'playcomplete_vt_settings_max_retries',  'src': 'playing_vt_settings_menu',  'dst': 'completed_vt_settings'},
    {'name': 'play_vt_settings_try_again',  'src': 'transit_vt_settings_menu',  'dst': 'playing_vt_settings_try_again'},
    {'name': 'playcomplete_vt_settings_try_again',  'src': 'playing_vt_settings_try_again',  'dst': 'completed_vt_settings'},

    #option - listen to own tweets
    #press 1 to share the vtweet to 10 random users, 2 to change tagging, press 3 to delete
    {'name': 'start_vt_settings_owntweet',  'src': 'transit_vt_settings_menu',  'dst': 'init_vt_settings_owntweet'},
    {'name': 'play_vt_settings_owntweet_notweets',  'src': 'init_vt_settings_owntweet',  'dst': 'playing_vt_settings_owntweet_notweets'},
    {'name': 'playcomplete_vt_settings_owntweet_notweets',  'src': 'playing_vt_settings_owntweet_notweets',  'dst': 'playing_vt_settings_menu'},

    {'name': 'play_vt_settings_owntweet_intro',  'src': 'init_vt_settings_owntweet',  'dst': 'playing_vt_settings_owntweet_intro'},
    {'name': 'playcomplete_vt_settings_owntweet_intro',  'src': 'playing_vt_settings_owntweet_intro',  'dst': 'playing_vt_settings_owntweet'},
    {'name': 'playcomplete_vt_settings_owntweet',  'src': 'playing_vt_settings_owntweet',  'dst': 'transit_playcomplete_vt_settings_owntweet'},
    {'name': 'play_vt_settings_owntweet',  'src': 'transit_playcomplete_vt_settings_owntweet',  'dst': 'playing_vt_settings_owntweet'},
    {'name': 'play_vt_settings_owntweet',  'src': 'transit_playcomplete_vt_settings_owntweet',  'dst': 'playing_vt_settings_owntweet_nomore'},
    {'name': 'playcompleted_vt_settings_owntweet_nomore',  'src': 'playing_vt_settings_owntweet_nomore',  'dst': 'playing_vt_settings_menu'},

    #option - listen+ random share
    {'name': 'share_vt_settings_owntweet',  'src': 'transit_playcomplete_vt_settings_owntweet',  'dst': 'vt_settings_owntweet_sharing'},
    {'name': 'play_vt_settings_owntweet_shared',  'src': 'vt_settings_owntweet_sharing',  'dst': 'playing_vt_settings_owntweet_shared'},
    {'name': 'playcomplete_vt_settings_owntweet_shared',  'src': 'playing_vt_settings_owntweet_shared',  'dst': 'playing_vt_settings_owntweet'},

    #option - listen+ update taging
    {'name': 'update_tag_vt_settings_owntweet',  'src': 'transit_playcomplete_vt_settings_owntweet',  'dst': 'playing_vt_settings_owntweet_update_tag_menu'},
    {'name': 'playcomplete_vt_settings_owntweet_update_tag_menu',  'src': 'playing_vt_settings_owntweet_update_tag_menu',  'dst': 'transit_playcomplete_vt_settings_owntweet_update_tag'},
    {'name': 'play_vt_settings_owntweet_update_tag_later',  'src': 'transit_playcomplete_vt_settings_owntweet_update_tag',  'dst': 'playing_vt_settings_owntweet_update_tag_later'},
    {'name': 'play_vt_settings_owntweet_tag_updated',  'src': 'transit_playcomplete_vt_settings_owntweet_update_tag',  'dst': 'playing_vt_settings_owntweet_tag_updated'},
    {'name': 'playcomplete_vt_own_vtweet_tag_updated',  'src': 'playing_vt_settings_owntweet_tag_updated',  'dst': 'playing_vt_settings_owntweet'},
    {'name': 'playcomplete_vt_settings_owntweet_update_tag_later',  'src': 'playing_vt_settings_owntweet_update_tag_later',  'dst': 'playing_vt_settings_owntweet'},

    #option - listen+ delete
    {'name': 'delete_vt_settings_owntweet',  'src': 'transit_playcomplete_vt_settings_owntweet',  'dst': 'playing_vt_settings_owntweet_delete'},
    {'name': 'playcomplete_vt_settings_owntweet_delete',  'src': 'playing_vt_settings_owntweet_delete',  'dst': 'transit_playcomplete_vt_settings_owntweet_delete'},
    {'name': 'play_vt_settings_owntweet_deleted',  'src': 'transit_playcomplete_vt_settings_owntweet_delete',  'dst': 'playing_vt_settings_owntweet_deleted'},
    {'name': 'play_vt_settings_owntweet_delete_later',  'src': 'transit_playcomplete_vt_settings_owntweet_delete',  'dst': 'playing_vt_settings_owntweet_delete_later'},
    {'name': 'playcomplete_vt_settings_owntweet_delete_later',  'src': 'playing_vt_settings_owntweet_delete_later',  'dst': 'playing_vt_settings_owntweet'},
    {'name': 'playcomplete_vt_settings_owntweet_deleted',  'src': 'playing_vt_settings_owntweet_deleted',  'dst': 'playing_vt_settings_owntweet'},


    #option - preview & re-record voice name
    {'name': 'start_vt_settings_name',  'src': 'transit_vt_settings_menu',  'dst': 'init_vt_settings_name'},
    {'name': 'play_vt_settings_name_notfound',  'src': 'init_vt_settings_name',  'dst': 'playing_vt_settings_name_notfound'},
    {'name': 'play_vt_settings_name',  'src': 'init_vt_settings_name',  'dst': 'playing_vt_settings_name'},
    {'name': 'playcomplete_vt_settings_name_notfound',  'src': 'playing_vt_settings_name_notfound',  'dst': 'playing_vt_settings_name_rerecord_intro'},
    {'name': 'playcomplete_vt_settings_name',  'src': 'playing_vt_settings_name',  'dst': 'playing_vt_settings_name_rerecord'},
    {'name': 'playcomplete_vt_settings_name_rerecord',  'src': 'playing_vt_settings_name_rerecord',  'dst': 'transit_playcomplete_vt_settings_name_rerecord'},
    {'name': 'play_vt_settings_name_record_try_later',  'src': 'transit_playcomplete_vt_settings_name_rerecord',  'dst': 'playing_vt_settings_name_record_try_later'},
    {'name': 'playcomplete_vt_settings_name_record_try_later',  'src': 'playing_vt_settings_name_try_later',  'dst': 'playing_vt_settings_menu'},
    {'name': 'play_vt_settings_name_rerecord_intro',  'src': 'transit_playcomplete_vt_settings_name_rerecord',  'dst': 'playing_vt_settings_name_rerecord_intro'},
    {'name': 'playcomplete__vt_settings_name_rerecord_intro',  'src': 'playing_vt_settings_name_rerecord_intro',  'dst': 'playing_vt_settings_name_beep'},

    {'name': 'playcomplete_vt_settings_name_beep',  'src': 'playing_vt_settings_name_beep',  'dst': 'vt_settings_record_name'},
    {'name': 'recordcomplete_vt_settings_record_name',  'src': 'vt_settings_record_name',  'dst': 'transit_recordcomplete_vt_settings_record_name'},
    {'name': 'play_vt_settings_record_name_set',  'src': 'transit_recordcomplete_vt_settings_record_name',  'dst': 'playing_vt_settings_record_name_set'},
    {'name': 'playcomplete_vt_settings_record_name_set',  'src': 'playing_vt_settings_record_name_set',  'dst': 'playing_vt_settings_menu'},

    #option - change privacy
    {'name': 'start_vt_settings_privacy',  'src': 'transit_vt_settings_menu',  'dst': 'init_vt_settings_privacy'},
    {'name': 'play_vt_settings_privacy_2_private',  'src': 'init_vt_settings_privacy',  'dst': 'playing_vt_settings_privacy_2_private'},
    {'name': 'play_vt_settings_privacy_2_public',  'src': 'init_vt_settings_privacy',  'dst': 'playing_vt_settings_privacy_2_public'},
    {'name': 'playcomplete_vt_settings_privacy_try_again',  'src': 'init_vt_settings_privacy',  'dst': 'playing_vt_settings_menu'},

    {'name': 'playcomplete_vt_settings_privacy_2_private',  'src': 'playing_vt_settings_privacy_2_private',  'dst': 'playing_vt_settings_privacy_set_private'},
    {'name': 'playcomplete_vt_settings_privacy_2_public',  'src': 'playing_vt_settings_privacy_2_public',  'dst': 'playing_vt_settings_privacy_set_public'},

    {'name': 'playcomplete_vt_settings_privacy_set_private',  'src': 'playing_vt_settings_privacy_set_private',  'dst': 'playing_vt_settings_menu'},
    {'name': 'playcomplete_vt_settings_privacy_set_public',  'src': 'playing_vt_settings_privacy_set_public',  'dst': 'playing_vt_settings_menu'},

    {'name': 'playcomplete_vt_settings_privacy_try_again',  'src': 'playing_vt_settings_privacy_set_private',  'dst': 'playing_vt_settings_menu'},
    {'name': 'playcomplete_vt_settings_privacy_try_again',  'src': 'playing_vt_settings_privacy_set_public',  'dst': 'playing_vt_settings_menu'},

    #option - change language
    {'name': 'start_vt_settings_lang',  'src': 'transit_vt_settings_menu',  'dst': 'init_vt_settings_lang'},
    {'name': 'play_vt_settings_langselect',  'src': 'init_vt_settings_lang',  'dst': 'playing_vt_settings_langselect'},
    {'name': 'playcomplete_vt_settings_langselect',  'src': 'playing_vt_settings_langselect',  'dst': 'transit_playcomplete_vt_settings_langselect'},
    {'name': 'play_vt_settings_langset',  'src': 'transit_playcomplete_vt_settings_langselect',  'dst': 'playing_vt_settings_langset'},
    {'name': 'play_vt_settings_langselect_try_again',  'src': 'transit_playcomplete_vt_settings_langselect',  'dst': 'playing_vt_settings_langselect_try_again'},

    {'name': 'playcomplete_vt_settings_langset',  'src': 'playing_vt_settings_langset',  'dst': 'playing_vt_settings_menu'},
    {'name': 'playcomplete_vt_settings_langselect_try_again',  'src': 'playing_vt_settings_langselect_try_again',  'dst': 'playing_vt_settings_menu'},

  ],

  'callbacks': {

    'oninit_vt_settings_menu':  oninit_vt_settings_menu,
    'ontransit_vt_settings_menu':  ontransit_vt_settings_menu,
    'oninit_vt_settings_owntweet':  oninit_vt_settings_owntweet,
    'onplaying_vt_settings_langselect':  onplaying_vt_settings_langselect,
    'onplaying_vt_settings_langselect_try_again':  onplaying_vt_settings_langselect_try_again,
    'onplaying_vt_settings_langset':  onplaying_vt_settings_langset,
    'onplaying_vt_settings_menu':  onplaying_vt_settings_menu,
    'onplaying_vt_settings_try_again':  onplaying_vt_settings_try_again,

    'onplaying_vt_settings_owntweet':  onplaying_vt_settings_owntweet,
    'onplaying_vt_settings_owntweet_intro':  onplaying_vt_settings_owntweet_intro,
    'onplaying_vt_settings_owntweet_nomore':  onplaying_vt_settings_owntweet_nomore,
    'onplaying_vt_settings_owntweet_notweets':  onplaying_vt_settings_owntweet_notweets,

    'onvt_settings_owntweet_sharing':  onvt_settings_owntweet_sharing,
    'onplaying_vt_settings_owntweet_shared':  onplaying_vt_settings_owntweet_shared,

    'onplaying_vt_settings_owntweet_tag_updated':  onplaying_vt_settings_owntweet_tag_updated,
    'onplaying_vt_settings_owntweet_update_tag_menu':  onplaying_vt_settings_owntweet_update_tag_menu,
    'onplaying_vt_settings_owntweet_update_tag_later':  onplaying_vt_settings_owntweet_update_tag_later,

    'oninit_vt_settings_name':  oninit_vt_settings_name,
    'onplaying_vt_settings_name':  onplaying_vt_settings_name,
    'onplaying_vt_settings_name_beep':  onplaying_vt_settings_name_beep,
    'onplaying_vt_settings_name_notfound':  onplaying_vt_settings_name_notfound,
    'onplaying_vt_settings_name_rerecord':  onplaying_vt_settings_name_rerecord,
    'onplaying_vt_settings_name_rerecord_intro':  onplaying_vt_settings_name_rerecord_intro,
    'onvt_settings_record_name':  onvt_settings_record_name,
    'onplaying_vt_settings_name_set':  onplaying_vt_settings_name_set,
    'ontransit_playcomplete_vt_settings_name_rerecord':  ontransit_playcomplete_vt_settings_name_rerecord,
    'ontransit_recordcomplete_vt_settings_record_name':  ontransit_recordcomplete_vt_settings_record_name,

    'oninit_vt_settings_privacy':  oninit_vt_settings_privacy,
    'onplaying_vt_settings_privacy_2_private':  onplaying_vt_settings_privacy_2_private,
    'onplaying_vt_settings_privacy_2_public':  onplaying_vt_settings_privacy_2_public,
    'onplaying_vt_settings_privacy_set_private':  onplaying_vt_settings_privacy_set_private,
    'onplaying_vt_settings_privacy_set_public':  onplaying_vt_settings_privacy_set_public,

    'onplaying_vt_settings_owntweet_delete':  onplaying_vt_settings_owntweet_delete,
    'onplaying_vt_settings_owntweet_deleted':  onplaying_vt_settings_owntweet_deleted,
    'onplaying_vt_settings_owntweet_delete_later':  onplaying_vt_settings_owntweet_delete_later,

    'oninit_vt_settings_lang':  oninit_vt_settings_lang,
    'ontransit_playcomplete_vt_settings_langselect':  ontransit_playcomplete_vt_settings_langselect,
    'ontransit_playcomplete_vt_settings_owntweet':  ontransit_playcomplete_vt_settings_owntweet,
    'ontransit_playcomplete_vt_settings_owntweet_delete':  ontransit_playcomplete_vt_settings_owntweet_delete,
    'ontransit_playcomplete_vt_settings_owntweet_update_tag':  ontransit_playcomplete_vt_settings_owntweet_update_tag,

    'oncompleted_vt_settings':  oncompleted_vt_settings,

    'onplaying_thankyou':   onplaying_thankyou,
    'onreleasecall':   onreleasecall,
  }
}

