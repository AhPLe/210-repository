# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 16:17:02 2020
@author: arthu
"""
"""
Carwash example.
Covers:
- Waiting for other processes
- Resources: Resource
Scenario:
  A carwash has a limited number of washing machines and defines
  a washing processes that takes some (random) time.
  Car processes arrive at the carwash at a random time. 
  If one washing machine is available, they start the washing process and wait for it
  to finish. If not, they wait until they an use one.
"""

import random
import simpy
import argparse
import sys
import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from matplotlib import pyplot

RANDOM_SEED = 42
NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5  # Minutes it takes to clean a car
T_INTER = 3  # Create a car every ~7 minutes
SIM_TIME = 20  # Simulation time in minutes

NUM_CAR_INIT = 2  # Initial number of cars
NUM_TOTAL_CARS = 15 # Total number of cars
DELTA = 1 	# RANDOMNESSINTERVAL generating cars
COL = '1'
VERBOSE = True
VERBOSE_HIGH = True
BALK_NUM = 4 # past this number cars will go elsewhere
PEAKS = 2 # number of poisson distribution peaks
CUSTOMERS_LOST = 0

rng = np.random.default_rng(seed=RANDOM_SEED)

CAR_DIST = []

def generate_poisson(PEAKS): # generates a poisson distribution, 
#div # creates multiple distributions equally throughout the SIM_TIME
    global CAR_DIST
    rng = np.random.default_rng(seed=RANDOM_SEED)
    CAR_DIST = []
    temp_np_dist = np.empty(0, int) #define tuple for time, number of cars
    temp_total = NUM_TOTAL_CARS
    temp_total = math.floor(NUM_TOTAL_CARS/(PEAKS)) + NUM_TOTAL_CARS%(PEAKS)
    peak_times = []
    dist = []
    for i in range(PEAKS):
        peak_times.append(SIM_TIME*(i+1)/(PEAKS+1))
        dist.append(rng.poisson(lam=int(SIM_TIME*(i+1)/(PEAKS+1)), size=math.floor(temp_total \
                                                                 if i==0 else NUM_TOTAL_CARS/(PEAKS))))        
        temp_np_dist = np.concatenate((temp_np_dist, dist[i]), axis = None)
    temp_np_dist = np.sort(temp_np_dist)
    if (VERBOSE):
        for i in range(len(dist)):
            print('time peak {:.2f} has cars at times:'.format(peak_times[i]))
            print(dist[i])
    j = 0
    count = 1
    ARRAY_TIME = 0 #not really sure if this is good practice, or to be avoided
    #it should probably be global too, but again, not completely sure
    CARS_AT_TIME = 1
    if len(temp_np_dist)>j:
        CAR_DIST.append((temp_np_dist[j], count))
    for i in range (1, len(temp_np_dist)):
        if temp_np_dist[i] == CAR_DIST[j][ARRAY_TIME]:
            CAR_DIST[j] = (CAR_DIST[j][ARRAY_TIME], CAR_DIST[j][CARS_AT_TIME] + 1)
        else:
            j += 1
            count = 1
            CAR_DIST.append((temp_np_dist[i], count)) 
    if (VERBOSE):
        print('sorted list of all cars (time, number of cars):')
        print(CAR_DIST)

    
class Carwash(object):
    """A carwash has a limited number of machines (``NUM_MACHINES``) to
    clean cars in parallel.
    Cars have to request one of the machines. When they got one, they
    can start the washing processes and wait for it to finish (which
    takes ``washtime`` minutes).
    """

    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime

    def wash(self, car):
        """The washing processes. It takes a ``car`` processes and tries to clean it."""
        yield self.env.timeout(WASHTIME)
        if(VERBOSE):
            print("Carwash removed %d%% of %s's dirt." %
                  (random.randint(50, 99), car))


def car(env, name, cw):
    """The car process (each car has a ``name``) arrives at the carwash
    (``cw``) and requests a cleaning machine.
    It then starts the washing process, waits for it to finish and
    leaves to never come back ...
    """

    # hackie.
    global numOfCars
    global VERBOSE
    global VERBOSE_HIGH
    global CUSTOMERS_LOST
    numOfCars = numOfCars + 1
    dfLine.at[env.now, COL] = numOfCars

    if(VERBOSE_HIGH):
        print('%s arrives at the carwash at %.2f. Car Length = %d' %
              (name, env.now, numOfCars))
    
    if BALK_NUM > -1 and numOfCars > BALK_NUM:
        if(VERBOSE_HIGH):
            print('%s balks at the long carwash line at     %.2f.' % (name, env.now))
        numOfCars = numOfCars - 1
        CUSTOMERS_LOST += 1
    else:
        with cw.machine.request() as request:
    
            yield request
    
            if(VERBOSE_HIGH):
                print('%s enters the carwash at     %.2f.' % (name, env.now))
    
            numOfCars = numOfCars - 1
            if pd.isnull(dfLine.at[env.now, COL]):
                dfLine.at[env.now, COL] = numOfCars
            else:
                dfLine.at[env.now, COL] = dfLine.at[env.now, COL] - 1
    
            yield env.process(cw.wash(name))
    
            if(VERBOSE_HIGH):
                print('%s leaves the carwash at     %.2f.' % (name, env.now))


def setup(env, num_machines, washtime, t_inter):
    """Create a carwash, a number of initial cars and keep creating cars
    approx. every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    # this is confusing - should only  REALLY create 1 car initially
    # Create 1 initial cars -> not 4.
    generate_poisson(PEAKS)
    
    j= 0
    CARS = NUM_CAR_INIT
    global CUSTOMERS_LOST
    CUSTOMERS_LOST = 0

    if len(CAR_DIST)>0 and CAR_DIST[0][0] == 0:
        CARS += CAR_DIST[0][1] #add the number of poisson distributed cars at time 0
        j += 1
        
    
    if(VERBOSE):
        print('Initial number of CARS: %d' % (CARS))
    for i in range(CARS):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    if len(CAR_DIST)>0:
        yield env.timeout(CAR_DIST[i][0])
    
    while True:
        # randomly generated cars.
        # yield env.timeout( random.randint(t_inter - 2, t_inter + 2) )
        # removes the randomness
        if (i<len(CAR_DIST) - 1):
            yield env.timeout(CAR_DIST[j + 1][0] - CAR_DIST[j][0])
        else:
            yield env.timeout(SIM_TIME - CAR_DIST[j][0] + 1) #should probably remove +1 later
        j += 1
        for k in range (CAR_DIST[j][1]):
            i += 1
            env.process(car(env, 'Car %d' % i, carwash))
        
        # yield env.timeout(random.randint(t_inter - DELTA, t_inter + DELTA))
        # i += 1
        # env.process(car(env, 'Car %d' % i, carwash))

