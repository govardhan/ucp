import logging

logger = logging.getLogger('ucp_core')

def init_logging(app_logfilename):
  logging.basicConfig(filename=app_logfilename,format='%(asctime)s|%(process)-5d|%(thread)d|%(filename)-30s|%(funcName)-16s|%(lineno)4d|%(levelname)-8s| %(message)s', level=logging.DEBUG)

#Refer to http://coding.derkeiler.com/Archive/Python/comp.lang.python/2006-07/msg02135.html
def RSHash(key):
  a = 378551
  b = 63689
  hash = 0
  for i in range(len(key)):
    hash = hash * a + ord(key[i])
    a = a * b
  l_hash = hash & 0x7FFFFFFF
  logger.debug("key: {0}, hash: {1}".format(key, l_hash))
  return l_hash

def BKDRHash(key):
  seed = 131 # 31 131 1313 13131 131313 etc..
  hash = 0
  for i in range(len(key)):
    hash = (hash * seed) + ord(key[i])
  l_hash = hash & 0x7FFFFFFF
  logger.debug("key: {0}, hash: {1}".format(key, l_hash))
  return l_hash
