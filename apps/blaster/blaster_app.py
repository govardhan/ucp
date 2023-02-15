# -*- coding: utf-8 -*-

import sys, os
import logging
import logging.config
from datetime import datetime

from twisted.application import service
from twisted.application.internet import TimerService
from twisted.python import log

lib_path = os.path.abspath('../../ucp/core')
sys.path.append(lib_path)
lib_path = os.path.abspath('../../conf')
sys.path.append(lib_path)

from dbpool import DBPool
from uv_decorators import *
from config import UVConfig
from blaster_worker import BlasterWorker

#@singleton
class CampaignWatcher:
  poll_counter = 0
  def __init__(self):
    self.init()

  def reload(self):
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.web")
    
  def campain_poller(self):
    CampaignWatcher.poll_counter += 1
    #rowcount,campaign_record = DBPool().execute_query("select id from app1_campaignstats where status='NEW' and scheduled_ts > now() order by scheduled_ts",self.db_name)
    rowcount,campaign_record = DBPool().execute_query("select id, uuid, msisdnfilename, smstext, sendername, user_id, smstype  from blaster_campaign where status='NEW' and scheduled_ts <= now() order by scheduled_ts",self.db_name)

    if(rowcount):
      logger.info("{0} campaigns ready to schedule ".format(rowcount))
      for l_row in campaign_record:
        #span blaster worker thread
        logging.info("id={0} uuid={1} msisdnfilename={2} smstext={3} sendername={4} user_id={5} smstype={6}".format(l_row['id'], l_row['uuid'], l_row['msisdnfilename'], l_row['smstext'].encode('utf-8'), l_row['sendername'], l_row['user_id'], l_row['smstype']))

        l_rc, l_ur = DBPool().execute_query("select msisdn, creditlimit, creditused, weight, username from blaster_userprofile a,auth_user b where user_id = {0} and a.user_id = b.id".format(int(l_row['user_id'])), self.db_name)
        l_weight = 1
        if(l_rc):
          logging.info("userprofile ({0}) - {1}".format(l_rc, l_ur))
          for l_r in l_ur:
            l_weight = int(l_r['weight'])
            l_username = l_r['username']

        l_worker_thread = BlasterWorker(l_row['id'], l_row['uuid'], l_row['msisdnfilename'], l_row['smstext'], l_row['sendername'], l_row['user_id'], l_weight, l_row['smstype'], l_row['sendername'], l_username)
        l_worker_thread.setDaemon(True)
        l_worker_thread.start()

        DBPool().execute_query("update blaster_campaign set status='RUNNING' where id={0}".format(l_row['id']),self.db_name)
    else:
      if( CampaignWatcher.poll_counter % 10 == 0):
        logger.info("No campaigns avalilable to schedule. poll counter {0}".format(CampaignWatcher.poll_counter))
      else:
        logger.debug("No campaigns avalilable to schedule. poll counter {0}".format(CampaignWatcher.poll_counter))


try:
  UCPHOME=os.environ['UCPHOME']
except:
  UCPHOME="/home/uvadmin"
  print "UCPHOME set to /home/uvadmin"

logging.config.fileConfig(UCPHOME+'conf/logging.conf')
logger = logging.getLogger('blaster_app')

observer = log.PythonLoggingObserver()
observer.start()

logger.info("Starting blaster application")
conf = UVConfig()
conf.init(UCPHOME+"conf/ucp.conf")
logger.info("configuration initialization done")
application = service.Application("blaster")
l_poll_interval = int(UVConfig().get_config_value("blaster","db_poll_interval"))
logger.info("Campaign poll interval {0} secs".format(l_poll_interval))
l_timer_service = TimerService(l_poll_interval,CampaignWatcher().campain_poller)
l_timer_service.setServiceParent(application)
 