# --------------------------------- color the plots


def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)


# --------------------------------- testing these
if(False):
    print ("3.\npython carwash.py -r 350 -m 2 -w 5 -t 4 -s 500")
    print ("4.\npython carwash.py -r 350 -m 1 -w 5 -t 4 -s 500")
    print ("5.\npython carwash.py -r 350 -m 0 -w 5 -t 4 -s 500")
    print ("6.\npython carwash.py -r 350 -m 3 -w 10 -t 4 -s 500")
    print ("7.\npython carwash.py -r 350 -m 2 -w 10 -t 4 -s 500")
    print ("8.\npython carwash.py -r 350 -m 1 -w 10 -t 4 -s 500")
    print ("XXX.\npython carwash.py -r 350 -m 2 -w 5 -t 4 -s 500 -d 0 -c 1")
parser = argparse.ArgumentParser()
parser.add_argument('-r', action="store", dest="RANDOM_SEED",
                    default=RANDOM_SEED,	type=int)
parser.add_argument('-m', action="store", dest="NUM_MACHINES",
                    default=NUM_MACHINES, 	type=int)
parser.add_argument('-w', action="store", dest="WASHTIME",
                    default=WASHTIME, 		type=int)
parser.add_argument('-t', action="store", dest="T_INTER",
                    default=T_INTER, 		type=int)
parser.add_argument('-s', action="store", dest="SIM_TIME",
                    default=SIM_TIME, 		type=int)
parser.add_argument('-c', action="store", dest="NUM_CAR_INIT",
                    default=NUM_CAR_INIT, 	type=int)
