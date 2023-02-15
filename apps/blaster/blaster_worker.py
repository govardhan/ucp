# -*- coding: utf-8 -*-
import sys, os.path
import logging
import time
import threading 
from datetime import datetime
import urllib
import urllib2

sys.path.append("../")
sys.path.append(".")

from dbpool import DBPool
from uv_decorators import *
from config import UVConfig
from cache_server import UVCache

logger = logging.getLogger('blaster_app')
cdr_logger = logging.getLogger('blaster_cdr')

def toHex(s):
  lst = []
  for ch in s:
    hv = hex(ord(ch)).replace('x', '')
    if len(hv) == 1:
      hv = '000'+hv
    elif len(hv) == 2:
      hv = '00'+hv
    elif len(hv) == 3:
      hv = '0'+hv

    lst.append(hv)
  return reduce(lambda x,y:x+y, lst)


class BlasterWorker(threading.Thread):
  
  def __init__(self,id,uuid,filename,smstext,sender,userid,userweight,smstype,sendername,user):
    threading.Thread.__init__(self)

    #Add common params used for http sending sms
    UCPHOME=os.environ['UCPHOME']
    UVConfig().init(UCPHOME+"conf/ucp.conf")
    self.url = UVConfig().get_config_value("blaster","url")
    self.username = UVConfig().get_config_value("blaster","username")
    self.password = UVConfig().get_config_value("blaster","password")
    self.update_stats_freq = int(UVConfig().get_config_value("blaster","update_stats_freq"))
    self.smsrate = int(UVConfig().get_config_value("blaster","smsrate"))
    self.db_name = UVConfig().get_config_value("database","db_name.web") 
    logger.info("url {0} username {1} password {2} db_name {3}".format(self.url, self.username, self.password, self.db_name))

    self.id = id
    self.uuid = uuid
    self.filename = filename  
    self.smstext = smstext
    self.sender = sender
    self.userid = userid
    self.userweight = int(userweight)
    self.smstype = smstype
    self.sendername = sendername
    self.user = user
    logger.info("campaign kickstart id {0} uuid {1} filename {2} sender {3} userid {4} userweight {5} smstype {6}".format(id, uuid, filename, sender, userid, userweight, smstype))
    logger.info("sms text {0}".format(smstext.encode('utf-8')))

  def run(self):
    self.update_stats_onstart()
    self.send_sms()
    self.update_stats_oncomplete()
    self.clear_stats()

  def update_stats_onstart(self):
    UVCache().lpush(self.userid,self.uuid)
    UVCache().hset(self.uuid,"started_ts",str(datetime.now()))
    UVCache().hset(self.uuid,"status","RUNNING")
    UVCache().hset(self.uuid,"delivered",0)
    UVCache().hset(self.uuid,"failed",0)
    UVCache().hset(self.uuid,"processed",0)
    logger.info("{0} Reset stats. Set campain to RUNNING state".format(self.uuid))
    UVCache().incr("activecampaigns")   
    UVCache().incr("totalweight",self.userweight)
#  def stats_refresh(self): - Removed for using

  def update_stats_oncomplete(self):
    UVCache().hset(self.uuid,"status","COMPLETED")
    l_status = UVCache().hget(self.uuid,"status")
    l_delivered = UVCache().hget(self.uuid,"delivered")
    l_failures = UVCache().hget(self.uuid,"failed")
    l_processed = UVCache().hget(self.uuid,"processed")
    UVCache().hset(self.uuid,"completed_ts",str(datetime.now()))
    DBPool().execute_query("update blaster_campaign set status='{0}',completed_ts=now(),processed_volume={1},failures={2} where uuid = '{3}'".format(l_status,l_processed,l_failures, self.uuid),self.db_name)    
    logger.info("{0} Campaign completed. delivered {1} failed {2} processed {3} completed_ts {4}".format(self.uuid,l_delivered, l_failures, l_processed,str(datetime.now()) ))
  def update_stats_onpause(self):
    pass

  def update_stats_onresume(self):
    pass

  def send_sms(self):
    filemsisdn = open(self.filename,'r')
    counter = 0
    elapsedtime = 0
    type = 0 
    try:
      self.smstext.decode('ascii')
      if( self.smstype == "FLASH" ):
        type = 1
    except:
      type = 2 
      self.smstext = toHex(self.smstext)
      if( self.smstype == "FLASH" ):
        type = 6

    for msisdn in filemsisdn:
      msisdn=msisdn.strip()
      activecampaigns = int(UVCache().get("activecampaigns"))
      totalweight = int(UVCache().get("totalweight"))
