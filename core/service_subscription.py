from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

logger = logging.getLogger('ucp_core')

class SubscriptionServices(object):
  def __init__(self):
    self.init()
  def reload():
    self.init()

  def init(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    l_res, self.rowcount, self.services = DBPool().execute_query("select id, service_id, service_name, service_group, remarks from tb_services order by id", self.db_name)
    logger.info("id     service_id       service_name      service_group        remarks")
    logger.info("-" * 70)
    for l_row in self.services:
      logger.info("{0}\t{1}\t{2}\t{3}\t{4}".format(l_row['id'], l_row['service_id'], l_row['service_name'], l_row['service_group'], l_row['remarks']))

  def subscribe_to_service(self, cell_no,service_subscribe,channel,operator_id):
    '''This Method used to initiate subscription, cell_no - customer cell no; service_subscribe - user wants which service to subscribe; 
	   channel - TODO ;operator_id - customer service provider  '''

    #customer_eligibility = get_customer_eligibility(cell_no,service_subscribe,operator_id) # check customer eligibility by requesting user eligibility from user service provider
    #  if customer_eligibility == true :
    pass
        
      
