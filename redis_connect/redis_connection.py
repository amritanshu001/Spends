import platform
import os
import redis
from config import config
from redis.exceptions import ConnectionError


redis_db = {}
redis_db["host"] = os.getenv("REDIS_HOST")
redis_db["port"] = os.getenv("REDIS_PORT")
redis_db["password"] = os.getenv("REDIS_PASSWORD")


blocklist_connection = redis.Redis(
    host=redis_db["host"], port=redis_db["port"], password=redis_db["password"]
)
