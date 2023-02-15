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
from cdr import CDR
import string
import unittest

class TestCdr(unittest.TestCase):
  def setUp(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    print id(conf)
  def test_cdr_reload(self):
    pass
 
  def test_cdr(self):
    init_logging("voiceapp.log")
    conf = UVConfig()
    l_cdr = CDR()
    conf.init("/home/rup/ucp/conf/ucp.conf")

    self.db_name = UVConfig().get_config_value("database","db_name.core")

    self.l_clear = DBPool().execute_query("delete from tb_cdr where source = 9886161856",self.db_name)
    for i in  range(1001,1051) :
      l_cdr.write_cdr('76c1a748-38dd-11e2-'+str(i)+'-57dae9aeee9b', '9886161856', '91.bh', '440', '440', '91.bh', 'sovoi_post', '2012-11-08 02:58:35', '2012-11-08 02:58:55', '20', 'release')

  def test_cdr_dbconnection(self):
    l_cdr = CDR()
    self.assertEqual(l_cdr.db_name , 'core')

  def test_num_rows_assertion(self):
    conf = UVConfig()
    l_cdr = CDR()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    a = id(l_cdr)
    #print a
    self.db_name = UVConfig().get_config_value("database","db_name.core")
    self.l_clear = DBPool().execute_query("delete from tb_cdr where source = 9886161856",self.db_name)

    for i in  range(1001,1051) :
      l_cdr.write_cdr('76c1a748-38dd-11e2-'+str(i)+'-57dae9aeee9b', '9886161856', '91.bh', '440', '440', '91.bh', 'sovoi_post', '2012-11-08 02:58:35', '2012-11-08 02:58:55', '20', 'release')

    self.l_rows,l_queryresult = DBPool().execute_query(" select * from tb_cdr",self.db_name)
    self.assertEqual(self.l_rows ,50,msg = 'asserting Number of rows witten to table')
#Deleting the inserted test Rows

if __name__ == '__main__':
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(TestCdr)
  unittest.TextTestRunner(verbosity=3).run(suite)

