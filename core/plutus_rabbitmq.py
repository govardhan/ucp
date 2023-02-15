import os
import sys
import codecs
import traceback

import pika

lib_path = os.path.abspath('../../ucp/core')
sys.path.append(lib_path)
lib_path = os.path.abspath('../../conf')
sys.path.append(lib_path)

from uv_decorators import *
from config import UVConfig
import logging

#@singleton
class UVRabbitMQSetup:
  def __init__(self):
    self.init()

  def init(self):
    try:
      UCPHOME=os.environ['UCPHOME']
    except:
      UCPHOME="/home/uvadmin/ucp/"

    logging.config.fileConfig(UCPHOME+'conf/logging.conf')
    self.logger = logging.getLogger('ucp_core')

    self.logger.info("UCPHOME - {0}".format(UCPHOME))
   
    #TODO support operator wise configuration 
    UVConfig().init(UCPHOME+"conf/ucp.conf") 
    self.smsusername = UVConfig().get_config_value("notification","username") 
    self.smspassword = UVConfig().get_config_value("notification","password")
    self.smsurl = UVConfig().get_config_value("notification","smsurl")
    self.suburl = UVConfig().get_config_value("billing","suburl")
    self.unsuburl = UVConfig().get_config_value("billing","unsuburl")
    self.renurl = UVConfig().get_config_value("billing","renurl")
    self.billingusername = UVConfig().get_config_value("billing","username")
    self.billingpassword = UVConfig().get_config_value("billing","password")

    if (False == self.setup_rabbitmq_for_postbox()):
      return False

    if(False == self.setup_rabbitmq_for_plutus()):
      return False

    if(False == self.setup_rabbitmq_for_plutus_callback()):
      return False

    return True
    
  def setup_rabbitmq_for_postbox(self):
    try:
      self.pb_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
      self.logger.info("Connected to RabbitMQ server for SMS communication : {0}".format(self.pb_connection))   

      self.pb_channel = self.connection.channel()
      self.logger.info("RabbitMQ channel established for SMS communication : {0}".format(self.pb_channel))

      self.pb_channel.exchange_declare(exchange='sms',exchange_type='direct') 
      self.logger.info("SMS direct exchange established")
      return True

    except:
      self.logger.error("unable to establish connection or exchange for postbox. exception trace {0}".format(traceback.print_exc()))
      return False

  def setup_rabbitmq_for_plutus(self):
    try:
      self.plutus_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
      self.logger.info("Connected to RabbitMQ server for subscription communication : {0}".format(self.plutus_connection))   

      self.plutus_channel = self.connection.channel()
      self.logger.info("RabbitMQ channel established for subscription communication : {0}".format(self.plutus_channel))

      self.plutus_channel.exchange_declare(exchange='subscription',exchange_type='direct') 
      self.logger.info("subscription direct exchange established")
      return True

    except:
      self.logger.error("unable to establish connection or exchange for plutus. exception trace {0}".format(traceback.print_exc()))
      return False
   
  def setup_rabbitmq_for_plutus_callback(self):
    try:
      self.plutus_cb_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
      self.logger.info("Connected to RabbitMQ server for plutus callback processing : {0}".format(self.plutus_cb_connection))   

      self.plutus_cb_channel = self.plutus_cb_connection.channel()
      self.logger.info("RabbitMQ channel established for plutus callback processing : {0}".format(self.plutus_cb_channel))   

      self.plutus_cb_channel.exchange_declare(exchange='callback',exchange_type='direct')
      self.logger.info("RabbitMQ exchange established for plutus callback processing")   

      self.plutus_cb_channel.queue_declare(queue='billingresponse',durable=True)
      self.logger.info("RabbitMQ billingresponse queue established for plutus callback processing")   

      self.plutus_cb_channel.queue_bind(exchange='callback',queue='billingresponse',routing_key='callbacklocal')
      self.logger.info("RabbitMQ billingresponse queue binded to callback exchange for plutus callback processing")   
      return True

    except:
      self.logger.error("unable to establish connection or queue or exchange for plutus callback. exception trace {0}".format(traceback.print_exc()))
      return False

     
  def __del__(self):
    try:
      self.pb_connection.close()
      self.logger.info("closed postbox rabbitmq connections")
    except:
      self.logger.error("unable to close postbox rabbitmq connections")
      return False

    try:
      self.plutus_connection.close()
      self.logger.info("closed plutus rabbitmq connections")

      self.plutus_cb_connection.close()
      self.logger.info("closed plutus callback rabbitmq connections")
    except:
      self.logger.error("unable to close plutus or plutus callback rabbitmq connections")
      return False

    return True
