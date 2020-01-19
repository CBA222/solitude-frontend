import os
from app import create_app
from app.create_celery import celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()