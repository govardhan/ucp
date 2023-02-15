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

class TestTelcoResolution(unittest.TestCase):
  def setUp(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")

  def test_init(self):
    pass

  def test_reload(self):
    pass

  def test_TelcoResolution(self):
    init_logging("voiceapp.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    l_num_telco_mapper = UVNumberTelcoResolution()
    logging.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("5555")))
    logging.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("12345")))
    logging.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("919886161856")))
    logging.debug("telco_id {0}".format(l_num_telco_mapper.get_telco_id("966551123728")))


if __name__ == '__main__':
  unittest.main()



