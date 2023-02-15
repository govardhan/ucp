from dbpool import DBPool
from genutils import *
from config import UVConfig

class CDR:
  def __init__(self):
    self.db_name = UVConfig().get_config_value("database","db_name.core")
  #TODO add offline batch process logic
  def write_cdr(self, p_uuid, p_src, p_src_telco_id, p_dst, p_norm_dst, p_dst_telco_id, p_service_id, p_start_time, p_end_time, p_call_duratin, p_call_complete_type):
    l_res, l_rc, l_tmp = DBPool().execute_query("insert into tb_cdr(uuid, source, src_telco_id, dialed_number, destination, dst_telco_id, service_id, start_time, end_time, call_duration, call_complete_type) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')".format(p_uuid, p_src, p_src_telco_id, p_dst, p_norm_dst, p_dst_telco_id, p_service_id, p_start_time, p_end_time, p_call_duratin, p_call_complete_type), self.db_name)

  def write_cdr_txn():
    pass


#Run unit tests
if __name__ == "__main__":
  init_logging("voiceapp.log")
  conf = UVConfig()
  conf.init("/root/ucp/ucp/conf/ucp.conf")
  l_cdr = CDR()
  l_dbname = l_cdr.db_name
  l_cdr.write_cdr('46c1a748-28dd-11e2-85c4-57dae9aeee9b', '9886161856', '91.bh', '440', '440', '91.bh', 'sovoi_post', '2012-11-08 02:58:35', '2012-11-08 02:58:55', '20', 'user_hangup')
