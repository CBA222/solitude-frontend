# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 18:13:50 2018

@author: blins
"""

#from abc import ABCMeta, abstractmethod
import abc
from .event import SignalEvent

from .utils.scheduledfunction import ScheduledFunction

class Strategy(object, metaclass=abc.ABCMeta):
    """

    Class defining a trading strategy.

    ...

    Attributes
    ----------
    scheduled_functions(list)
        A list of scheduled functions for the strategy

    Methods
    -------
    get_signals

    """
    
    def master_setup(self):
        self.scheduled_functions = []    
        self.setup()
    
    @abc.abstractmethod
    def get_signals(self, event):
        raise NotImplementedError("Should implement get_signals()")
    
    def log_vars(self):
        pass
    
    @abc.abstractmethod
    def setup(self):
        raise NotImplementedError("Should implement setup()")
    
    def set_params(self, bars, events, portfolio, engine):
        self.bars = bars
        self.symbols = bars.symbols
        self.events = events
        self.portfolio = portfolio
        self.engine = engine
        
    def schedule_function(self, function, sch_rule):
        self.scheduled_functions.append(ScheduledFunction(function, sch_rule))
        
    def execute_scheduled_functions(self, event):
        
        if event.type != 'MARKET':
            return
        
        for func in self.scheduled_functions:
            if func.on_date(self.bars.current_date(), self.bars.date_idx, self.bars.starts) == True:
                func.function()
                
    def __place_order(self, symbol, amount, amount_type, target):
        signal = SignalEvent(symbol, amount=amount, amount_type=amount_type, target=target)
        self.events.put(signal)
        
    def order(self, symbol, shares):
        self.__place_order(symbol, shares, 'SHARES', False)
    
    def order_target(self, symbol, shares):
        self.__place_order(symbol, shares, 'SHARES', True)
    
    def order_value(self, symbol, value):
        self.__place_order(symbol, value, 'VALUE', False)
    
    def order_target_value(self, symbol, value):
        self.__place_order(symbol, value, 'VALUE', True)
    
    def order_percent(self, symbol, percentage):
        self.__place_order(symbol, percentage, 'PERCENTAGE', False)
        
    def order_target_percent(self,symbol,percentage):
        self.__place_order(symbol, percentage, 'PERCENTAGE', True)
        
        
