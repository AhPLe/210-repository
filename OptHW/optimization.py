"""important message: Save the Camels!
Also I have been unable to see any camels in the code
MC2-P1: Market simulator."""
import pandas as pd
import numpy as np
import datetime as dt
import sys
import math
import argparse
import apl_001_minimizer as apl_min
from util import get_data, plot_data
import time

VERBOSE = False
VERY_VERBOSE = True


def minimize_sharpe(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
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

    sym_vals = prices*(shares)
    normed_vals = sym_vals/sym_vals.iloc[0]
    port_val = sym_vals.sum(axis=1) + cash
    
    
    normed_SPY = prices_SPY/prices_SPY.iloc[0]
    
    daily_rets = port_val/port_val.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    

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
        print ("End Value:", ev)
    
    return port_val, cash, syms, shares

def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
           syms=['GOOG','AAPL','GLD','XOM'], gen_plot=False):
    
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    
    #check that all numbers obtained are valid
    
    for i in range(len(syms) - 1, -1, -1):   
        if prices_all[syms[i]].isnull().values.any():
                print('unable to obtain values for:', syms[i])
                syms.pop(i)
    
    allocs = [1/len(syms) for _ in range(len(syms))]
    #allocs=[0.1,0.2,0.3,0.4]
    sv=1000000
    rfr=0.0
    sf=252.0
    
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value

    # Get portfolio statistics (note: std_daily_ret = volatility)
    
    port_val = prices_SPY # add code here to compute daily portfolio values

    if VERBOSE:
        print(port_val)
    
    normed = prices/prices.iloc[0]
    if len(syms)<2:
        print('not enough allocations')
        return None
    
    #sym_adr = []
    #sym_sddr = []
    #sym_rfr = []
    df_names = ['alloc', 'mean', 'stdev', 'rfr']
    syms_df = pd.DataFrame([[]])
    #for i in range(len(syms_df)):
    #    print('i is ', i, ':', syms_df.iloc[i])
    
    assigned = False
    for i in range(len(syms)):
        sym_val = normed[syms[i]]
        sym_daily_rets = sym_val/sym_val.shift(1) - 1
        sym_adr=sym_daily_rets.mean()
        sym_sddr=sym_daily_rets.std()
        sym_rfr=rfr
        sym_df = pd.DataFrame([[allocs[i], sym_adr, sym_sddr, sym_rfr]], index=[syms[i]], columns=df_names)
        if not assigned:
            syms_df = sym_df
            assigned = True
        else:
            syms_df = pd.concat([syms_df, sym_df])
    program_start = time.time()
            
    minima = apl_min.create_function(syms_df)
    program_end = time.time()
    if VERY_VERBOSE:
        print('time to complete at {} syms, {}'.format(len(syms), program_end-program_start))
    #index1, index2, alloc1 = apl_min.sharpeminima(syms_df)
    
    
    if VERBOSE:
        print(minima)
        print('ratio amount {}: {}'.format(syms, minima.x))
    
    alloced = normed*allocs
    pos_vals = alloced*sv
    port_val = pos_vals.sum(axis=1)
    normed_SPY = prices_SPY/prices_SPY.iloc[0]
    
    daily_rets = port_val/port_val.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    
    allocs_imp = minima.x
#    for i in range(len(syms)):
#        if i == index1:
#            allocs_imp.append(alloc1)
#        elif i == index2:
#            allocs_imp.append(1-alloc1)
#        else:
#            allocs_imp.append(0)
    
    alloced_imp = normed*allocs_imp
    pos_vals_imp = alloced_imp*sv
    port_val_imp = pos_vals_imp.sum(axis=1)
    
    daily_rets_imp = port_val_imp/port_val_imp.shift(1) - 1 #by 1 row, subtracted by 1 to view change    
    
    ev = port_val[len(pos_vals.index) - 1]
    ev_imp  = port_val_imp [len(pos_vals_imp.index) - 1]

    cr = ev/port_val[0] - 1 #portval.length?  
    cr_imp = ev/port_val_imp[0] - 1 #portval.length?  

    adr = daily_rets.mean() #check that avg. daily return is correct
    adr_imp = daily_rets_imp.mean() #check that avg. daily return is correct

    sddr = daily_rets.std()
    sddr_imp = daily_rets_imp.std()

    sr_annualized = math.sqrt(sf)

    sr = sr_annualized*(adr-rfr)/(sddr-rfr)
    sr_imp = sr_annualized*(adr_imp-rfr)/(sddr_imp-rfr)

    # Compare daily portfolio value with SPY using a normalized plot
    
    
    
    if gen_plot:
        # add code to plot here
        #plot_data( normed, title="Normalized Stock Prices", ylabel="Normalized price")
        #df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
        df_temp = pd.concat([port_val/sv, port_val_imp/sv, normed_SPY], keys=['Portfolio', 'Improved Portfolio', 'SPY'], axis=1)
        #df_temp = pd.concat([normed_SPY], keys=['Portfolio', 'SPY'], axis=1)
        
        #df_temp = pd.concat([port_val], keys=['Portfolio', 'SPY'], axis=1)
        
        #plot_data([port_val, prices_SPY], title="Daily portfolio value and SPY", ylabel="Normalized price")
        plot_data(df_temp, title = 'Daily portfolio values and SPY', ylabel = 'Normalized price')
        pass

    # Add code here to properly compute end value
    
    print('final note: save the bactrians, who are not a dromedary species \
          (although thay are an ungulate)!')
    #if VERY_VERBOSE:
    #    print('time of program: {} seconds'.format(program_end - program_start))
    return allocs_imp, cr_imp, adr_imp, sddr_imp, sr_imp