parser.add_argument('-d', action="store", dest="DELTA",
                    default=DELTA, 			type=int)
parser.add_argument('-v', action="store_false", dest="VERBOSE", default=True)
parser.add_argument('-vh', action="store_false", dest="VERBOSE_HIGH", default=True)
parser.add_argument('-p', action="store", dest="PEAKS",
                    default=PEAKS, 			type=int)
parser.add_argument('-n', action="store", dest="NUM_TOTAL_CARS",
                    default=NUM_TOTAL_CARS,    type=int)
parser.add_argument('-b', action="store", dest="BALK_NUM",
                    default=BALK_NUM,    type=int)
args = parser.parse_args()


RANDOM_SEED = args.RANDOM_SEED
NUM_MACHINES = args.NUM_MACHINES
WASHTIME = args.WASHTIME
T_INTER = args.T_INTER
SIM_TIME = args.SIM_TIME
NUM_CAR_INIT = args.NUM_CAR_INIT
DELTA = args.DELTA
PEAKS = args.PEAKS
NUM_TOTAL_CARS = args.NUM_TOTAL_CARS
BALK_NUM = args.BALK_NUM
VERBOSE = args.VERBOSE
VERBOSE_HIGH = args.VERBOSE_HIGH

max_sim = 8
if NUM_MACHINES == 0:
    print( "Car Wash is closed ... ")
    print (" ... come back later ...")
    sys.exit(0)
elif NUM_MACHINES > max_sim:
    print('this simulation was not designed to handle more than %d machines'%max_sim)
    sys.exit(0)
    
print ("-r {:<10} (RANDOM_SEED)".format(RANDOM_SEED))
print ("-m {:<10} (NUM_MACHINES)".format(NUM_MACHINES))
print ("-w {:<10} (WASHTIME)".format(WASHTIME))
print ("-t {:<10} (T_INTER)".format(T_INTER))
print ("-s {:<10} (SIM_TIME)".format(SIM_TIME))
print ("-c {:<10} (NUM_CAR_INIT)".format(NUM_CAR_INIT))
print ("-d {:<10} (DELTA)".format(DELTA))
print ("-p {:<10} (PEAKS)".format(PEAKS))
print ("-p {:<10} (NUM_TOTAL_CARS)".format(NUM_TOTAL_CARS))
print ("-p {:<10} (BALK_NUM)".format(BALK_NUM))

# -----------------
#RANDOM_SEED = 42
# NUM_MACHINES = 3  # Number of machines in the carwash
# WASHTIME = 5      # Minutes it takes to clean a car
# T_INTER = 4       # Create a car every ~7 minutes
# SIM_TIME = 500     # Simulation time in minutes
# exit(1)
# Setup and start the simulation


if(VERBOSE):
    print('Carwash')
    print('Check out http://youtu.be/fXXmeP9TvBg while simulating ... ;-)')
# -----------------


random.seed(RANDOM_SEED)  # This helps reproducing the results
# Create an environment and start the setup process

COLS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
dfLine = pd.DataFrame(np.nan, index=range(0, SIM_TIME), columns=['1'])

cust_lost_arr = []


for i in range(1, NUM_MACHINES+1):
    print ("Starting. Simulating carwash with %d machines ------------ " % (i))
    
    COL = COLS[i]
    numOfCars = 0
    env = simpy.Environment()
    env.process(setup(env, i, WASHTIME, T_INTER))
    env.run(until=SIM_TIME)
    dfLine[-1] = np.nan  # fill last row with Nan
    dfLine.rename(columns={-1: COLS[i+1]}, inplace=True)
    cust_lost_arr.append(CUSTOMERS_LOST)
    if (VERBOSE):
        print('{} customers were lost'.format(CUSTOMERS_LOST) if CUSTOMERS_LOST>1  else '{} customer was lost'.format(CUSTOMERS_LOST))
    print ("Done. Simulating carwash with %d machines ------------ " % (i))
dfLine.dropna(axis=1, how='all', inplace=True)

# ------------------------------------------
dfLine = dfLine.ffill(axis=0)  # "forward fill "

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


