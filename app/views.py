from flask import current_app, render_template, Blueprint, jsonify, request
from flask import session
from .tasks import run_backtest
import redis
import uuid
import datetime as dt
import pandas_market_calendars as mcal
from . import config

backtest = Blueprint('backtest', __name__)

@backtest.route('/', methods=['GET'])
def index():

    if 'saved_code' not in session.keys():
        session['saved_code'] = config.DEFAULT_CODE

    if 'id' not in session.keys():
        session['id'] = uuid.uuid4()

    return render_template('index.html', saved_code=session['saved_code'])

@backtest.route('/logs')
def logs():
    remaining_logs = []

    r = redis.Redis(host='localhost')

    for i in range(r.llen('logs')):
        remaining_logs.append(r.lpop('logs').decode('utf-8'))

    return jsonify(remaining_logs)

@backtest.route('/returns')
def returns():
    remaining_returns = []

    r = redis.Redis(host='localhost')

    for i in range(r.llen('returns')):
        remaining_returns.append(r.lpop('returns').decode('utf-8'))

    return jsonify(remaining_returns)

@backtest.route('/backtest/savecode', methods=['POST'])
def savecode():
    session['saved_code'] = request.json['saved_code']
    return 'Saved successfully.'

@backtest.route('/backtest/start', methods=['POST'])
def backtest_start():
    id = 0

    start_date = dt.datetime(
        int(request.json['start_date'][0:4]), 
        int(request.json['start_date'][5:7]),
        int(request.json['start_date'][8:10])
        )

    end_date = dt.datetime(
        int(request.json['end_date'][0:4]), 
        int(request.json['end_date'][5:7]),
        int(request.json['end_date'][8:10])
        )

    task = run_backtest.apply_async(args=[
        session['id'],
        start_date, 
        end_date, 
        request.json['cash'], 
        request.json['code']
        ])

    schedule = mcal.get_calendar('NYSE').schedule(start_date=start_date, end_date=end_date)
    chart_labels = [str(x)[0:10] for x in list(schedule.index)]

    return jsonify({'labels': chart_labels})