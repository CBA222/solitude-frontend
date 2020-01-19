from flask import current_app, render_template, Blueprint, jsonify, request
from .tasks import run_backtest
import redis
import datetime as dt
import pandas_market_calendars as mcal

backtest = Blueprint('backtest', __name__)

@backtest.route('/')
def index():
    return render_template('index.html')

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


@backtest.route('/backtest/<int:id>/logs', methods=['GET'])
def backtest_logs(id):
    pass

@backtest.route('/backtest/<int:id>/returns', methods=['GET'])
def backtest_returns(id):
    pass

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

    class_definition = 'class TestStrategy: \n'

    task = run_backtest.apply_async(args=[start_date, end_date, request.json['cash']])

    schedule = mcal.get_calendar('NYSE').schedule(start_date=start_date, end_date=end_date)
    chart_labels = [str(x)[0:10] for x in list(schedule.index)]

    return jsonify({'labels': chart_labels})