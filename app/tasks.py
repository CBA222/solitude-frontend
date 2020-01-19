from .create_celery import celery
import redis

from .solitude.trader import Trader
from .solitude.strategy import Strategy
from .solitude.commission import IBCommission
from .solitude.datafeed import CDFDataFeed
from .solitude.logging import Logger
import datetime as dt

@celery.task(name='solitude-frontend.app.tasks.run_backtest')
def run_backtest(start_date, end_date, cash):

    r = redis.Redis(host='localhost')
    
    class BuyHold(Strategy):
    
        def __init__(self):
            self.bought = False
            self.aapl = 'AAPL'
            self.target_leverage = 1.00
            self.target_stocks = ['AAPL','MSFT','GS','AMZN','FB']
            self.num_stocks = 5
        
        def setup(self):
            pass
            
        def get_signals(self, event):
            percent = self.target_leverage / self.num_stocks
            
            if self.bought is False:
                for stock in self.target_stocks:
                    self.order_target_percent(stock, percent)
                self.bought = True

    class TestStrategy(Strategy):

        def setup(self):
            self.symbol = 'AAPL'

        def get_signals(self, event):
            try:
                history_10d = self.bars.history(self.symbol, 'adj_close', 10)
                returns_10d = history_10d.iloc[-1] / history_10d.iloc[0]

                if returns_10d > 0.0:
                    self.order_target_percent(self.symbol, 0.5)
                else:
                    self.order_target_percent(self.symbol, 0.0)
            except ValueError:
                return

    trader = Trader(
        CDFDataFeed('stock_data.nc'), 
        TestStrategy()
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
