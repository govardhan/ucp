# -*- coding: utf-8 -*-
import sys, os
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

class processbilling:
  def __init__(self):
    self.init()
  
  def init(self):
    try:
      UCPHOME=os.environ['UCPHOME']
    except:
      UCPHOME="/home/uvadmin/ucp/"

    logging.config.fileConfig(UCPHOME+'conf/logging.conf')
    self.logger = logging.getLogger('uvbilling.blaster')
    self.logger.info("UCPHOME - {0}".format(UCPHOME))

    try:
      self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
      self.channel = self.connection.channel()
      self.channel.exchange_declare(exchange='subscription',type='direct')
      self.channel.queue_declare(queue='billing',durable=True) 
      self.channel.queue_bind(exchange='subscription',queue='billing',routing_key='billinglocal')

      self.logger.info("RabbitMQ Connection Established for consuming Billing messages")
      self.logger.info("RabbitMQ Channel Established for consuming Billing messages")
      self.logger.info("Queue connected to Exchange : billing")
    except:
      self.logger.info("ERROR - RabbitMQ queue not established. Check if RabbitMQ is running")    

    try:
      self.connectionCallback = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
      self.channelCallback = self.connectionCallback.channel()
      self.channelCallback.exchange_declare(exchange='callback',exchange_type='direct')

      self.logger.info("Connection to RabbitMQ server Established for billing callback communication : {0}".format(self.connectionCallback))
      self.logger.info("RabbitMQ Channel established for billing callback communication : {0}".format(self.channelCallback))
      self.logger.info("Callback Exchange established ")

    except:
      self.logger.info("ERROR in establishing RabbitMQ connection for callback")

	
  def callback(self,ch, method, properties, body):
    paramdict = eval(body)
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

