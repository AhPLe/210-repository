"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import datetime as dt
import os
import sys
import math
import argparse
from util import get_data, plot_data

VERBOSE = False

def extract_orders(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
    syms = ['GOOG','AAPL','GLD','XOM'], \
    shares=[1,2,3,4], \
    buys = [True, True, True, True], \
    cash = 1000000, \
    rfr=0.0, sf=252.0, \
    commission=9.95, mimpact=0.005, \
    gen_plot=False):
    
    init_syms = syms.copy()
    init_shares = shares.copy()
    init_buys = buys.copy()
    #this is a modified version of the assess_portfolio we did in class
    #the primary difference is the shares portion vs. allocation %
    #the rest should be the same
    
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    
    if not len(syms)==len(shares) and not len(syms)==len(buys):
        print('LENGTHS OF SYMS, SHARES, AND BUYS DO NOT MATCH')
        sys.exit(1)

    moveshares = [None]*len(syms)
    #if VERBOSE:
    #    print('moveshares is')
    #    print(moveshares)
    removeshares = []
    
    shortlistsyms = syms.copy()
    
    i=0
    count=0
    while i<len(syms):
        index = syms.index(syms[i])
        if not index == i:
            moveshares[i] = index
            shortlistsyms.pop(i-count)
            count+=1
        i+=1    
    
    #i=0
    #while i<len(syms):
    #    index = syms.index(syms[i])
    #    #if not index == i:
    #    if buys[i] == True:
    #        shares[index] = shares[index] + shares[i]
    #    elif buys[i] == False:
    #        shares[index] = shares[index] - shares[i]
    #    else:
    #        print('illegal value in buys, value was not', None, ',', True, \
    #              'or', False)
    #        exit(1)
    
    #    i+=1
        #None buys indicate the share already existed, True or False indicates
        #selling or buying
        
    
    
    #print(syms)
    #print(dates)
    prices_all = get_data(shortlistsyms, dates)  # automatically adds SPY
    prices = prices_all[shortlistsyms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later
    
    # Get daily portfolio value

    port_val = prices_SPY # add code here to compute daily portfolio values

    # Get portfolio statistics (note: std_daily_ret = volatility)
            
    for i in range(len(syms)):
        if not buys[i]==None:
            index = i if moveshares[i] == None else moveshares[i]
            #if VERBOSE:
            #    print(syms[i], 'comparing ', syms[index])

            if buys[i] == True:
                #remove the cash of the inital price back
                cash -= (1+mimpact)*prices[syms[index]].iloc[0]*shares[i]
                cash -= commission
                if not index == i:
                    shares[index]+=shares[i]
            elif buys[i] == False:
                #add the cash of the inital price back
                cash += (1-mimpact)*prices[syms[index]].iloc[0]*shares[i]
                cash -= commission
                if not index == i:
                    shares[index] -= shares[i]
                else:
                    shares[index] = -shares[i]
                #removeshares.append(i)
            else:
                print('illegal value in buys, value was not', None, ',', True, \
                      'or', False)
                exit(1)

    i = 0
    #if VERBOSE:
    #    print('premoveshares', moveshares)
    while i<len(moveshares):
        if not moveshares[i] == None:
            syms.pop(i)
            shares.pop(i)
            buys.pop(i)
            moveshares.pop(i)
            i-=1
        i+=1
    #if VERBOSE:
    #    print('postmoveshares', moveshares)

    #print(prices)
    #p = 1500
    #print(shares[0]*1.0)
    sym_vals = prices*(shares)
    normed_vals = sym_vals/sym_vals.iloc[0]
    port_val = sym_vals.sum(axis=1) + cash
    
    #alloced = normed*allocs
    
    #pos_vals = alloced*sv
    #port_val = pos_vals.sum(axis=1)
    
    normed_SPY = prices_SPY/prices_SPY.iloc[0]
    
    daily_rets = port_val/port_val.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    
    #cr = port_val[len(port_val.index) - 1]/port_val[0] - 1 #portval.length?  
    #adr = daily_rets.mean() #check that avg. daily return is correct
    #sddr = daily_rets.std()
    #sr = adr/sddr

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        #plot_data( normed_vals, title="Normalized Stock Prices", ylabel="Normalized price")
        df_temp = pd.concat([normed_vals, normed_SPY], keys=['Portfolio', 'SPY'], axis=1)
        
        plot_data(df_temp, title = 'Daily portfolio value and SPY', ylabel = 'Normalized price')
        pass

    # Add code here to properly compute end value
    ev = port_val[len(port_val.index) - 1]
    if VERBOSE:
        print ("From between {} and {}:".format(sd, ed))
    #    print ("End Date:", ed)
        print ("Symbols:", init_syms)
        print ("Shares:", init_shares)
     #   print ("Buys:", init_buys)
     #   print ("Sharpe Ratio:", sr)
     #   print ("Volatility (stdev of daily returns):", sddr)
     #   print ("Average Daily Return:", adr)
     #   print ("Cumulative Return:", cr)
        print ("End Value:", ev)
    
    #TODO: check for duplicate shares and remove them
    
    return port_val, cash, syms, shares#, cr, adr, sddr, sr, ev

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

    port_val = prices_SPY # add code here to compute daily portfolio values

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cr, adr, sddr, sr = [0.25, 0.001, 0.0005, 2.1] # add code here to compute stats
    
    normed = prices/prices.iloc[0]
    
    alloced = normed*allocs
    
    pos_vals = alloced*sv
    port_val = pos_vals.sum(axis=1)
    
    normed_SPY = prices_SPY/prices_SPY.iloc[0]

    
    daily_rets = port_val/port_val.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    
    cr = port_val[len(pos_vals.index) - 1]/port_val[0] - 1 #portval.length?  
    adr = daily_rets.mean() #check that avg. daily return is correct
    sddr = daily_rets.std()
    sr = adr/sddr

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        #plot_data( normed, title="Normalized Stock Prices", ylabel="Normalized price")
        df_temp = pd.concat([port_val/sv, normed_SPY], keys=['Portfolio', 'SPY'], axis=1)
        
        plot_data(df_temp, title = 'Daily portfolio value and SPY', ylabel = 'Normalized price')
        pass

    # Add code here to properly compute end value
    ev = sv
    ev = port_val[len(pos_vals.index) - 1]
    return cr, adr, sddr, sr, ev 

def compute_portvals(orders_file = "./orders/orders.csv", \
     start_val = 1000000, commision = 9.95, impact=0.05):
    # this is the function the autograder will call to test your code
    
    #extract the orders
    expected_list = ['Date','Symbol','Order','Shares']
    with open(orders_file, 'r') as file:
        orders = file.read()
    
    by_line = orders.split('\n')
    equal = True
    by_line_initial = by_line[0].split(',')
    
    if (len(expected_list)!=len(by_line_initial)):
        equal = False
    
    for i in range(len(expected_list)):
        if equal and not by_line_initial[i].lower() == expected_list[i].lower(): #.lower
            equal = False
    
    if not equal:
        print('unable to parse orders, correct structure is', expected_list)
        print('please put header of structure',expected_list,\
              'as the first line in the file')
        return None
    
    portorders = []
    datepos = 0
    sympos = 1
    buypos = 2
    sharepos = 3
    for line in by_line[1:]:
        if not len(line)<1:
            templine = line.split(',')
            tempdate = templine[datepos]
            tempsym = templine[sympos]
            if templine[buypos] == 'BUY':
                buy = True
            elif templine[buypos] == 'SELL':
                buy = False
            else:
                print('unable to parse a buy or sell, terminating')
                return None
            tempshares = int(templine[sharepos])
            portorders.append([tempdate, tempsym, buy, tempshares])
    portsorted = sorted(portorders, key=lambda portorders: portorders[0])
    portorders = portsorted
    
    if VERBOSE:
        print('printing the sorted list of orders')
        for i in range(len(portorders)):
            print(portorders[i])
            #if i<len(portorders)-1:
            #    print(portorders[i][datepos] < portorders[i+1][0])
    
    if len(portorders)>0:
        #starting to compute the orders
        start_date = portorders[0][datepos]
        
        end_date = portorders[len(portorders)-1][datepos]

        i=0
        cash=start_val
        syms = []
        shares = []
        buys = []
        while i<len(portorders):
            syms.append(portorders[i][sympos])
            shares.append(portorders[i][sharepos])
            buys.append(portorders[i][buypos])
            #temporary start date
            sd = portorders[i][datepos]
            while i<len(portorders)-1 and not \
                portorders[i][datepos]<portorders[i+1][datepos]:
                #combine multiple syms when the next time frame is the same
                i+=1
                syms.append(portorders[i][sympos])
                shares.append(portorders[i][sharepos])
                buys.append(portorders[i][buypos])
            if i<len(portorders)-1:
                ed = portorders[i+1][datepos]
            else:
                #the final value of the portorders
                ed = portorders[i][datepos]
                
            
            port_temp, cash, syms, shares = extract_orders(sd=sd, \
                           ed=ed, syms=syms, shares=shares, \
                           cash=cash, buys=buys, rfr=0, sf=252.0, \
                           commission=9.95, mimpact=0.005)
            buys = []
            for j in range(len(syms)):
                buys.append(None)
            if sd == start_date:
                portvals = port_temp
                if VERBOSE:
                    print('portvals')
                    print(portvals.iloc[0])
                    print(portvals.iloc[len(portvals)-1])
            else:
                
                portvals = portvals.iloc[:len(portvals)-1].append(port_temp)
                
                #portvals = pd.concat(portvals.iloc[:len(portvals)-1], port_temp)
                
                #portvals = pd.concat(portvals, port_temp) #will likely need to be
                if VERBOSE:
                    print('after adding portvals')
                    print(portvals.iloc[0])
                    print(portvals.iloc[len(portvals)-1])
                    print(port_temp.iloc[0])
                    print(port_temp.iloc[len(port_temp)-1])
                
            i+=1
            
        
        
    else:
        portvals = pd.DataFrame([[start_val]])
        return portvals
    
    daily_rets = portvals/portvals.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    
    cr = portvals[len(portvals.index) - 1]/portvals[0] - 1 #portval.length?  
    adr = daily_rets.mean() #check that avg. daily return is correct
    sddr = daily_rets.std()
    sr = adr/sddr
    ev = portvals[len(portvals.index) - 1]
    
    if VERBOSE:
        print ("Date Range: {} to {}".format(start_date, end_date))
    
#         print ("Symbols:", syms)
#        print ("Shares:", init_shares)
#        print ("Buys:", init_buys)
        print ("Sharpe Ratio:", sr)
        print ("Volatility (stdev of daily returns):", sddr)
        print ("Average Daily Return:", adr)
        print ("Cumulative Return:", cr)
        print ("End Value:", ev)
    
    # TODO: Your code here

    # In the template, instead of computing the value of the portfolio, we just
    # read in the value of IBM over 6 months
    
    #start_date = dt.datetime(2008,1,1)
    #end_date = dt.datetime(2008,6,1)
    #portvals = get_data(['IBM'], pd.date_range(start_date, end_date))
    #print(portvals)
    #portvals = portvals[['IBM']]  # remove SPY

    return portvals

def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./orders/orders-short.csv"  #orders2.csv
    file = of
    sv = 1000000
    
    parser = argparse.ArgumentParser()
    
    #parser.add_argument( '-p', action="store_true", dest="plot", default=False )
    #parser.add_argument( '-s', action="store", dest="start_date",default=start_date )
    #parser.add_argument( '-e', action="store", dest="end_date",default=end_date )
    #parser.add_argument( '-x', nargs='*',action="store", dest="symbols",default=symbols )
    parser.add_argument( '-f', action="store", dest="file",default=file)
    parser.add_argument( '-v', action="store", type=float, dest="start_value", default=sv)#nargs='*',

    args = parser.parse_args()
    
    file = args.file
    sv = args.start_value
    
    # Process orders
    portvals = compute_portvals(orders_file = file, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"
    
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = portvals.index[0]
    end_date = portvals.index[len(portvals)-1]

    date_range = pd.date_range(start_date, end_date)
    spysym = '$SPX'
    SPYdata = get_data(symbols = [spysym], dates = date_range)
    SPYport = SPYdata[spysym]
    daily_rets = portvals/portvals.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    daily_rets_SPY = SPYport/SPYport.shift(1) - 1
    
    sharpe_daily_rfr = 0.0000
    sr_annualized = math.sqrt(252)
    
    cum_ret = portvals[len(portvals.index) - 1]/portvals[0] - 1 #portval.length?  
    avg_daily_ret = daily_rets.mean() #check that avg. daily return is correct
    std_daily_ret = daily_rets.std()
    sharpe_ratio = sr_annualized*\
        (avg_daily_ret-sharpe_daily_rfr)/(std_daily_ret-sharpe_daily_rfr)
    
    cum_ret_SPY = SPYport[len(SPYport.index) - 1]/SPYport[0] - 1 #portval.length?  

    avg_daily_ret_SPY = daily_rets_SPY.mean() #check that avg. daily return is correct
    std_daily_ret_SPY = daily_rets_SPY.std()
    sharpe_ratio_SPY = sr_annualized*\
        (avg_daily_ret_SPY-sharpe_daily_rfr)/(std_daily_ret_SPY-sharpe_daily_rfr)
    
#    start_date = dt.datetime(2008,1,1)
#    end_date = dt.datetime(2008,6,1)
#    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
#    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    # Compare portfolio against $SPX
    print ("Date Range: {} to {}".format(start_date, end_date))
    print
    print ("Sharpe Ratio of Fund: {}".format(sharpe_ratio))
    print ("Sharpe Ratio of {} : {}".format(spysym, sharpe_ratio_SPY))
    print
    print ("Cumulative Return of Fund: {}".format(cum_ret))
    print ("Cumulative Return of {}: {}".format(spysym, cum_ret_SPY))
    print
    print ("Standard Deviation of Fund: {}".format(std_daily_ret))
    print ("Standard Deviation of {}: {}".format(spysym, std_daily_ret_SPY))
    print
    print ("Average Daily Return of Fund: {}".format(avg_daily_ret))
    print ("Average Daily Return of {}: {}".format(spysym, avg_daily_ret_SPY))
    print
    print ("Final Portfolio Value: {}".format(portvals[-1]))
    print
#    print ('final portfolio:')
#    print (portvals.index[0])

if __name__ == "__main__":
    test_code()
