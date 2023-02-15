import os, sys
lib_path = os.path.abspath('../ucp/core')
sys.path.append(lib_path)

from number_normalize import *
from dbpool import DBPool
from genutils import *
from uv_decorators import *
from config import UVConfig
import time
import re

import unittest

class TestTelcoProfile(unittest.TestCase):
  def setUp(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")

  def test_init(self):
    pass

  def test_reload(self):
    pass

  def test_TelcoProfile(self):
    init_logging("voiceapp.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
   
    l_telco_profile = UVTelcoProfile()
    l_found, l_result = l_telco_profile.get_lang("91.BH")
    l_found, l_result = l_telco_profile.get_lang("966.STC")
    l_found, l_result = l_telco_profile.get_lang("966.STC",2)
    l_found, l_result = l_telco_profile.get_lang("91.BH",3)

if __name__ == '__main__':
  unittest.main()


