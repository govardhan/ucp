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
import logging
import unittest

try:
  UCPHOME=os.environ['UCPHOME']
except:
  UCPHOME="/home/uvadmin/ucp/"
  print "UCPHOME set to /home/uvadmin/ucp/"

class TestUVConfig(unittest.TestCase):
  def __init__(self):
    

  
  def test_singleton(self):
    conf = UVConfig()
    conf.init("/home/uvadmin/ucp/conf/ucp.conf")
    conf_dup = UVConfig()
    self.assertNotEqual(conf ,conf_dup)
  def test_init_012(self):
    """ TestCase Describes the Initialization return value as 1 if initialization goes fine.
        Expected Result for pass value is 1 and 0 for failed initalization.
    """
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    self.assertEqual(conf.m_initialized,1)

    #assert for parser number of sections
    l_sections = len(conf.parser.sections())
    logging.info("Total no of section found".format(l_sections))
    logging.info(" "* 30)
    self.assertTrue(l_sections > 0)
    """Test case to assert the Number of sections present in conf file"""
    self.assertEqual(l_sections, 7)
    l_core_sec_entries = len(conf.parser.items("core"))
    self.assertTrue(l_core_sec_entries > 0)
    """Test case to assert the total count of Items present in "Core" section"""
    self.assertEqual(l_core_sec_entries,8)
    #assert on random config key existance



  def test_reload(self):
    """ Tescase description: Check for the reloading functionality for any dynamic changes are
	Happned to Configuration file.
	Expected Result : Dynamic Changes should be reflected after Reload() is called.
    """
    init_logging("testUCP.log")
    conf= UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    f = open("/home/rup/ucp/conf/ucp.conf", 'r+w')
    f_content = f.readlines()
    sec = 'Test_Section1'
    for line in f_content:
      if sec in line:
        f_content.write(line.replace(sec,''))
      else:
        f_content += "\n[Test_Section1]\n\tkey1 = value1\n\tkey2 = value2\n\tkey3 = value3"
    f.seek(0)
    f.truncate()
    f.write(''.join(f_content))
    f.close()
   
    conf.reload()
    l_sections = len(conf.parser.sections())
    self.assertEqual(l_sections, 1)
    l_core_sec_entries = len(conf.parser.items("Test_Section1"))
    self.assertEqual(l_core_sec_entries,3)
    
  def test_setUp_obsolutepath_001(self):
    """TestCase Description: Check for the Obsolute path of the conf file while Initializing.
       Expected Result : Should get initialized for obsolute path

    """
    init_logging("testUCP.log")
    conf = UVConfig()
    a = conf.init("/home/rup/ucp/conf/ucp.conf")
    print a #TODO donte use print statements instead use logging

  def test_setUp_IncorrectFile_002(self):
    """TestCAse Description : Check for Incorrect file by giving un-matching file in the path
       Expected Result : Should throw proper Error Log message before starting the application.
    """
    init_logging("testUCP.log")
    conf = UVConfig()
    a = conf.init("/home/rup/ucp/conf/uc.conf")
    print a
 
  def test_setUp_IncorrectPath_003(self):
    """ TestCase Description: Check the functionality by giving the incorrect path
        Expected Result : Should throw an aprropriate error message in log 
    """
    init_logging("testUCP.log")
    conf = UVConfig()
    a = conf.init("/home/ucp/conf/ucp.conf")
    print a
  def test_setUp_RelativePath_004(self):
    """ TestCase Description: Check the functionality by giving the relative Path while initializing.
	Expected Result : Should get executed without any error.
    """
    init_logging("testUCP.log")
    conf = UVConfig()
    a = conf.init("../ucp/conf/ucp.conf")
    print a

  def test_setUp_EmptyArg_005(self):
    """TestCase Description: Check for the functionality for anegative case by sending empty arguemnts 
       Expected Result : Should throw a relevant error message.
    """
    init_logging("testUCP.log")
    conf = UVConfig()
    a = conf.init(" ")
    print a 

  def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

  def test_setUp_ASCIIfile_006(self):
    """ Test Case Description: Check for the functionality of ASCII file format for conf file , by default conf file is in ASCII format, UVCOnfig() may be converting it to UTF-8 character set .
	Expected Result : Should be converted to UTF-8 character set format file.
    """
    init_logging("testUCP.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    f = os.popen('file /home/rup/ucp/conf/ucp.conf')
    txt = f.read()
    print txt
    if 'ASCII' in txt : 
	print ('Success')
    else:
        print('ASCII case Failed')
  def test_setUP_UTF8_007(self):
    init_logging("testUCP.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.txt")
    g  = os.popen('file /home/rup/ucp/conf/ucp.txt')
    tt = f.read()
    print tt
    if 'UTF-8' in tt :
        print ('Success')
    else:
        print('UTF -8 case Failed')    


  def test_setUp_EmptyArg_008(self):
    init_logging("testUCP.log")
  
    conf = UVConfig()
    a = conf.init(" ")
    print a

  def test_getConfigMissingSection_009(self):
    init_logging("testUCP.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    print conf.get_config_value("test"," ")
  
  def test_getConfigMissingKey_010(self):
    init_logging("testUCP.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    print conf.get_config_value("test_rupesh"," ")
   
  def test_getConfigMissingValue_011(self):
    init_logging("testUCP.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    print conf.get_config_value("test_rupesh","datamiss")




if __name__ == '__main__':
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(TestUVConfig)
  unittest.TextTestRunner(verbosity=2).run(suite)
