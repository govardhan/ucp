# -*- coding: utf-8 -*-
import os,sys
import logging.config
from datetime import datetime
lib_path = os.path.abspath('../../ucp/core')
sys.path.append(lib_path)
lib_path = os.path.abspath('../../conf')
sys.path.append(lib_path)
from config import UVConfig
import pika
from producer import *
from cache_server import UVCache
import urllib
import urllib2
from processBilling import processbilling

class plugin(processbilling):
  def __init__(self):
    self.init()

  def init(self):
    processbilling.init(self)

  def billlingRequest(self):
   try:
     self.channel.basic_consume(self.callback,queue='billing') 
     self.channel.start_consuming()
     self.logger.info("Ready to Process Billing request . . .")
   except:
     self.logger.info("ERROR in receivng Billing request . . .")
  
  # sample operator specfic plugin
  def callback(self,ch, method, properties, body):
    paramdict = eval(body)
    self.logger.info("Operator Specific Plugin")
    parameter = urllib.urlencode({'username':paramdict['username'],'password':paramdict['password'],'from':paramdict['source'],'to':paramdict['destination'],'sid':paramdict['chargekey'],'action':paramdict['action']})
    fullurl = paramdict['url'] + "?" + parameter
    try:
      response = urllib2.urlopen(fullurl)
      responsebody = response.read()
      self.logger.info("Billing Request send to Operator - {0}".format(fullurl))
      self.logger.info("Billing Response - {0}".format(responsebody))    
      try:
        callback = {}
        if(responsebody == '1702'):
          callback['code'] = responsebody
          callback['status'] = "success"
        else:
          callback['code'] = responsebody
          callback['status'] = "failure"
        callbackstr = str(callback)
        self.logger.info("Response - {0}".format(callbackstr))
        self.channelCallback.basic_publish(exchange='callback',routing_key='callbacklocal',body=callbackstr,properties=pika.BasicProperties(delivery_mode = 2,))
        self.logger.info("Response is sent to callback excahange")
      except:
        self.logger.info("ERROR - Sending response back to billing response queue")

      ch.basic_ack(delivery_tag = method.delivery_tag)
      
    except urllib2.URLError, e:
      self.logger.info("ERROR in sending billing request - {0}".format(fullurl))

pluginInstance = plugin()
pluginInstance.billlingRequest()
