Initial readme of project -
Short instructions - run HashSim_MultiEx.py
Many things were attempted, but this is a short writeup of the initial readme file. While very surface changes have been implemented, there are a large number of attempted and improved features in the program. There are more arguments, including an executive argument (think cities instead of airports), and there is some switching of LPs from one city to another. This is also something that is configurable. All cities are alike, and all features are alike, but it is randomized.
There is a seed feature, which is improved but still not successful using the hash implementation. While initial trials suggested this was fixed, after completing the multiple executives, the random feature was found to be erratic to a degree (with small numbers, you can rediscover similar trials if repeatedly running the trials). This backtrack is also why this project feels unfinished. Because the randomness stopped working, I spend time modifying the random feature to create randomness directly from the timeline instead of repeatedly running simulations to a certain point. This also probably helps with the random variability between the runs.

    parser.add_argument('-dr0', action="store", dest="dr0",  # no double type in python, only numpy
                        default=1.5,   type=float)  # stores the r0, the d is meant to allow differentiation
    # from r, so it will always be different instead of -r storing for -r0
    parser.add_argument('-dinfected', action="store", dest="dinfected",
                        default=0.05,	type=float)  # stores initial percentage of infected
    parser.add_argument('-dlength_time', action="store", dest="dlength_time",
                        default=4,	type=int)  # time spent having the disease
    parser.add_argument('-dsick', action="store", dest="dsick",
                        default=0.2,	type=float)  # percent once infected get sick
    parser.add_argument('-ddead', action="store", dest="ddead",
                        default=0.1,	type=float)  # percent that die once sick
    parser.add_argument('-use_area', action="store_true", dest="use_area",
                        default=False)  # percent that die once sick
    parser.add_argument('-switch', action="store", dest="switch",
                        default=0.01, type=float)  # percent that switch executives
    
    parser.add_argument('-iplot', action="store_true", dest="iplot")  # shows the attempt at individual plots

    parser.add_argument('-r', action="store", dest="random_Seed",
                        default=42,	type=int)
    parser.add_argument('-s', action="store", dest="sim_Time",
                        default=5, 	    type=int)
    parser.add_argument('-f', action="store_true", dest="fixed_latency",
                        default=True)
    parser.add_argument('-k', action="store", dest="lim_Latency",
                        default=1,   type=int)
    parser.add_argument('-v', action="store_true",
                        dest="VERBOSE", default=False)
    parser.add_argument('-p', action="store",
                        dest="processes", default=2,   type=int)
    parser.add_argument('-x', action="store", dest="num_executives",
                        default=1,	type=int)

This is the full list of arguments. The new ones to note are -x, which implements more than one executive, -iplot which shows the attempt at an individual plot, use-area which allows the simplistic area feature to be turned on or off, and possibly -ddead which creates a percentage of sick agents into dead agents and removes them from the executive.