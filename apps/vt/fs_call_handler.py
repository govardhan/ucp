#!/usr/bin/env twistd --pidfile=server.pid -ny
# using:
#  1. register your sip client as 1000 in the freeswitch server
#  2. run this server (twistd --pidfile=server.pid -ny server.py)
#  3. open the freeswitch console and place a call to 1000 using
#     this server as context:
#     originate sofia/internal/1000%127.0.0.1 '&socket(127.0.0.1:8888 async full)'

#Setup application home path

# -*- coding: UTF-8 -*-

import sys, os.path
try:
  UCPHOME=os.environ['UCPHOME']
except:
  UCPHOME="/home/uvadmin/ucp/"
  print "UCPHOME set to /home/uvadmin/ucp/"

sys.path.append(UCPHOME+"core")
sys.path.append(UCPHOME+"apps/vt/")
sys.path.append(UCPHOME+"apps/postbox/")

import eventsocket
from twisted.internet import defer, protocol
from twisted.application import service, internet
from twisted.python import log

from genutils import *
from cache_server import UVCache
from config import UVConfig
from number_normalize import UVNormalizer
from number_telco_resolution import UVNumberTelcoResolution
from feature_profile import *
from user_profile import UVUserProfile
from telco_profile import UVTelcoProfile
from cdr import CDR

from fysom import Fysom
import ivr_root_fsm_states

##Setup application logging
#logging.config.fileConfig(UCPHOME+'conf/vt_logging.conf')
#logger = logging.getLogger('vt_app')

#observer = log.PythonLoggingObserver()
#observer.start()

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
    self.parent_fsm = None
    self.parent_fsm_resume_event = None
    self.calldisconnected = False
    #print "data is:", l_calldata
    logger.info("new incoming call src={0}, dst={1}, uuid={2}".format(self.raw_src_num, self.raw_dst_num, self.uuid) )

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
    logger.debug("{0} received dtmf digit {1}".format(self.uuid, ev.DTMF_Digit) )

  def onChannelExecuteComplete(self, ev):
    if (self.calldisconnected):
      logger.warn("{0} event {1} after call disconnection. Ignoring".format(self.uuid, ev.variable_current_application))
      return

    if ev.variable_current_application == "answer":
      logger.debug("call has been answered {0}".format(self.uuid))
    elif ev.variable_current_application == "playback":
      l_event_name = "playcomplete_" + self.curr_prompt_name
      logger.debug("{0} received fs event {1}".format(self.uuid, l_event_name) )
      getattr(self.current_fsm, l_event_name)(uuid=self.uuid, call_instance = self)
    elif ev.variable_current_application == "play_and_get_digits":
      l_event_name = "playcomplete_" + self.curr_prompt_name
      #logger.debug("event data {0}".format(ev) )
      l_dtmf = ''
      l_reason = 'playcomplete'
      if(ev.has_key('variable_user_dtmf')):
        l_reason = 'digit_abort'
        l_dtmf=ev.variable_user_dtmf
      logger.debug("{0} play_and_get_digits event {1} reason {2} dtmf {3}".format(self.uuid, l_event_name, l_reason, l_dtmf))
        
      getattr(self.current_fsm, l_event_name)(uuid=self.uuid, reason = l_reason, dtmf = l_dtmf, call_instance = self)
    elif ev.variable_current_application == "set":
      logger.debug("channel variable set event {0}".format(ev.variable_current_application_data))
    elif ev.variable_current_application == "record":
      l_rec_duration = ev.variable_record_seconds
      l_rec_file = ev.Application_Data
      try:
        l_dtmf = ev.variable_user_dtmf
      except AttributeError:
        l_dtmf = ""
        logger.debug("recordcomplete uuid {0} no DTMF detected".format(self.uuid))
        
      l_event_name = "recordcomplete_" + self.curr_prompt_name
      logger.debug("recordcomplete uuid {0} file {1} duration {2} dtmf {3}".format(self.uuid, l_rec_file, l_rec_duration, l_dtmf))
      getattr(self.current_fsm, l_event_name)(uuid=self.uuid, rec_duration = l_rec_duration, rec_file = l_rec_file, dtmf = l_dtmf, call_instance = self)
    else:
      logger.warn("{0} unhandled event {1}".format(self.uuid, ev.variable_current_application))
      logger.debug("event data {0}".format(ev) )

  def onChannelHangup(self, ev):
    start_usec = float(ev.Caller_Channel_Answered_Time)
    end_usec = float(ev.Event_Date_Timestamp)
    duration = (end_usec - start_usec) / 1000000.0
    logger.info(" %s  %s hung up: %s (call duration: %0.2f)" % (ev.Caller_Unique_ID, ev.variable_presence_id, ev.Hangup_Cause, duration))
    self.calldisconnected = True
    self.current_fsm.calldisconnect(uuid=self.uuid, callduration=duration, call_instance = self)

  # To avoid 'unbound Event' messages in the log, you may
  # define the unboundEvent() method in your class:
  def unboundEvent(self, evdata, evname):
    logger.debug("************** {0} unbound Event: {0} {1}".format(evdata["Caller_Unique_ID"], evname, evdata["variable_current_application"]) )
 

class IVRCallFactory(protocol.ServerFactory):
  """our server factory"""
  protocol = IVRCall

##Here is application main function logic starts
#logger.info("Starting voicetweet application")
#conf = UVConfig()
#conf.init(UCPHOME+"conf/ucp.conf")
#logger.info("configuration initialization done")
#UVCache().set("UCPHOME", UCPHOME)
#logger.info("Starting application")
#application = service.Application("call_manager")
#port = int(UVConfig().get_config_value("vt","fs_evt_sock_port"))
#internet.TCPServer(port, IVRCallFactory(), interface="0.0.0.0").setServiceParent(application)
