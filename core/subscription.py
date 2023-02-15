from genutils import *

logger = logging.getLogger('ucp_core')

class UVSubscription(object):
  def subscribe_byname(self, uuid, f_msisdn, t_name):
    logger.debug("params - uuid {0}, f_msisdn {1}, t_name {2}".format(uuid, f_msisdn, t_name))

  def subscribe_bymsisdn(self, uuid, f_msisdn, t_msisdn):
    logger.debug("params - uuid {0}, f_msisdn {1}, t_name {2}".format(uuid, f_msisdn, t_msisdn))

