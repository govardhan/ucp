# -*- coding: utf-8 -*-
"""
  postbox_server.py module register with postbox exchange and process
  outgoing SMS notifications
"""

import sys
import os
import logging.config
from datetime import datetime
import traceback
import urllib
import urllib2

try:
  UCPHOME=os.environ['UCPHOME']
except:
  UCPHOME="/home/uvadmin/ucp/"
  print "UCPHOME set to /home/uvadmin/ucp/"

sys.path.append(UCPHOME+"core")
sys.path.append(UCPHOME+"conf")
sys.path.append(UCPHOME+"apps/postbox")

import logging
import logging.config

import pika

from config import UVConfig
from cache_server import UVCache
from postbox_rabbitmq import PostBoxRabbitMQ
from telco_profile import UVTelcos

class PostBoxServer(object):
  def __init__(self, p_routing_key):
    self.set_routing_key(p_routing_key)

    self.init()

  def reload(self):
    self.init()

  def set_routing_key(self, p_route_key):
    self.routing_key = p_route_key
    return True

  def callback(self, ch, method, properties, body):
    logger.info("received message from queue {0}".format(body))
    l_payload = eval(body)
    l_plugin_handler = PostBoxPluginManager().get_postbox_mt_plugin(l_payload['uuid'], l_payload['telco_id'])
    if(l_plugin_handler is None):
      pass
    else:
      l_plugin_handler(l_payload['uuid'], l_payload['from'], l_payload['to'], l_payload['telco_id'], l_payload['sms'])
    ch.basic_ack(delivery_tag = method.delivery_tag)

    parameter = urllib.urlencode({'username':paramdict['username'],'password':paramdict['password'],'from':paramdict['source'],'to':paramdict['destination'],'text':paramdict['template']})
    fullurl = paramdict['url'] + "?" + parameter
    try:
      response = urllib2.urlopen(fullurl)
      responsebody = response.read()
      logger.info("Http sent to kannel - {0}".format(fullurl))
      logger.info("Http Response - {0}".format(responsebody))
      ch.basic_ack(delivery_tag = method.delivery_tag)
    except urllib2.URLError, e:
      logger.info("ERROR sending http to kannel - {0}".format(fullurl))
      ch.basic_ack(delivery_tag = method.delivery_tag)

  def init(self):
    try:
      self.exchange_name = UVConfig().get_config_value("postbox", "rabbitmq_exchange_name")
      self.conf_queue_name = UVConfig().get_config_value("postbox", "rabbitmq_queue_name")
      self.conf_queue_name += "_" + self.routing_key

      pb_logger_info("rabbitmq_exchange_name {0}, rabbitmq_conf_queue_name {1}, routing_key {2}".format(self.exchange_name, self.conf_queue_name, self.routing_key))

      self.pb_rabbitmq = PostBoxRabbitMQ()

      self.queue_name = create_or_get_queue(queue_name = self.conf_queue_name, durable = True)
      if(None == self.queue_name):
        return False

      if( False == self.pb_rabbitmq.bind_queue_to_exchange(self.exchange_name, self.queue_name, self.routing_key) ):
        return False

      if( False == self.pb_rabbitmq.register_callback(self.callback, queue = self.queue_name) ):
        return False

    except:
      logger.info("ERROR - RabbitMQ queue not established. Check if RabbitMQ is running")
      return False
    return True


if __name__ == "__main__":
  try:
    UCPHOME=os.environ['UCPHOME']
  except:
    UCPHOME="/home/uvadmin/ucp/"
  logging.config.fileConfig(UCPHOME+'conf/postbox_logging.conf')
  logger = logging.getLogger('postbox_app')

  if (len(sys.argv) != 2):
    logger.error("Postbox app requires additional command line argument. It must be one of the telco ids in tb_telcos table")
    sys.exit(2)

  l_route_key = sys.argv[1]  
  # validate l_routing_key is not one of the telco_id
  if(False == UVTelcos().is_telco_id_exists(l_route_key)):
    logger.error("l_route_key {0} is not valid telco id. It must be one of the entries in tb_telcos".format(l_route_key))
    sys.exit(2)

  l_postbox_server = PostBoxServer(l_route_key)
