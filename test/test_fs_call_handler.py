#!/usr/bin/env twistd --pidfile=server.pid -ny
# coding: utf-8
# using:
#  1. register your sip client as 1000 in the freeswitch server
#  2. run this server (twistd --pidfile=server.pid -ny server.py)
#  3. open the freeswitch console and place a call to 1000 using
#     this server as context:
#     originate sofia/internal/1000%127.0.0.1 '&socket(127.0.0.1:8888 async full)'

import sys, os.path
sys.path.append("../")

import eventsocket
from twisted.internet import defer, protocol
from twisted.application import service, internet

from genutils import *
from cache_server import UVCache
from config import UVConfig
from number_normalize import UVNormalizer
from number_telco_resolution import UVNumberTelcoResolution
from service_finder import *
from user_profile import UVUserProfileHandler
from telco_profile import UVTelcoProfile
from cdr import CDR

from fysom import Fysom
import ivr_root_fsm_states

class IVRCall(eventsocket.EventProtocol):
  """our protocol class for receiving calls"""

  @defer.inlineCallbacks
  def connectionMade(self):
    # Once the call is originated, the freeswitch will connect
    # to our service and a new MyProtocol instance is created.
    #
    # Please refer to http://wiki.freeswitch.org/wiki/Event_Socket_Outbound
    # for more information.
    #
    # Anyway, the first thing to do when receiving such connections
    # from the freeswitch, is to send the `connect` command. We do this by
    # calling self.connect().
    l_calldata = yield self.connect()
    self.uuid = l_calldata['Caller_Unique_ID']
    self.raw_src_num = l_calldata['Channel_Username']
    self.raw_dst_num= l_calldata['Caller_Destination_Number']
    self.current_fsm = Fysom(ivr_root_fsm_states.states)
    #print "data is:", l_calldata
    logging.info("new incoming call src={0}, dst={1}, uuid={2}".format(self.raw_src_num, self.raw_dst_num, self.uuid) )

    # After the connection with the eventsocket is established, we may
    # inform the server about what type of events we want to receive.
    # Use either self.eventplain("LIST_OF EVENT_NAMES") or self.myevents().
    # Please refer to http://wiki.freeswitch.org/wiki/Event_Socket_Outbound#Events
    # for more information.
    yield self.myevents()

    # The next step is to `answer` the call. This is done by calling
    # self.answer(). After answering the call, our service will begin
    # receiving events from the freeswitch. 
    yield self.answer()

    self.current_fsm.incall(uuid=self.uuid, raw_src_num=self.raw_src_num, raw_dst_num=self.raw_dst_num, call_instance = self)

  def onDtmf(self, ev):
    # for k, v in sorted(ev.items()):
    #   print k, "=", v
    logging.debug("{0} received dtmf digit {1}".format(self.uuid, ev.DTMF_Digit) )

  def onChannelExecuteComplete(self, ev):
    if ev.variable_current_application == "answer":
      logging.debug("call has been answered {0}".format(self.uuid))
    elif ev.variable_current_application == "playback":
      l_event_name = "playcomplete_" + self.curr_prompt_name
      logging.debug("{0} received fs event {1}".format(self.uuid, l_event_name) )
      getattr(self.current_fsm, l_event_name)(uuid=self.uuid, call_instance = self)
    elif ev.variable_current_application == "play_and_get_digits":
      l_event_name = "playcomplete_" + self.curr_prompt_name
      #logging.debug("event data {0}".format(ev) )
      l_dtmf = ''
      l_reason = 'playcomplete'
      if(ev.has_key('variable_user_dtmf')):
        l_reason = 'digit_abort'
        l_dtmf=ev.variable_user_dtmf
      logging.debug("{0} play_and_get_digits event {1} reason {2} dtmf {3}".format(self.uuid, l_event_name, l_reason, l_dtmf))
        
      getattr(self.current_fsm, l_event_name)(uuid=self.uuid, reason = l_reason, dtmf = l_dtmf, call_instance = self)
    elif ev.variable_current_application == "set":
      logging.debug("channel variable set event {0}".format(ev.variable_current_application_data))
    else:
      logging.warn("{0} unhandled event {1}".format(self.uuid, ev.variable_current_application))
      logging.debug("event data {0}".format(ev) )

  def onChannelHangup(self, ev):
    start_usec = float(ev.Caller_Channel_Answered_Time)
    end_usec = float(ev.Event_Date_Timestamp)
    duration = (end_usec - start_usec) / 1000000.0
    print "%s hung up: %s (call duration: %0.2f)" % \
        (ev.variable_presence_id, ev.Hangup_Cause, duration)

  # To avoid 'unbound Event' messages in the log, you may
  # define the unboundEvent() method in your class:
  def unboundEvent(self, evdata, evname):
    pass
  #
  # This is the original method in eventsocket.py:
  #def unboundEvent(self, evdata, evname):
  #  logging.warn("[eventsocket] unbound Event: {0}".format(evname) )
 

class IVRCallFactory(protocol.ServerFactory):
  """our server factory"""
  protocol = IVRCall

init_logging("voiceapp.log")
conf = UVConfig()
conf.init("/root/ucp/ucp/conf/ucp.conf")

logging.info("Starting application")
application = service.Application("call_manager")
internet.TCPServer(8040, IVRCallFactory(), interface="127.0.0.1").setServiceParent(application)
