import redis
from decouple import config

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client 