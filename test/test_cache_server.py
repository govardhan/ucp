from redis import Redis
from genutils import *
from config import UVConfig
from uv_decorators import *

@singleton
class UVCache(Redis):
  def __init__(self):
    Redis.__init__(self, UVConfig().get_config_value("platform", "redis_server"))

if __name__ == "__main__":
  init_logging("voiceapp.log")
  conf = UVConfig()
  conf.init("/root/ucp/ucp/conf/ucp.conf")

  UVCache().set("name", "govi")
  print UVCache().get("name")
