from celery import Celery

rabbit_host = 'amqp://localhost'
redis_host = 'redis://localhost'

celery = Celery(__name__, broker=redis_host, include=['app.tasks'])