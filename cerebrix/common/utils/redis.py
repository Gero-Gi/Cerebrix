from redis import Redis
from django.conf import settings

_redis_client = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )
    return _redis_client
