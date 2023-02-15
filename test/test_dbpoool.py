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
import base64
import unittest

class TestDBpool(unittest.TestCase):
  def setUp(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
  def test_singleton(self):
    dbp = DBPool()
    dbp1 = DBPool()
    self.assertEqual(dbp,dbp1)
  
  def test_init(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    dbp = DBPool()
    duname = dbp.db_user_name
    dpswd = dbp.db_user_password
    #print dpswd
    dmconn = dbp.db_max_connections
    dserver = dbp.db_server

    uname = conf.get_config_value("database", "db_user_name")
    upswd = conf.get_config_value("database", "db_user_password")
    a = base64.b64decode(upswd)
    umaxconn = conf.get_config_value("database","db_max_connections")
    userver = conf.get_config_value("database", "db_server")

    self.assertEqual(duname,uname)
    self.assertEqual(dpswd,a)
    self.assertEqual(dmconn,umaxconn)
    self.assertEqual(dserver,userver)

    logging.info( duname,dpswd,dmconn,dserver)


  def test_reload(self):
    pass
    # TODO Have to write a methoed for put_config_value to enter the values into config file dynamically
  def test_mqsqlserver_alive(self):
    mysql_status = os.system("service mysqld status")
#    print mysql_status
    self.assertEqual(mysql_status ,0)
  def test_fetched_numRows(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    t_dbp = DBPool()
    t_numrows, t_rows = t_dbp.execute_query("select * from tb_number_normalizer", conf.get_config_value("database","db_name.core") )
    self.assertEqual(t_numrows,6)
    #print("rows {0}".format(l_rows))
  def test_invaliddbname(self):
    conf = UVConfig()
    conf.init("/home/rup/ucp/conf/ucp.conf")
    t_dbp = DBPool()
    t_numrows, t_rows = t_dbp.execute_query("select * from tb_number_normalizer", conf.get_config_value("database","db_name.score") )
    assertRaise(exception)
if __name__ == '__main__':
 

 #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(TestDBpool)
  unittest.TextTestRunner(verbosity=2).run(suite)


