import os
import redis
r = redis.StrictRedis(host=os.environ.get('REDIS_URL', 'localhost'), port=6379, db=0)