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

class TestUVAudioPrompts(unittest.TestCase):
  def setUp(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")

  def test_init(self):
    pass

  def test_reload(self):
    pass

  def test_UVAudioPrompts(self):
    #init_logging("voiceapp.log")

    
    l_prompts = UVAudioPrompts()
    l_prompts.get_file_name("welcome")  
    l_prompts.get_file_name("welcome", "91.BH")
    l_prompts.get_file_name("thankyou", "91.BH")
    l_prompts.get_file_name("THANKYOU", "91.BH")
    l_prompts.get_file_name("")
    l_prompts.get_file_name("welcome", None)




if __name__ == '__main__':
  unittest.main()

