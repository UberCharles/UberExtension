import os
import redis
import urlparse
if os.environ.get('REDIS_URL', 'localhost') != 'localhost':
  url = urlparse.urlparse(os.environ.get('REDIS_URL'))
  r = redis.Redis(host=url.hostname, port=url.port, password=url.password)
else:
  r = redis.StrictRedis(host='localhost', port=6379h, db=0)