#      waittime = (1.0/float(self.smsrate))*activecampaigns
      waittime = totalweight/(30*float(self.userweight))
      logger.debug("{0} activecampaigns {1}, smsrate {2}, waittime {3} elapsedtime {4}".format(self.uuid, activecampaigns, self.smsrate, waittime, elapsedtime))
      if( elapsedtime < waittime ):
        time.sleep(waittime - elapsedtime)
      to = time.time()

      params = urllib.urlencode({'username':self.username,'password':self.password,'type':type,'dlr':'0','source':self.sender,'destination':msisdn,'message':self.smstext})
      fullurl = self.url + "?" + params
      logger.info("{0} fullurl {1}".format(self.uuid, fullurl))
      try:
        #params - second arg in urllib2.urlopen() make POST reuest 
        #response = urllib2.urlopen(self.url,params)
        response = urllib2.urlopen(fullurl)
      except urllib2.URLError, e:
        UVCache().hincrby(self.uuid,"failed")
        logger.warn("{0} SMS to {1} failed to send. url {2}".format(self.uuid, msisdn , self.url ))
        cdr_logger.info("\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\thttp error".format(self.user,self.sendername,self.uuid,self.smstype,str(datetime.now()),msisdn ))
      else:
        responsebody = response.read()
        logger.debug("{0} HTTP response body {1}".format(self.uuid, responsebody))
        #if response body logic
        responsebodylog = responsebody.replace("|","\t")
        cdr_logger.info("\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(self.user,self.sendername,self.uuid,self.smstype,str(datetime.now()),msisdn,responsebodylog ))
        UVCache().hincrby(self.uuid,"delivered")
        logger.debug("{0} SMS delivered to {1}".format(self.uuid, msisdn))

      UVCache().hincrby(self.uuid,"processed")
      counter += 1
      if( counter % self.update_stats_freq == 0):
        self.save_stats()
      elapsedtime = time.time() - to
    logger.info("{0} campaign completed. {1} iterations. ".format(self.uuid, counter)) 
	
  def clear_stats(self):
    UVCache().hdel(self.uuid,"started_ts")
    UVCache().hdel(self.uuid,"status")
    UVCache().hdel(self.uuid,"delivered")
    UVCache().hdel(self.uuid,"failed")
    UVCache().hdel(self.uuid,"processed")
    UVCache().hdel(self.uuid,"update_ts")
    UVCache().hdel(self.uuid,"completed_ts")     
    UVCache().lrem(self.userid,self.uuid)
    UVCache().decr("activecampaigns")
    UVCache().decr("totalweight",self.userweight)
  
  def save_stats(self):
    l_status = UVCache().hget(self.uuid,"status")
    UVCache().hset(self.uuid,"update_ts",str(datetime.now()))
    l_processed = UVCache().hget(self.uuid,"processed")
    l_delivered = UVCache().hget(self.uuid,"delivered")
    l_failures = UVCache().hget(self.uuid,"failed")
    DBPool().execute_query("update blaster_campaign set status='{0}',update_ts=now(),processed_volume={1},failures={2} where uuid = '{3}'".format(l_status,l_processed,l_failures, self.uuid),self.db_name)    
    logger.info("{0} updating campaign stats. status {1} update_ts {2} processed {3} delivered {4} failed {5}".format(self.uuid, l_status, str(datetime.now()), l_processed, l_delivered, l_failures ))
