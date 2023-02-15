
def mt_plugin_kannel(p_uuid, p_from, p_to, p_telco_id, p_sms):
    l_username = UVConfig().get_config_value("postbox", "kannel_username_"+p_telco_id)
    l_password = UVConfig().get_config_value("postbox", "kannel_password_"+p_telco_id)
    l_url = UVConfig().get_config_value("postbox", "kannel_url_"+p_telco_id)

    parameter = urllib.urlencode({'username':l_username,'password':l_password,'from':p_from,'to':p_to,'text':p_sms})
    fullurl = l_url + "?" + parameter
    try:
      logger.info("initiating http request to kannel {0}".format(fullurl))
      response = urllib2.urlopen(fullurl)
      responsebody = response.read()
      logger.info("kannel response {0}".format(responsebody))
    except urllib2.URLError, e:
      logger.info("ERROR sending http to kannel - {0}".format(fullurl))
      return False
    return True

