#!/usr/bin/env python

import logging
import redis

from genutils import *
from uv_decorators import *
from cache_server import UVCache
from config import UVConfig

@singleton
class UVStatsServer:
  def update_stats_on_newcall(self):
    UVCache().incr( UVConfig().get_config_value("stats","active_incoming_call_counter") )

    UVCache().incr( UVConfig().get_config_value("stats","incoming_call_counter") )

    l_active_incoming_call_counter = int(UVCache().get( UVConfig().get_config_value("stats","active_incoming_call_counter") ))
    l_max_active_incoming_calls = UVCache().get( UVConfig().get_config_value("stats","max_active_incoming_calls") )
    l_max_active_incoming_calls = int(0 if l_max_active_incoming_calls is None else l_max_active_incoming_calls)

    if( l_active_incoming_call_counter >  l_max_active_incoming_calls):
      UVCache().set( UVConfig().get_config_value("stats","max_active_incoming_calls"), l_active_incoming_call_counter )


  def update_stats_on_callrelease(self):
    UVCache().decr( UVConfig().get_config_value("stats","active_incoming_call_counter") )

  def update_stats_on_newuser(self, telcoid, channel):
    l_new_user_key = telcoid + "." + channel + "." + "new_user_count"
    UVCache().incr( UVConfig().get_config_value("stats", l_new_user_key) )
    
#implement timer functionality
#flush stats in to databae & reset at regular interval - 5 mins, hourly & daily basis
