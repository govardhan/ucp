from postbox_plugin_handlers import *

@singleton
class PostBoxPluginManager(object):
  def __init__(self):
    self.init()

  def reload(self):
    self.init()

  def init(self):
    pass

  def get_postbox_mt_plugin(p_uuid, p_telco_id):
    l_plugin_key = "mt_plugin_"+p_telco_id
    l_plugin_str = UVConfig().get_config_value("postbox", l_plugin_key)
    try:
      l_plugin_handler = eval(l_plugin_str)
    except:
      logger.error("{0} unable to find postbox mt plugin handler for telco_id {1}, [postbox] key {2}".format(p_uuid, p_telco_id, l_plugin_str))
      return None
    return l_plugin_handler
