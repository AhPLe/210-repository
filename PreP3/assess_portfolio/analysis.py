"""Analyze a portfolio.

Copyright 2017, Georgia Tech Research Corporation
Atlanta, Georgia 30332-0415
All Rights Reserved
"""

import pandas as pd
import numpy as np
import datetime as dt
import argparse
import sys
sys.path.insert(1, '../')
import math
from util import get_data, plot_data

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def assess_portfolio(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
    syms = ['GOOG','AAPL','GLD','XOM'], \
    allocs=[0.1,0.2,0.3,0.4], \
    sv=1000000, rfr=0.0, sf=252.0, \
    gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cr, adr, sddr, sr = [0.25, 0.001, 0.0005, 2.1] # add code here to compute stats
    
    port_val = prices_SPY # add code here to compute daily portfolio values
    
    

    
    normed = prices/prices.iloc[0]
    
    #print (allocs)
    alloced = normed*allocs
    
    pos_vals = alloced*sv
    port_val = pos_vals.sum(axis=1)
    
    normed_SPY = prices_SPY/prices_SPY.iloc[0]

    
    daily_rets = port_val/port_val.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    
    ev = sv
    ev = port_val[len(pos_vals.index) - 1]
    cr = ev/port_val[0] - 1 #portval.length?  
    adr = daily_rets.mean() #check that avg. daily return is correct
    sddr = daily_rets.std()
    sr_annualized = math.sqrt(sf)
    sr = sr_annualized*(adr-rfr)/(sddr-rfr)
    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        #plot_data( normed, title="Normalized Stock Prices", ylabel="Normalized price")
        #df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
        df_temp = pd.concat([port_val/sv, normed_SPY], keys=['Portfolio', 'SPY'], axis=1)
        #df_temp = pd.concat([normed_SPY], keys=['Portfolio', 'SPY'], axis=1)
        
        #df_temp = pd.concat([port_val], keys=['Portfolio', 'SPY'], axis=1)
        
        #plot_data([port_val, prices_SPY], title="Daily portfolio value and SPY", ylabel="Normalized price")
        plot_data(df_temp, title = 'Daily portfolio value and SPY', ylabel = 'Normalized price')
        pass

    # Add code here to properly compute end value
    return cr, adr, sddr, sr, ev

def test_code():
    # This code WILL NOT be tested by the auto grader
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!
    start_date = dt.datetime(2009,1,1)
    end_date = dt.datetime(2010,1,1)
    symbols = ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocations = [0.2, 0.3, 0.4, 0.1]
    start_val = 1000000  
    risk_free_rate = 0.0
    sample_freq = 252

    parser = argparse.ArgumentParser(
		prog='analysis',
		add_help=True,
		description = 'Short Sample'
		)

    parser.add_argument( '-p', action="store_true", dest="plot", default=False )
    parser.add_argument( '-s', action="store", dest="start_date",default=start_date )
    parser.add_argument( '-e', action="store", dest="end_date",default=end_date )
    parser.add_argument( '-x', nargs='*',action="store", dest="symbols",default=symbols )
    parser.add_argument( '-a', nargs='*',action="store", type=float, dest="allocations",default=allocations )
    parser.add_argument( '-v', nargs='*',action="store", dest="start_value",default=start_val )

    args = parser.parse_args()
    
    symbols = args.symbols
    allocations = args.allocations
    start_date = args.start_date
    end_date = args.end_date
    start_val = args.start_value
    gen_plot = args.plot
    
    # Assess the portfolio
    cr, adr, sddr, sr, ev = assess_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        allocs = allocations,\
        sv = start_val, \
        gen_plot = gen_plot) #should be False on default

    # Print statistics
#    print ("sr test:", sr)
#    print ("backsr test:", 1.51819243641 *sddr*math.sqrt(12))
#    print ("sr2 test2:", (ev/start_val)*math.sqrt(12))
#    print ("srback test:", (cr+1)/1.51819243641)
#    print ("srback test:", (adr)/sddr*math.sqrt(12))
    print ("Start Date:", start_date)
    print ("End Date:", end_date)
    print ("Symbols:", symbols)
    print ("Allocations:", allocations)
    print ("Sharpe Ratio:", sr)
    print ("Volatility (stdev of daily returns):", sddr)
    print ("Average Daily Return:", adr)
    print ("Cumulative Return:", cr)

if __name__ == "__main__":
    test_code()
