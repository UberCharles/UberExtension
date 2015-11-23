import os
import redis
r = redis.StrictRedis(host=os.environ.get('REDIS_URL', 'localhost'), db=0)