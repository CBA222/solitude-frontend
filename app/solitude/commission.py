# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 23:15:20 2018

@author: blins
"""

import abc

class Commission(object, metaclass = abc.ABCMeta):
    """
    Commission Class

    Purpose is to return the commission value for a certain stock order
    """
    
    @abc.abstractclassmethod
    def get_commission(self, shares, share_price):
        pass

class IBCommission(Commission):
    """
    Interactive Brokers Commission
    (https://www.interactivebrokers.com/en/index.php?f=1590&p=stocks1)

    Max commission value: 1% of the total trade value (shares x share price)
    Min commission value: 1.00
    Otherwise: 0.005 per share
    """
    
    def __init__(self):
        self.min = 1.00
        self.fixed = 0.005
        self.max_share = 0.01
    
    def get_commission(self, shares, share_price):
        max_comm = ( shares * share_price ) * self.max_share
        base_value = shares * self.fixed
        if base_value < self.min:
            return self.min
        elif base_value > max_comm:
            return max_comm
        else:
            return base_value
        
class FixedCommission(Commission):
    """
    Fixed Commission

    Charges a fixed commission for every trade, regardless of size or value
    """
    
    def __init__(self, fixed):
        self.fixed = fixed
        
    def get_commission(self, shares, share_price):
        return self.fixed
        
class FixedPercentageCommission(Commission):
    """
    Fixed Percentage Commission

    Charges a fixed percentage of the total trade value
    """
    
    def __init__(self, percent):
        self.percent = percent
        
    def get_commission(self, shares, share_price):
        return (shares * share_price) * self.percent
        
        
        
        
        
        
        
        
        
    