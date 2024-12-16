import logging
import functools
from celery import shared_task
from redis import Redis
from .redis import get_redis_client

logger = logging.getLogger(__name__)


def locked_task(timeout: int = 60):
    """
    Decorator to lock a task so that only one instance of it can run at a time.
    If the task is already running, it will raise an exception.
    
    Args:
        timeout: The timeout in seconds for the lock.
    """
    def decorator(func):
        @shared_task(bind=True)
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            redis_client = get_redis_client()
            task_id = self.request.id
            lock_key = f"task_lock:{task_id}"

            if redis_client.set(lock_key, "locked", ex=timeout):
                try:
                    return func(self, *args, **kwargs)
                finally:
                    redis_client.delete(lock_key)
            else:
                logger.debug(f"Task {task_id} is already running")
                raise Exception(f"Task {task_id} is already running")

        return wrapper

    return decorator


def is_task_running(task_id: str) -> bool:
    """
    Check if a locked task is already running.
    
    Args:
        task_id: The ID of the task to check.
    """
    redis_client = get_redis_client()
    lock_key = f"task_lock:{task_id}"
    return redis_client.exists(lock_key)
