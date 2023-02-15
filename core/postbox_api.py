# -*- coding: utf-8 -*-
"""
  postbox_api.py module provides API to send SMS to the applications
"""
import sys
import os
import logging
from datetime import datetime

import pika
from django.template import Template, Context
from django.conf import settings

from config import UVConfig
from cache_server import UVCache
from rmq_setup import Producer
from uv_decorators import *
from postbox_rabbitmq import PostBoxRabbitMQ

@singleton
class PostBox(object):
  """PostBox class provides API to the applications to send SMS
     Various options are explored to applications such as
     - SMS as template along with specific language and telco id.
     - SMS as exact text message.
     - to single recepient, multiple recepients in list, multiple recepients in text file, db query

    PostBox writes SMS into RabbitMQ. :class:`PostBoxServer` on otherhand process the same and send to recepient  
  """
  def __init__(self):
    self.init()

  def reload(self):
    self.init()

  def init(self):
    """Initializaiton
       Initialize django settings to use django templates
       Load tb_sms table entries
    """
    settings.configure()  #for django templates
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.sms_list = DBPool().execute_query("select id, template, telco_id, lang, sms, sender_name, remarks from tb_sms order by id desc", self.db_name)
    assert (l_res == True and self.rowcount > 0) , "PostBox failed to load sms from database. verify tb_sms table result {0} rows (1)".format(l_res, self.rowcount)

    logger.info("SMS messages. Search order from top to bottom")
    for l_row in self.sms_list:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(l_row['id'], l_row['template'], l_row['telco_id'], l_row['lang'], l_row['sms'], l_row['sender_name'], l_row['remarks']))
    return True

    
  def get_sms_for_template(self, p_uuid, p_template, p_telco_id, p_lang):
    """get_sms_for_template method retrieves SMS message for the given template from tb_sms table.
    """
    logger.debug("params - p_uuid {0}, p_template {1}, p_telco_id {2}, p_lang {3}".format(p_uuid, p_template, p_telco_id, p_lang))
    for l_row in self.sms_list:
      if( (None != re.match(l_row['template'], p_template)) and (None != re.match(l_row['telco_id'], p_telco_id)) and (None != re.match(l_row['lang'], p_lang))  ):
        logger.info("Matchfound. id = {0}, sender_name = {1}, sms = {2} ".format(l_row['id'], l_row['sender_name'], l_row['sms']) )
        return True, l_row['sms'], l_row['sender_name']

    #End of for loop. No match found. So return False
    logger.warn("No sms match not found for the given p_template {0},  = p_telco_id {1}. p_lang = {2}".format(p_template, p_telco_id, p_lang) )
    return False, None, None


  def expand_sms(self, p_sms, p_template_vars):
    """ expand_sms replaces template strings in p_sms with corresponding values in p_template_vars dict
    """
    l_template = Template(p_sms)
    l_context = Context(p_template_vars)
    return l_template.render(l_context)


  def sendsms(self, p_uuid, p_sender_name, p_telco_id, p_sms, p_to, sms_type = "text", lang = None, template_vars = None):
    """sendsms API to applications to send sms.
       - args p_uuid: unique id, p_sender_name: CLI in the SMS, p_telco_id: recipient telco id, 
              p_sms: sms text or template name, p_to: recipient phone number,
              sms_type: type of sms (template, text), lang: receipient preferred language (not applicable if sms_type is text)
              template_vars: dict contains data for the corresponding sms template (not applicable if sms_type is text)
       - returns True or False whether sendsms initiated or not
    """

    if(template_vars is None):
      logger.debug("{0} template_vars is none. setting to empty dict".format(p_uuid))
      template_vars = {}

    if(lang is None):
      logger.debug("{0} lang is none. setting to empty".format(p_uuid))
      lang = ""

    logger.debug("params - p_uuid {0}, p_sender_name {1}, p_telco_id {2} lang {3}, p_sms {4}, p_to {5}, sms_type {6}, template_vars {7}".format(p_uuid, p_sender_name, p_telco_id, lang, p_sms, p_to, sms_type, template_vars))

    #if the p_sms is template fetch & explode
    if( "template" == sms_type):
      l_found, l_sms, l_sender_name = self.get_sms_for_template(p_uuid, p_sms, p_telco_id, lang)  
      if(False == l_found):
        log.warn("{0} sendsms failed to send. sms not found for the template {1}, p_telco_id {2}, lang {3}".format(p_uuid, p_sms, p_telco_id, lang))
        return False
      else:
        p_sms = l_sms  #assign sms from template 
        if(l_sender_name is not None and len(l_sender_name) > 0):
          log_debug("{0} replacing sendername with {1} template sendername {2}".format(p_uuid, p_sms, p_sender_name))
          p_sender_name = l_sender_name 

        if( not isinstance(template_vars, dict) ): #if the template_vars is not the dict
          logger.error("{0} expecting template_vars to be dict. But found {1}. unable to send sms".format(p_uuid, template_vars))
          return False
        elif( len(template_vars) == 0 ) :
          logger.debug("{0} template_vars dict is empty".format(p_uuid))
        expand_sms(p_uuid, p_sms, template_vars)
    return PostBoxRabbitMQ().sendsms(p_uuid, p_sender_name, p_telco_id, p_sms, p_to)
