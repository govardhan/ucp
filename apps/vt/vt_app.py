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
from fs_call_handlerimport import IVRCallFactory
from fs_call_handlerimport import IVRCall

#Setup application logging
logging.config.fileConfig(UCPHOME+'conf/vt_logging.conf')
logger = logging.getLogger('vt_app')

observer = log.PythonLoggingObserver()
observer.start()

#Here is application main function logic starts
logger.info("Starting voicetweet application")
conf = UVConfig()
conf.init(UCPHOME+"conf/ucp.conf")
logger.info("configuration initialization done")
UVCache().set("UCPHOME", UCPHOME)
logger.info("Starting application")
application = service.Application("call_manager")
port = int(UVConfig().get_config_value("vt","fs_evt_sock_port"))
internet.TCPServer(port, IVRCallFactory(), interface="0.0.0.0").setServiceParent(application)

