import redis
import os

local = os.environ.get("LOCAL")
if local:
    redis_hosting = '127.0.0.1'
else:
    redis_hosting = 'my_blog_redis'

client = redis.Redis(host=redis_hosting)
