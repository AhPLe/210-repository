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

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from matplotlib import pyplot

RANDOM_SEED = 56
NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5  # Minutes it takes to clean a car
T_INTER = 3  # Create a car every ~7 minutes
SIM_TIME = 20  # Simulation time in minutes

NUM_CAR_INIT = 4  # Initial number of cars
DELTA = 3 	# RANDOMNESSINTERVAL generating cars
COL = '1'
VERBOSE = True


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
    numOfCars = numOfCars + 1
    dfLine.at[env.now, COL] = numOfCars

    if(VERBOSE):
        print('%s arrives at the carwash at %.2f. Car Length = %d' %
              (name, env.now, numOfCars))

    with cw.machine.request() as request:

        yield request

        if(VERBOSE):
            print('%s enters the carwash at     %.2f.' % (name, env.now))

        numOfCars = numOfCars - 1
        if pd.isnull(dfLine.at[env.now, COL]):
            dfLine.at[env.now, COL] = numOfCars
        else:
            dfLine.at[env.now, COL] = dfLine.at[env.now, COL] - 1

        yield env.process(cw.wash(name))

        if(VERBOSE):
            print('%s leaves the carwash at     %.2f.' % (name, env.now))


def setup(env, num_machines, washtime, t_inter):
    """Create a carwash, a number of initial cars and keep creating cars
    approx. every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    # this is confusing - should only  REALLY create 1 car initially
    # Create 1 initial cars -> not 4.
    CARS = NUM_CAR_INIT

    if(VERBOSE):
        print('Initial number of CARS: %d' % (CARS))
    for i in range(CARS):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    while True:
        # randomly generated cars.
        # yield env.timeout( random.randint(t_inter - 2, t_inter + 2) )
        # removes the randomness
        yield env.timeout(random.randint(t_inter - DELTA, t_inter + DELTA))
        i += 1
        env.process(car(env, 'Car %d' % i, carwash))

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
parser.add_argument('-v', action="store_true", dest="VERBOSE", default=True)
args = parser.parse_args()


RANDOM_SEED = args.RANDOM_SEED
NUM_MACHINES = args.NUM_MACHINES
WASHTIME = args.WASHTIME
T_INTER = args.T_INTER
SIM_TIME = args.SIM_TIME
NUM_CAR_INIT = args.NUM_CAR_INIT
DELTA = args.DELTA

if NUM_MACHINES == 0:
    print( "Car Wash is closed ... ")
    print (" ... come back later ...")
    exit(1)

print ("-r {:<10} (RANDOM_SEED)".format(RANDOM_SEED))
print ("-m {:<10} (NUM_MACHINES)".format(NUM_MACHINES))
print ("-w {:<10} (WASHTIME)".format(WASHTIME))
print ("-t {:<10} (T_INTER)".format(T_INTER))
print ("-s {:<10} (SIM_TIME)".format(SIM_TIME))
print ("-c {:<10} (NUM_CAR_INIT)".format(NUM_CAR_INIT))
print ("-d {:<10} (NUM_CAR_INIT)".format(DELTA))

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

for i in range(1, NUM_MACHINES+1):
    print ("Starting. Simulating carwash with %d machines ------------ " % (i))
    COL = COLS[i]
    numOfCars = 0
    env = simpy.Environment()
    env.process(setup(env, i, WASHTIME, T_INTER))
    env.run(until=SIM_TIME)
    dfLine[-1] = np.nan  # fill last row with Nan
    dfLine.rename(columns={-1: COLS[i+1]}, inplace=True)
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

save_string = '-r-%d_-m-%d_-w-%d_-t-%d_-s-%d_c-%d_d-%d' %(RANDOM_SEED, NUM_MACHINES, WASHTIME, T_INTER, SIM_TIME, NUM_CAR_INIT, DELTA)

plt.savefig('%s.png'%save_string)
plt.savefig('%s.pdf'%save_string)

plt.show()

print(save_string)
#RANDOM_SEED = 42
#NUM_MACHINES = 2  # Number of machines in the carwash
#WASHTIME = 5  # Minutes it takes to clean a car
#T_INTER = 3  # Create a car every ~7 minutes
#SIM_TIME = 20  # Simulation time in minutes

#NUM_CAR_INIT = 2  # Initial number of cars
#DELTA = 3 ')

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
