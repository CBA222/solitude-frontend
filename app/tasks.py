from .create_celery import celery
import redis

from RestrictedPython import compile_restricted
from RestrictedPython import safe_builtins
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import guarded_iter_unpack_sequence
import textwrap

from .solitude.trader import Trader
from .solitude.strategy import Strategy
from .solitude.commission import IBCommission
from .solitude.datafeed import CDFDataFeed
from .solitude.logging import Logger
import datetime as dt


_safeglobals = {
    '__builtins__': safe_builtins,
    '__metaclass__': type,
    '_getiter_': default_guarded_getiter,
    '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
    '__name__': __name__
}

def build_strategy(str):

    loc = {'Strategy': Strategy}

    source_code = """
class TestStrat(Strategy):
    def __init__(self):
        pass

    """ + textwrap.indent(str, '    ')


    byte_code = compile(
        source_code,
        filename='<inline code>',
        mode='exec'
    )

    exec(byte_code, globals(), loc)
    return loc['TestStrat']

@celery.task(bind=True, name='solitude-frontend.app.tasks.run_backtest')
def run_backtest(self, session_id, start_date, end_date, cash, code):

    r = redis.Redis(host='localhost') 

    trader = Trader(
        CDFDataFeed('stock_data.nc'), 
        build_strategy(code)()
        )

    trader.attach_logger(Logger())

    trader.set_run_settings(
        cash = int(cash),
        log_orders = False,
        start = start_date,
        end = end_date,
        commission = IBCommission()
        )

    r.rpush('logs', 'Beginning backtest from {} to {}'.format(start_date, end_date))
        
    trader.run()
    trader.results()

    r.rpush('logs', 'Backtest ended.')
    r.rpush('logs', trader.save_results())
