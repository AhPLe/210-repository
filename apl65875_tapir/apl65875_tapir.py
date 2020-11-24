from agent.TradingAgent import TradingAgent
import pandas as pd
import numpy as np
import os
from contributed_traders.util import get_file

class apl65875_tapir(TradingAgent):
    """
     # Author: Arthur LeBlanc
    # Agent Name: tapir
    # Other Names: Bollinger_Simple_Agent
    #
    # The author of this code hereby permits it to be included as a part of the ABIDES distribution, 
    # and for it to be released under any open source license the ABIDES authors choose to release ABIDES under.
    
    apl65875 tapir modifies Simple Trading Agent to use Bollinger Bands. The bands can be modified by changing a value in the __init__ of this file.
    """

    def __init__(self, id, name, type, symbol, starting_cash,
                 min_size, max_size, wake_up_freq='60s',
                 log_orders=False, random_state=None):

        super().__init__(id, name, type, starting_cash=starting_cash, log_orders=log_orders, random_state=random_state)
        self.symbol = symbol
        self.min_size = min_size  # Minimum order size
        self.max_size = max_size  # Maximum order size
        self.size = self.random_state.randint(self.min_size, self.max_size)
        self.wake_up_freq = wake_up_freq
        self.mid_list, self.avg_win1_list, self.avg_win2_list = [], [], []
        self.log_orders = log_orders
        self.state = "AWAITING_WAKEUP"
        self.band_width = 2.25
        #self.window1 = 100 
        #self.window2 = 5 

    def kernelStarting(self, startTime):
        super().kernelStarting(startTime)
        # Read in the configuration through util
        with open(get_file('simple_agent.cfg'), 'r') as f:
            self.window1, self.window2 = [int(w) for w in f.readline().split()]
        #print(f"{self.window1} {self.window2}")

    def wakeup(self, currentTime):
        """ Agent wakeup is determined by self.wake_up_freq """
        can_trade = super().wakeup(currentTime)
        if not can_trade: return
        self.getCurrentSpread(self.symbol)
        self.state = 'AWAITING_SPREAD'

    def dump_shares(self):
        # get rid of any outstanding shares we have
        if self.symbol in self.holdings and len(self.orders) == 0:
            order_size = self.holdings[self.symbol]
            bid, _, ask, _ = self.getKnownBidAsk(self.symbol)
            if bid:
                self.placeLimitOrder(self.symbol, quantity=order_size, is_buy_order=False, limit_price=0)

    def receiveMessage(self, currentTime, msg):
        """ Momentum agent actions are determined after obtaining the best bid and ask in the LOB """
        super().receiveMessage(currentTime, msg)
        if self.state == 'AWAITING_SPREAD' and msg.body['msg'] == 'QUERY_SPREAD':
            dt = (self.mkt_close - currentTime) / np.timedelta64(1, 'm')
            if dt < 25:
                self.dump_shares()
            else:
                bid, _, ask, _ = self.getKnownBidAsk(self.symbol)
                if bid and ask:
                    self.mid_list.append((bid + ask) / 2)
                    if len(self.mid_list)>5:
                        relmid_list = pd.Series(self.mid_list[-6:-1])
                        band_low = relmid_list.mean() - relmid_list.std()*self.band_width
                        band_high = relmid_list.mean() + relmid_list.std()*self.band_width
                        if len(self.orders) == 0:
                            if self.mid_list[-1] <= band_low:
                                # Check that we have enough cash to place the order
                                if self.holdings['CASH'] >= (self.size * ask):
                                    self.placeLimitOrder(self.symbol, quantity=self.size, is_buy_order=True, limit_price=ask)                            
                                elif self.mid_list[-1] >= band_high:
                                    
                                    if self.symbol in self.holdings and self.holdings[self.symbol] > 0:
                                        order_size = min(self.size, self.holdings[self.symbol])
                                        self.placeLimitOrder(self.symbol, quantity=order_size, is_buy_order=False, limit_price=bid)
                                else:
                                    # do nothing, was not in band length
                                    pass

                    #if len(self.mid_list) > self.window1: self.avg_win1_list.append(pd.Series(self.mid_list).ewm(span=self.window1).mean().values[-1].round(2))
                    #if len(self.mid_list) > self.window2: self.avg_win2_list.append(pd.Series(self.mid_list).ewm(span=self.window2).mean().values[-1].round(2))
                    #if len(self.avg_win1_list) > 0 and len(self.avg_win2_list) > 0 and len(self.orders) == 0:
                    #    if self.avg_win1_list[-1] >= self.avg_win2_list[-1]:
                            # Check that we have enough cash to place the order
                   #         if self.holdings['CASH'] >= (self.size * ask):
                   #             self.placeLimitOrder(self.symbol, quantity=self.size, is_buy_order=True, limit_price=ask)
                   #     else:
                   #         if self.symbol in self.holdings and self.holdings[self.symbol] > 0:
                   #             order_size = min(self.size, self.holdings[self.symbol])
                   #             self.placeLimitOrder(self.symbol, quantity=order_size, is_buy_order=False, limit_price=bid)
            self.setWakeup(currentTime + self.getWakeFrequency())
            self.state = 'AWAITING_WAKEUP'

    def getWakeFrequency(self):
        return pd.Timedelta(self.wake_up_freq)
