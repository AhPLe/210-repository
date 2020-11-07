This file calculates the value of a portfolio over a period of time. This file reads in a list of BUY and SELL orders into marketsim.py.
The BUY and SELL orders are in a specific format that includes date, stock, BUY or SELL, and number of shares.
The file will then calculate the portfolio price over the range of dates and return the value.
If the program is run as the main program, it will give a list of figures about the portfolio including Sharpe ratio (yearly), start date, end date, daily average, daily standard deviation, and end price. These will be compared to the $SPX (S&P 500 stock).
The program, if run as the main program, will include possible args values including -f for file and -v for starting value, defaults are -f ./orders/orders-short.csv and -v 1000000

code for running with the command line includes
-f "./orders/orders-short.csv"
-f "./orders/orders.csv"
-f "./orders/orders2.csv"

from above description, both parts A and B were completed. optimization is not due just yet

Checklist:
Part A:
api implemented for compute_portvals
able to read in an order_file
returns portval dataframe containing value of portfolio at each date

Part B:
Commissions and Market Impact included in price changes
output checked on orders.csv, orders2.csv, orders-short.csv