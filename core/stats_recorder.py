#!/usr/bin/env python

import logging
import redis

from genutils import *
from uv_decorators import *
from cache_server import UVCache
from config import UVConfig

logger = logging.getLogger('ucp_core')

@singleton
class UVStatsServer:
  def update_stats_on_newcall(self, telcoid):
    UVCache().incr("active_incoming_call_counter")
    UVCache().incr(telcoid + ".active_incoming_call_counter")

    UVCache().incr("incoming_call_counter" )
    UVCache().incr(telcoid + ".incoming_call_counter" )

    l_active_incoming_call_counter = UVCache().get("active_incoming_call_counter")
    l_max_active_incoming_calls = UVCache().get( "max_active_incoming_calls" )
    l_max_active_incoming_calls = 0 if l_max_active_incoming_calls is None else l_max_active_incoming_calls
    if( l_active_incoming_call_counter >  l_max_active_incoming_calls):
      UVCache().set("max_active_incoming_calls", l_active_incoming_call_counter )

    l_active_incoming_call_counter = UVCache().get(telcoid + ".active_incoming_call_counter") 
    l_active_incoming_call_counter = 0 if l_active_incoming_call_counter is None else l_active_incoming_call_counter

    l_max_active_incoming_calls = UVCache().get(telcoid + ".max_active_incoming_calls" )
    l_max_active_incoming_calls = 0 if l_max_active_incoming_calls is None else l_max_active_incoming_calls
    if( l_active_incoming_call_counter >  l_max_active_incoming_calls):
      UVCache().set(telcoid + ".max_active_incoming_calls", l_active_incoming_call_counter )

  def update_stats_on_callrelease(self, telcoid):
    l_active_incall_counter = telcoid + "." + "active_incoming_call_counter"
    UVCache().decr(l_active_incall_counter)
    UVCache().decr("active_incoming_call_counter")

  def update_stats_on_calldisconnected(self, telcoid):
    l_active_incall_counter = telcoid + "." + "active_incoming_call_counter"
    UVCache().decr(l_active_incall_counter)
    UVCache().decr("active_incoming_call_counter")

  def update_stats_on_newuser(self, telcoid, channel):
    l_new_user_key = telcoid + "." + channel + "." + "new_user_count"
    UVCache().incr( l_new_user_key )
    
  def update_stats_on_newdormantuser(self, telcoid, channel):
    l_new_dormantuser_key = telcoid + "." + channel + "." + "new_dormantuser_count"
    UVCache().incr(l_new_dormantuser_key)
    
#implement timer functionality
#flush stats in to databae & reset at regular interval - 5 mins, hourly & daily basis
