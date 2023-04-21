import os
import redis
import logging
from celery import Celery

# *****************************************************************************
#                  Celery-redis interface initialization
# *****************************************************************************


try:
    worker = Celery("worker",
                backend=os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0'),
                broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
                )
    redis_client = redis.Redis(host='redis', port=6379)
    worker.conf.update(task_track_started=True)
    logger = logging.getLogger("uvicorn.error")
    logger.info("Successfully connected to the Redis server.")
except:
    logger.error("Error while connecting to the Redis server.")


# *****************************************************************************
#                  ASYNCHRONOUS ROUTES OF CELERY 
# *****************************************************************************


@worker.task(name="", trail=True)
def task():
    return 