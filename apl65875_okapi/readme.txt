APL65875 - Arthur LeBlanc, 6210 Simulation and Modeling class
The provided agent has small changes to the original SimpleAgent.py class. This agent removes the randomization and only places the max possible bid instead of a number between the min and max bid. If a stock is triggered to buy, it buys the maximum possible stock it is able to with cash on hand directly, instead of using the maximum bid each time and if that bid is not possible, doing nothing.
Bollinger bands in tandem with the Simple_Agent produced very low results, and even had losses in some small band cases. The agent described was not included in the zipped folder.
Simple_agent looks at a spread between (EDIT) window 1 and window 2 and buys stock if it is at window1 and sells if it is in window2. The agent takes prices once a minute and dumps stock with 25 minutes left. This could be improved to sell stock at 1 minute left with a caveat of only selling once the price starts to dip with  exponential average window or at the five minute/one minute mark regardless. 


There are two provided agents. The important one is apl65875_okapi. That is an improved version of SimpleAgent.py. It removes the randomization present in a possible max bid, and always bets everything it can on the stock if betting is possible. In the original SimpleAgent, there may be a time when stock could be bought, but there was not enough cash to implement the order of max*number of shares. This agent overcomes that. It might be possible to optimize further with checking if more useful orders were possible, but the time scale is probably small enough to not make much of a difference.

Simple_Agent looks at the average price of the stocks to start with. Once there have been 25 samples, the Agent starts taking weighted averages (exponential weighted averages weighted towards the most recent), and if the price is falling it tries to sell if possible. If it's rising it tries to buy if possible.

apl65875_tapir just implements bollinger bands. It turns out they are awful for trading in a single day. It could make a slight bit of money if optimized to a certain band width, but it just doesn't compare to Simple_Agent.


