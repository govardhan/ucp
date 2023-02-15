"""
  :mod:`postbox_rabbitmq_setup.py` module will be used by :mod:`postbox_server` and :mod:`postbox_api`
  to setup connection, channel & exchange with RabbitMQ to send SMS notifications

  TODO. document exchange type, name, routing keys

"""
import os
import sys
import codecs
import traceback
import logging
from inspect import isfunction

import pika

from uv_decorators import *
from config import UVConfig

"""
  core & postbox logger initilization
"""
logger = logging.getLogger('ucp_core')

@singleton
class PostBoxRabbitMQ(object):
  """
    PostBoxRabbitMQ class is :class:`singleton`. This class establishes connection to rabbitmq-server, 
    channel & define exchange name and type.
  """
  def __init__(self):
    self.initialized = False
    self.init()

  def init(self):
    """initialization

      reads configuration parameters - rabbitmq_server, exchange_name, exchange_type
      create connection, channel and exchange.
      returns True if the initialization success. Throws exception, write excepton data in log
      and return False if the initialization fails.
    """
    try:
      self.rabbitmq_server = UVConfig().get_config_value("platform","rabbitmq_server")
      self.exchange_name = UVConfig().get_config_value("postbox", "rabbitmq_exchange_name")
      self.exchange_type = UVConfig().get_config_value("postbox", "rabbitmq_exchange_type")
      logger_info("rabbitmq_server {0}, rabbitmq_exchange_name {1}, rabbitmq_exchange_type {2}".format(self.rabbitmq_server, self.exchange_name, self.exchange_type))

      self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_server))
      logger.info("Connected to RabbitMQ server for postbox: {0}".format(self.connection))   

      self.channel = self.connection.channel()
      logger.info("RabbitMQ channel established for postbox: {0}".format(self.channel))

      self.channel.exchange_declare(exchange = self.exchange_name,exchange_type = self.exchange_type) 
      logger.info("postbox exchange has been established")
      self.initialized = True
      return True

    except:
      logger.error("unable to establish connection or exchange for postbox. exception trace {0}".format(traceback.print_exc()))
      return False

  def create_or_get_queue(queue_name = "", durable = False):
    """create_or_get_queue declare rabbit mq queue if not exists
       By default durable is False.
    """
    try:
      l_result = self.channel.queue_declare(queue = queue_name, durable=True)
      return l_result.method.queue
    except:
      logger.error("unable to create or get queue {0}. exception trace {1}".format(queue_name, traceback.print_exc()))
      return None

  def bind_queue_to_exchange(exchange_name, queue_name, routing_key):
    """bind_queue_to_exchange bins queue to an exchange. 
    """
    try:
      self.channel.queue_bind(exchange = exchange_name, queue = queue_name, routing_key = routing_key)
      return True
    except:
      logger.error("unable to bind queue {0} to an exchange {1} using routing key {2}. exception trace {1}".format(queue_name, exchange_name, routing_key, traceback.print_exc()))
      return False

  def register_callback(callback_fun, queue_name = "", no_ack = False, exclusive = False):
    """register_callback consumer use this API to register to consume messages from the queue
    """
    if( False == isfunction(callback_fun) ):
      logger.error("unable to register. callback_fun {0} parameter is not the function".format(callback_fun))
      return False
    try:
      self.channel.basic_consume(callback_fun, queue = queue_name, no_ack = no_ack, exclusive = exclusive)
      return True
    except:
      logger.error("unable to register callback_fun bind queue {0} to an exchange {1} using routing key {2}. exception trace {1}".format(queue_name, exchange_name, routing_key, traceback.print_exc()))
      return False
  
  def is_initialized(self):
    return self.initialized

  def get_connection(self):
    if(True == self.initialized):
      return self.connection
    else:
      return None

  def get_channel(self):
    if(True == self.initialized):
      return self.channel
    else:
      return None

  def sendsms(p_uuid, p_sender_name, p_telco_id, p_sms, p_to):
    """ sendsms method frames payload and push into rabbit mq
    """
    l_mq_payload = {}
    l_mq_payload['uuid'] = p_uuid
    l_mq_payload['from'] = p_sender_name
    l_mq_payload['to'] = p_to
    l_mq_payload['telco_id'] = p_telco_id
    l_mq_payload['sms'] = p_sms
    l_mq_msg = str(l_mq_payload)
    try:
      self.channel.basic_publish(exchange = self.exchange_name, routing_key = p_telco_id, body = l_mq_msg, properties = pika.BasicProperties(delivery_mode = 2,))       
      logger.info("{0} SMS has been pushed to queue".format(p_uuid))
    except:
      logger.error("{0} unable to push SMS to queue. trace {1}".format(p_uuid, traceback.print_exc()))
      return False
    return True

    
  def __del__(self):
    """ Cleanup connection
    """
    try:
      self.pb_connection.close()
      logger.info("closed postbox rabbitmq connections")
    except:
      logger.error("unable to close postbox rabbitmq connections")
      return False
    return True
