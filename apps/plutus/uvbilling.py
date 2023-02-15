# -*- coding: utf-8 -*-
import sys, os
import logging
import logging.config
from datetime import datetime

lib_path = os.path.abspath('../../ucp/core')
sys.path.append(lib_path)
lib_path = os.path.abspath('../../conf')
sys.path.append(lib_path)

from config import UVConfig
import pika
from rmq_setup import *
from cache_server import UVCache
@singleton
class billing(Producer):
  def __init__(self):
    self.init()

  def init(self):
    Producer.init(self)
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    self.logger1.info("DB Used for Billing communication : {0}".format(self.db_name))

  def sub(self,uuid,action="ACT",url=None):
    
    if url is None:
      self.logger1.info("Billing Request - Subscription")
      url = self.suburl
    sub = {}
    sub['username'] = self.billingusername
    sub['password'] = self.billingpassword
    sub['source'] = UVCache().hget(uuid,"source")
    sub['destination'] = UVCache().hget(uuid,"destination")
    sub['chargekey'] = UVCache().hget(uuid,"chargekey")
    sub['action'] = action
    sub['url'] = url
    sub['uuid'] = uuid
    message = str(sub)
    try:
      self.channelSub.basic_publish(exchange='subscription',routing_key='billinglocal',body=message,properties=pika.BasicProperties(delivery_mode = 2,))
      self.logger1.info("Billing Request sent to Queue")
      self.logger1.info("Billing Message : {0}".format(message))
    except:
      self.logger1.info("ERROR - Billing Request not sent to Queue : {0}".format(message))
#    clear redis cache

  def unsub(self,uuid):
    self.logger1.info("Billing Request - UnSubscription")
    self.sub(uuid,"DCT",self.unsuburl)

  def renewal(self,uuid):
    self.logger1.info("Billing Request - Renewal")
    self.sub(uuid,"REN",self.renurl)
 

  
    
