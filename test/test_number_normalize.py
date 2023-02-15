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

class TestUVNormalizer(unittest.TestCase):
  def setUp(self):
    init_logging("unittest_number_normalize.log")
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
  
  #TODO
  def test_singleton(self):
    pass
    #add assertion for singleton test

  def test_init_001(self):
    l_normalizer = UVNormalizer()
    pass
    #TODO - remove pass. Add assert rule to ensure UVNormalizer init() method loaded rules successfully. 
    #This assertion might need enhancements in UVNormalizer to return number of rows it has been loaded or use len() function to return num of rows

  def test_reload_002(self):
    l_normalizer = UVNormalizer()
    l_normalizer.reload()
    #TODO 
    #add/delete/update more rows in number normalizer table and verify they are reloaded
    pass

  def test_normalize_positive_003(self):
    l_normalizer = UVNormalizer()
    l_number = "9886161856"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,'91'+l_number)
   
  def test_normalize_negative_004(self):
    l_normalizer = UVNormalizer()
    l_number = "988616ghttr"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,False);
    self.assertEqual(l_result,l_number)

  def test_normalize_negative_005(self):
    l_normalizer = UVNormalizer()
    l_number = "9886161856uuu"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,False);
    self.assertEqual(l_result,l_number) 

  def test_normalize_telco_006(self):
    l_normalizer = UVNormalizer()
    l_number = "9886161856"
    l_telco = "91.BH"
    l_found, l_result = l_normalizer.normalize(l_number, p_telco_id = l_telco)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,'91'+l_number)



  def test_normalize_WhiteSpaceRule_007(self):
    l_normalizer = UVNormalizer()
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    DBPool().execute_query("delete from tb_number_normalizer where id = 1001", self.db_name)

    self.rowcount, self.normalize_rules = DBPool().execute_query("insert into tb_number_normalizer( id, in_pattern, out_pattern, telco_id, channel, remarks) values (1001,'(\\d{10})','91\\1','.*','.*','.*')", self.db_name)
    #TODO 
    #this is where you have to reload. after update/insert normalize rule into database they will not load automatically
    #instead we have to invoke reload to take affect
    #self.rowcount, self.normalize_rules .... here self refers to TestUVNormalizer not UVNormalizer. same applies to rest of rests cases too
    l_number = "   906 870 8766"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,'91'+l_number)

  def test_normalize_Third_5_8sRule_008(self):
    l_normalizer = UVNormalizer()
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    DBPool().execute_query("delete from tb_number_normalizer where id = 1002", self.db_name)

    self.rowcount, self.normalize_rules = DBPool().execute_query("insert into tb_number_normalizer( id, in_pattern, out_pattern, telco_id, channel, remarks) values (1002,'(5\\d{8})','966\\1','.*','.*','.*')", self.db_name)
   
    l_number = "888889068708766"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,'966'+l_number)

  def test_normalize_FourthRule_009(self):
    l_normalizer = UVNormalizer()
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    DBPool().execute_query("delete from tb_number_normalizer where id = 1003", self.db_name)

    self.rowcount, self.normalize_rules = DBPool().execute_query("insert into tb_number_normalizer( id, in_pattern, out_pattern, telco_id, channel, remarks) values (1003,'440     440','.*','.*','.*','.*')", self.db_name)

    l_number = "440 440 987643"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,'91'+l_number)


  def test_normalize_FifthRule_010(self):
    l_normalizer = UVNormalizer()
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    DBPool().execute_query("delete from tb_number_normalizer where id = 1004", self.db_name)

    self.rowcount, self.normalize_rules = DBPool().execute_query("insert into tb_number_normalizer( id, in_pattern, out_pattern, telco_id, channel, remarks) values (1004,'441     441','.*','.*','.*','.*')", self.db_name)

    l_number = "440 441 987643"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,'91'+l_number)
    print('Fifth Rule value',l_number)

  def test_normalize_SixthRule_011(self):
    l_normalizer = UVNormalizer()
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    DBPool().execute_query("delete from tb_number_normalizer where id = 1005", self.db_name)

    self.rowcount, self.normalize_rules = DBPool().execute_query("insert into tb_number_normalizer( id, in_pattern, out_pattern, telco_id, channel, remarks) values (1005,'(\\*)(9\\d{8})','*249\\2','.*','.*','.*')", self.db_name)

    l_number = "9888441987643"
    l_found, l_result = l_normalizer.normalize(l_number)
    self.assertEqual(l_found,True);
    self.assertEqual(l_result,l_number)
    print('Sixth Rule value',l_number)

    #TODO - I see there is a serious bug in UVNormalizer.normalize() method. Let see if you can find it 


if __name__ == '__main__':
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(TestUVNormalizer)
  unittest.TextTestRunner(verbosity=2).run(suite)
