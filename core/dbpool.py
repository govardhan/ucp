import base64
import PySQLPool
from genutils import *
from uv_decorators import *
from config import UVConfig

logger = logging.getLogger('ucp_core')

@singleton
class DBPool:
  def __init__(self):
    self.db_user_name = UVConfig().get_config_value("database", "db_user_name")
    self.db_user_password = UVConfig().get_config_value("database", "db_user_password")
    self.db_max_connections = UVConfig().get_config_value("database", "db_max_connections")
    self.db_server = UVConfig().get_config_value("database", "db_server")
    logger.info("db_user_name {0} db_user_password {1} db_max_connections {2} db_server {3}".format(self.db_user_name, self.db_user_password, self.db_max_connections, self.db_server))
    self.db_user_password = base64.b64decode(self.db_user_password)

    PySQLPool.getNewPool().maxActiveConnections = self.db_max_connections


  #TODO connection object can be persisted instead of getting connection object every time
  #Handle exceptions
  #Find more on query return execution return value vs l_query.affectedRows
  def execute_query(self, p_query, p_dbname):
    try:
      logger.debug("query {0} dbname {1}".format(p_query, p_dbname))
      l_connection = PySQLPool.getNewConnection(username=self.db_user_name, password=self.db_user_password, host=self.db_server, db=p_dbname,  charset = "utf8")
      #TODO Second param True is autocommit flag. Explore more on this param behavior for batch inserts
      l_query = PySQLPool.getNewQuery(l_connection, True)
      l_retval = l_query.Query(p_query)
      #print l_query.affectedRows
      return True, l_retval, l_query.record
    except:
      logger.exception("query [{0}] failed to execute. p_dbname {1}".format(p_query, p_dbname))
      return False, None, None
 
if __name__ == "__main__":
  #Run unit tests
  init_logging("voiceapp.log")
  conf = UVConfig()
  conf.init("/home/uvadmin/ucp/conf/ucp.conf")

  l_dbpool = DBPool()
  l_res, l_numrows, l_rows = l_dbpool.execute_query1("select * from tb_number_normalizer", conf.get_config_value("database","db_name.core") )
  if(l_res):
    print("Num of rows {0}".format(l_numrows))
    print("rows {0}".format(l_rows))
  else:
    print "failed to run query"

  print "\n\n"

  l_res, l_numrows, l_rows = l_dbpool.execute_query1("select * from tb_number_normalier", conf.get_config_value("database","db_name.core") )
  if(l_res): 
    print("Num of rows {0}".format(l_numrows))
    print("rows {0}".format(l_rows))
  else:
    print "failed to run query"

