from celery import Celery
import os
celery=Celery('jarvis',broker=os.getenv('CELERY_BROKER_URL','redis://redis:6379/0'),backend=os.getenv('CELERY_RESULT_BACKEND','redis://redis:6379/1'),include=['app.tasks'])
celery.conf.update(task_serializer='json',result_serializer='json',accept_content=['json'])