def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters
    
    # numsyms = ['GOOG', 'AAPL', 'GLD', 'XOM', 'ADI', 'BAX', 'BCR', 'BBBY',\
    #           'BLK', 'BK', 'BLL', 'BMC', 'BMS', 'BMY', 'C', 'CAT', 'CBE',\
    #               'CBS', 'CCL', 'DELL', 'EBAY', 'EA', 'IBM', 'INTU', 'INTC',\
    #                   'IP', 'JAVA', 'NBL', 'NBR', 'NCC', 'NKE', 'PBI', 'PCG',\
    #                       'PCL', 'PCLN', 'PFE', 'PFG', 'PNW', 'PPL', 'THC',\
    #                           'USB', 'T', 'X', 'YUM']
    numsyms = ['GOOG','XOM', 'FMCC', 'FNMA', 'A', 'AA', 'AAPL', 'ABC', 'ABI', 'ABKFQ', 'ABT', 'ACAS', 'ACE', 'ACS', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AES', 'AET', 'AFL', 'AGN', 'AIG', 'AIV', 'AIZ', 'AKAM', 'ALL', 'ALTR', 'AMAT', 'AMD', 'AMGN', 'AMP', 'AMT', 'AMZN', 'AN', 'ANF', 'AON', 'APA', 'APC', 'APD', 'APOL', 'ASH', 'ATI', 'AVB', 'AVP', 'AVY', 'AXP', 'AYE', 'AZO', 'BA', 'BAC', 'BAX', 'BBBY', 'BBT', 'BBY', 'BC', 'BCR', 'BDK', 'BDX', 'BEAM', 'BEN', 'BF.B', 'BHI', 'BIG', 'BIIB', 'BJS', 'BK', 'BLL', 'BMC', 'BMS', 'BMY', 'BRCM', 'BRK.B', 'BRLI', 'BSC', 'BSX', 'BTU', 'BUD', 'BXP', 'C', 'CA', 'CAG', 'CAH', 'CAT', 'CB', 'CBE', 'CBG', 'CBSH', 'CBS', 'CCE', 'CCL', 'CCMO', 'CEG', 'CELG', 'CFC+A', 'CHK', 'CHRW', 'CI', 'CIEN', 'CINF', 'CIT', 'CL', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMI', 'CMS', 'CNP', 'CNX', 'COF', 'COH', 'COL', 'COP', 'COST', 'COV', 'CPB', 'CPWR', 'CSC', 'CSCO', 'CSX', 'CTAS', 'CTL', 'CTSH', 'CTX', 'CTXS', 'CVG', 'CVH', 'CVS', 'CVX', 'D', 'DD', 'DDR', 'DDS', 'DE', 'DELL', 'DF', 'DFS', 'DGX', 'DHI', 'DHR', 'DIS', 'DOV', 'DOW', 'DRI', 'DTE', 'DTV', 'DUK', 'DVN', 'DYN', 'EBAY', 'ECL', 'ED', 'EDS', 'EFX', 'EIX', 'EK', 'EL', 'EMC', 'EMN', 'EMR', 'EOG', 'EP', 'EQ', 'EQR', 'ERTS', 'ESRX', 'ESV', 'ETFC', 'ETN', 'ETR', 'EXC', 'EXPD', 'EXPE', 'F', 'FCX', 'FDO', 'FDX', 'FE', 'FHN', 'FII', 'FIS', 'FISV', 'FITB', 'FLR', 'FRX', 'FTR', 'GAS', 'GCI', 'GD', 'GE', 'GENZ', 'GGP', 'GILD', 'GIS', 'GLW', 'GM', 'GME', 'GNW', 'GPC', 'GPS', 'GR', 'GS', 'GT', 'GWW', 'HAL', 'HAR', 'HAS', 'HBAN', 'HCBK', 'HD', 'HES', 'HIG', 'HNZ', 'HOG', 'HON', 'HOT', 'HPQ', 'HRB', 'HSP', 'HST', 'HSY', 'HUM', 'IACI', 'IBM', 'ICE', 'IFF', 'IGT', 'INTC', 'INTU', 'IP', 'IPG', 'IR', 'ITT', 'ITW', 'JAVA', 'JBL', 'JCI', 'JCP', 'JDSU', 'JEC', 'JNJ', 'JNPR', 'JNS', 'JNY', 'JPM', 'JWN', 'K', 'KBH', 'KEY', 'KFT', 'KG', 'KIM', 'KLAC', 'KMB', 'KO', 'KR', 'KSS', 'L', 'LEG', 'LEHMQ', 'LEN', 'LH', 'LIZ', 'LLL', 'LLTC', 'LLY', 'LM', 'LMT', 'LNC', 'LOW', 'LSI', 'LTD', 'LUK', 'LUV', 'LXK', 'M', 'MAR', 'MAS', 'MAT', 'MBI', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDP', 'MDT', 'MET', 'MHP', 'MHS', 'MI', 'MIL', 'MKC', 'MMC', 'MMM', 'MO', 'MOLX', 'MON', 'MRK', 'MRO', 'MS', 'MSFT', 'MSI', 'MTB', 'MTG', 'MTW', 'MU', 'MUR', 'MWV', 'MWW', 'MYL', 'NBL', 'NBR', 'NCC', 'NE', 'NEE', 'NEM', 'NI', 'NKE', 'NOC', 'NOV', 'NOVL', 'NSC', 'NSM', 'NTAP', 'NTRS', 'NUE', 'NVDA', 'NVLS', 'NWL', 'NWSA', 'NYT', 'NYX', 'ODP', 'OMC', 'OMX', 'ORCL', 'OXY', 'PAYX', 'PBG', 'PBI', 'PCAR', 'PCG', 'PCL', 'PCP', 'PDCO', 'PEG', 'PEP', 'PFE', 'PFG', 'PG', 'PGN', 'PGR', 'PH', 'PHM', 'PKI', 'PLD', 'PLL', 'PNC', 'PNW', 'POM', 'PPG', 'PPL', 'PRU', 'PSA', 'PTV', 'PX', 'Q', 'QCOM', 'QLGC', 'R', 'RAI', 'RDC', 'RF', 'RHI', 'RIG', 'RL', 'ROH', 'ROK', 'RRC', 'RRD', 'RSH', 'RTN', 'S', 'SAF', 'SBUX', 'SCHW', 'SE', 'SEE', 'SGP', 'SHLD', 'SHW', 'SIAL', 'SII', 'SLB', 'SLE', 'SLM', 'SNA', 'SNDK', 'SNV', 'SO', 'SPG', 'SPLS', 'SRE', 'SSP', 'STI', 'STJ', 'STR', 'STT', 'STZ', 'SUN', 'SVU', 'SWK', 'SWY', 'SYK', 'SYMC', 'SYY', 'T', 'TAP', 'TDC', 'TE', 'TEG', 'TEL', 'TER', 'TEX', 'TGT', 'THC', 'TIE', 'TIF', 'TJX', 'TLAB', 'TMK', 'TMO', 'TROW', 'TRV', 'TSN', 'TSO', 'TWX', 'TXN', 'TXT', 'TYC', 'UIS', 'UNH', 'UNM', 'UNP', 'UPS', 'USB', 'UST', 'UTX', 'VAR', 'VFC', 'VIA.B', 'VLO', 'VMC', 'VNO', 'VRSN', 'VZ', 'WAG', 'WAMUQ', 'WAT', 'WB', 'WEN', 'WFC', 'WFM', 'WFR', 'WFT', 'WHR', 'WIN', 'WLP', 'WM', 'WMB', 'WMT', 'WPI', 'WPO', 'WU', 'WWY', 'WY', 'WYE', 'WYN', 'X', 'XEL', 'XL', 'XLNX', 'XRX', 'XTO', 'YHOO', 'YUM', 'ZION', 'ZMH']
          
    
    of = "./orders/orders-short.csv"  #orders2.csv
    file = of
    sv = 1000000
    start_date=dt.datetime(2008,1,1)
    end_date=dt.datetime(2009,1,1)
    symbols=['GOOG','AAPL','GLD','XOM']
    gen_plot=False
    numsymbols = 4
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument( '-p', action="store_true", dest="plot", default=gen_plot )
    parser.add_argument( '-s', action="store", dest="start_date",default=start_date )
    parser.add_argument( '-e', action="store", dest="end_date",default=end_date )
    parser.add_argument( '-x', nargs='*',action="store", dest="symbols",default=symbols )
    parser.add_argument( '-n', action="store", type=int, dest="numsymbols",default=numsymbols )
    #parser.add_argument( '-f', action="store", dest="file",default=file)
    parser.add_argument( '-v', action="store", type=float, dest="start_value", default=sv)#nargs='*',

    args = parser.parse_args()

    #file = args.file
    sv = args.start_value
    start_date=args.start_date
    end_date=args.end_date
    symbols=args.symbols
    gen_plot=args.plot
    
    loop = False
    if numsymbols!=args.numsymbols: #if the number of symbols is different from the default
        num = min(len(numsyms), args.numsymbols)
        numsymbols=num
        loop = True
    
    
    # Process orders
    if loop:
        times = []
        #for i in range(2, numsymbols, 100):
        for i in range(numsymbols-1, numsymbols):
            
            symbols = []
            for j in range(i):
                symbols.append(numsyms[j])
            
            program_start = time.time()
            allocs, cr, adr, sddr, sr = optimize_portfolio(sd=start_date, ed=end_date, \
                   syms=symbols, gen_plot=gen_plot)
            program_end = time.time()
            times.append(program_end - program_start)
        print('times are:')
        print(times)
    
    else:
        program_start = time.time()
        
        allocs, cr, adr, sddr, sr = optimize_portfolio(sd=start_date, ed=end_date, \
               syms=symbols, gen_plot=gen_plot)
        program_end = time.time()
        if VERY_VERBOSE:
            program_time = program_end - program_start
            print('the time for the program to complete was: {}'.format(program_time))
        

    # portvals = minimize_portfolio(sd = dt.datetime(2011,1,1), ed = dt.datetime(2012,1,1), \
    #     syms = ['GOOG','AAPL','GLD','XOM'], \
    #     allocs=[0.1,0.2,0.3,0.4], \
    #     sv=1000000, rfr=0.0, sf=252.0, \
    #     gen_plot=False)
    
    #portvals = compute_portvals(orders_file = file, start_val = sv)
    # if isinstance(portvals, pd.DataFrame):
    #     portvals = portvals[portvals.columns[0]] # just get the first column
    # else:
    #     "warning, code did not return a DataFrame"
    
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    # start_date = portvals.index[0]
    # end_date = portvals.index[len(portvals)-1]

    date_range = pd.date_range(start_date, end_date)
    spysym = '$SPX'
    SPYdata = get_data(symbols = [spysym], dates = date_range)
    SPYport = SPYdata[spysym]
    # daily_rets = portvals/portvals.shift(1) - 1 #by 1 row, subtracted by 1 to view change
    daily_rets_SPY = SPYport/SPYport.shift(1) - 1
    
    sharpe_daily_rfr = 0.0000
    sr_annualized = math.sqrt(252)
    
    # cum_ret = portvals[len(portvals.index) - 1]/portvals[0] - 1 #portval.length?  
    # avg_daily_ret = daily_rets.mean() #check that avg. daily return is correct
    # std_daily_ret = daily_rets.std()
    # sharpe_ratio = sr_annualized*\
    #     (avg_daily_ret-sharpe_daily_rfr)/(std_daily_ret-sharpe_daily_rfr)
    
    cum_ret_SPY = SPYport[len(SPYport.index) - 1]/SPYport[0] - 1 #portval.length?  

    avg_daily_ret_SPY = daily_rets_SPY.mean() #check that avg. daily return is correct
    std_daily_ret_SPY = daily_rets_SPY.std()
    sharpe_ratio_SPY = sr_annualized*\
        (avg_daily_ret_SPY-sharpe_daily_rfr)/(std_daily_ret_SPY-sharpe_daily_rfr)
    
#    start_date = dt.datetime(2008,1,1)
#    end_date = dt.datetime(2008,6,1)
#    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
#    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    # Compare portfolio against $SPX]
    
    print ("Date Range: {} to {}".format(start_date, end_date))
    print
    print ("Sharpe Ratio of Fund: {}".format(sr))
    print ("Sharpe Ratio of {} : {}".format(spysym, sharpe_ratio_SPY))
    print
    print ("Cumulative Return of Fund: {}".format(cr))
    print ("Cumulative Return of {}: {}".format(spysym, cum_ret_SPY))
    print
    print ("Standard Deviation of Fund: {}".format(sddr))
    print ("Standard Deviation of {}: {}".format(spysym, std_daily_ret_SPY))
    print
    print ("Average Daily Return of Fund: {}".format(adr))
    print ("Average Daily Return of {}: {}".format(spysym, avg_daily_ret_SPY))
    print
    print ("Symbols: {}".format(symbols))
    print ("Final Allocations: {}".format(allocs))
    print
#    print ('final portfolio:')
#    print (portvals.index[0])

if __name__ == "__main__":
    test_code()