minor_ticks = np.arange(0, SIM_TIME, 5)  # every 5
ax.set_xticks(minor_ticks, minor=True)
ax.set_yticks(minor_ticks, minor=True)

# and a corresponding grid
ax.grid(which='minor', alpha=0.5)
ax.set(xlim=(0, SIM_TIME), ylim=(0, 1+dfLine.values.max()))
plt.grid()

cmap = get_cmap(NUM_MACHINES+1)
for i in range(1, NUM_MACHINES+1):
    if i == 1:
        thelabel = COLS[i] + " car wash machine "
    else:
        thelabel = COLS[i] + " car wash machines "
    dfLine.reset_index().plot(kind='scatter', x='index', y=COLS[i], color=cmap(i), ax=ax,
                              marker='.', label=thelabel,  linewidths=1)
    ax.set_ylabel('line length (#cars)')
    ax.set_xlabel('time(minutes)')

save_string = '-r-%d_-m-%d_-w-%d_-t-%d_-s-%d_c-%d_d-%d_p-%d_n-%d_b-%d' \
    %(RANDOM_SEED, NUM_MACHINES, WASHTIME, T_INTER, SIM_TIME, NUM_CAR_INIT, DELTA, PEAKS, NUM_TOTAL_CARS, BALK_NUM)

plt.savefig('Balk_%s.png'%save_string)
#plt.savefig('Balk_%s.pdf'%save_string)

plt.show()

#testing matplotlib
# ----------------------------------------


fig1 = plt.figure()
ax = fig1.add_subplot(1, 1, 1)

ax.set( ylim=(0, NUM_TOTAL_CARS)) #xlim=(0, len(cust_lost_arr)+1),
plt.grid()

barplot = plt.bar(COLS[1:len(cust_lost_arr)+1], cust_lost_arr)

for i in range(1, NUM_MACHINES+1):

    barplot[i-1].set_color(cmap(i))


ax.set_ylabel('balked customers')
ax.set_xlabel('number of carwash machines')


plt.savefig('Balk_LostCustomers_%s.png'%save_string)
#plt.savefig('Balk_LostCustomers_%s.pdf'%save_string)

plt.show()

fig2 = plt.figure()
ax = fig2.add_subplot(1, 1, 1)

ax.set( ylim=(0, NUM_TOTAL_CARS)) #xlim=(0, len(cust_lost_arr)+1),
plt.grid()

final_count = []
for i in range(NUM_MACHINES):
    final_count.append(dfLine.at[SIM_TIME - 1, COLS[i+1]]+cust_lost_arr[i])

barplot = plt.bar(COLS[1:len(cust_lost_arr)+1], final_count)

for i in range(1, NUM_MACHINES+1):

    barplot[i-1].set_color(cmap(i))


ax.set_ylabel('balked+in line at (SIM_TIME - 1) customers')
ax.set_xlabel('number of carwash machines')

plt.savefig('Balk_AngryCustomers_%s.png'%save_string)
#plt.savefig('Balk_LostCustomers_%s.pdf'%save_string)

plt.show()



if (VERBOSE):
    print('saving files as', save_string)
#RANDOM_SEED = 42
#NUM_MACHINES = 2  # Number of machines in the carwash
#WASHTIME = 5  # Minutes it takes to clean a car
#T_INTER = 3  # Create a car every ~7 minutes
#SIM_TIME = 20  # Simulation time in minutes

#NUM_CAR_INIT = 2  # Initial number of cars
#DELTA = 3 ')
#PEAKS = 2

print ("")
theTime = 100
if SIM_TIME > theTime:
    print("Line length at %d with %d machine is --> %d" %
          (theTime, NUM_MACHINES, dfLine.at[theTime, COLS[NUM_MACHINES]]))
theTime = 250
if SIM_TIME > theTime:
    print("Line length at %d with %d machine is --> %d" %
          (theTime, NUM_MACHINES, dfLine.at[theTime, COLS[NUM_MACHINES]]))
theTime = SIM_TIME-1
if SIM_TIME > theTime:
    print("Line length at %d with %d machine is --> %d" %
          (theTime, NUM_MACHINES, dfLine.at[theTime, COLS[NUM_MACHINES]]))