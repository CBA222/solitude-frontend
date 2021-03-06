from multiprocessing import Process, Manager
import time
import redis

from flask import Flask, render_template, jsonify, session
from flask_session import Session
from flask_pymongo import PyMongo
from celery import Celery

from .views import backtest

def create_app(test_config=None):

    app = Flask(__name__)
    app.register_blueprint(backtest)

    app.config['MONGO_URI'] = "mongodb://localhost:27017/gcc_data"
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis.Redis('localhost')


    #app.config['CELERY_BROKER_URL'] = 'amqp://localhost'
    #app.config['CELERY_RESULT_BACKEND'] = 'amqp://localhost'

    mongo = PyMongo(app)

    Session(app)

    return app