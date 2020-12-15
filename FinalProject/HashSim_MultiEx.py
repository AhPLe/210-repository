# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 22:35:29 2020

Coordinates the timing between multiple 
MultiEx_TimeCo

@author: arthu
"""
import random
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
from matplotlib import cm
import math
import HashEventEx_MultiEx as ev_exec
import MYSim_LP_Class as MYSim_LP
import enum
#import threading
import waiting

import argparse


class State(ev_exec.Executive.Event_Enum, enum.Enum):
    Healthy = 1
    Infected = 2
    Sick = 3
    Infectious = 4
    Recovered = 5
    Dead = 6
    Vaccinated = 7

    def name(self) -> str:
        if(self.value == 1):
            return 'Healthy'
        elif(self.value == 2):
            return 'Infected'  # can transmit, may get sick
        elif(self.value == 3):
            return 'Sick'
        elif(self.value == 4):
            return 'Infectious'  # finished sick, still can transmit
        elif(self.value == 5):
            return 'Recovered'
        elif(self.value == 6):
            return 'Dead'
        elif(self.value == 7):
            return 'Vaccinated'
        else:
            return 'not a State'  # with explicitly defined states, this shouldn't happen


class MYAgent_LP(MYSim_LP.MYSim_LP):

    # def __init__(self, ex: MYSim_LP.ev_exec.MYEventExecutive):
    #    self.msg_history = [(int, int, State)]

    r0 = 1.5
    infected = 0.05
    vaccinated = 0.05
    length_time = 4
    sick = 0.2
    use_area = False
    area = 40  # arbitrary units, helps determine how many contacts per 'day' of infection
    DEFAULT_CONCENTRATION = 50/50
    # computed later, value affected by sick and length_time
    adj_sick = math.exp(math.log(1-0.2)/5)
    adj_r0 = 1.5/5

    def __init__(self, ex: ev_exec.MYEventExecutive, to_insert = True, state: State = State(1)):
        #self.time = 0
        #self.ex = ex
        #self.id = self.ex.insert_LP(self)
        #self.msg_history = []
        super().__init__(ex, to_insert)
        self.state = state
        self.infected_time = 0
        if to_insert:
            self.msg_history = [(int, int, State)]
        
    def GetCopy(self):
        agent_copy = MYAgent_LP(self.ex, to_insert = False, state = self.state)
        agent_copy.infected_time = self.infected_time
        agent_copy.time = self.time
        agent_copy.id = self.id
        return agent_copy
    
    def MYSimGetMsg(self, time: int, transmit_id: int, state: State):
        # overwriting message behavior to convert to pingpong
        self.msg_history.append((transmit_id, time, state))
        temp_state = self.state
        self.time = time

        if transmit_id == self.id and self.state == state and self.infected_time > 0:
            self.InfectionCycle(self.infected_time)
        else:
            if self.state.value > State.Healthy.value and self.state.value < State.Recovered.value:
    
                if self.state.value + 1 == state.value:
                    self.state = state
                if state == State.Recovered or state == State.Dead:
                    self.state = state
    
            if self.state == State.Healthy:
                self.state = state
    
            if not temp_state == self.state:  # if the state was changed
                if self.ex.Get_VERBOSE():
                    print(self.id, 'in state', temp_state,
                          'is now', self.state, 'at time', time)
    
                if self.state == State.Infected or self.state == State.Infectious:
                    self.InfectionCycle()
                elif self.state == State.Sick:
                    self.Sick()
                elif self.state == State.Dead:
                    self.Dead()

            # Infected can go to sick, which can go to infectious
            # only non-stepwise are recovered and dead
            # also you can't start being infected again after being infected
            # same for sick, or infectious

    def __repr__(self):
        return str(self.id) + ' Object ' + str(self.state)

    def GetState(self) -> str:
        return self.state.name()

    def GetCount(self) -> int:
        return self.count

    def DailyInfection(self, time_in_future):
        if self.use_area:
            concentration = self.ex.Get_List_Count()/self.area
            to_infect = self.adj_r0*concentration/self.DEFAULT_CONCENTRATION
        else:
            to_infect = self.adj_r0
        num_spread = math.floor(to_infect)
        if self.ex.Get_VERBOSE():
            print('to_infect is {}'.format(to_infect))
        test = random.random()
        if test < to_infect-num_spread:
            num_spread += 1
        for i in range(num_spread):
            if self.ex.Get_VERBOSE():
                print('attempting to spread at time {}'.format(time_in_future))
            self.ex.send_Next(self.time + time_in_future,
                              self.id, State.Infected, rand_recip=True)

    def Dead(self):
        self.ex.remove_LP(self.id)
        if self.ex.Get_VERBOSE():
            print(self.id, 'died at', self.time)

    def Sick(self):
        if self.ex.Get_VERBOSE():
            print(self.id, ' is sick at time', self.time)
        died = False
        for i in range(self.length_time):
            test = random.random()
            if test >= self.adj_dead and not died:
                self.ex.send_Message(self.time+i, self.id, self.id, State.Dead)
                died = True
        if not died:
            self.ex.send_Message(self.time+self.length_time,
                             self.id, self.id, State.Infectious)
        # after length_time, this Agent will recover from being sick

    def test_time_LP(self, itime):
        if self.ex.Get_Time() + 1 - (self.time + itime + 1) < 0:
            return False
        else:
            return True
    
    def InfectionCycle(self, ilength: int = length_time):
        self.infected_time = 0
        if self.ex.Get_VERBOSE():
            print('starting infection cycle for object',
                  self.id, 'at', self.time, 'for', ilength)
        sick = False
        
        itime = ilength
        iextra = 0
        
        if self.time + ilength > self.ex.Get_Time() + 1:
            itime = self.ex.Get_Time() + 1 - (self.time)
            iextra =  ilength - itime
        
        for i in range(itime):
            self.DailyInfection(i)

            if self.state == State.Infected:# and random.random() >= self.adj_sick:
                testdaily = random.random()
                if testdaily >= self.adj_sick:
                    self.ex.send_Message(self.time + i, self.id, self.id, State.Sick)
                    sick = True
                    iextra = 0
                    break
                    # send a message to self at the proper time that this Agent will
                    # become sick
                    # a sick member will isolate                
        if iextra == 0 and not sick:
            self.ex.send_Message(self.time + itime,
                                 self.id, self.id, State.Recovered)
        elif iextra > 0 and not sick:
            #this only happens if the person is still sick and able to infect
            self.infected_time = iextra
            self.ex.send_Message(self.time + itime + 1 - self.ex.Get_Lat(), self.id, self.id, self.state)
            #waiting.wait(self.test_time_LP(itime))
            #threading.Event.wait(self.ex.WAIT_TIME)
            #self.InfectionCycle(iextra)
        else:
            if self.ex.Get_VERBOSE():
                print('{} was sick'.format(self))
        
    def InitializeInfection(self):  # initial start
        if self.ex.Get_VERBOSE():
            print(self.id, 'was infected at time', self.time)
        self.state = State.Infected
        self.InfectionCycle()
        #self.MySimSend(self.time, self.state, dest)

def MYSimInitApplication(time_set=None, randstate = None):  # int argc, char ** argv
    parser = argparse.ArgumentParser()
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
    parser.add_argument('-dvacc', action="store", dest="dvacc",
                        default=0.1,	type=float)  # percent that are vaccinated
    
    
    parser.add_argument('-iplot', action="store_true", dest="iplot")  # shows the attempt at individual plots
    
    # dr0 = 1.5 for concentration of 50 people per area (default area is 20 units)
    #dinfected = 0.05
    #dlength_time = 4
    #dsick = 0.2
    #VERBOSE= True
    #LP_hash = None
    
    '''
    -dr0 is the r0 of the disease
    dr0 for a concentration 1:1 person per area (default area is 40 units)
    -dinfected is the percent of population that is infected
    -dlength_time is the length of time of time before becoming 'recovered'
    this model is simplistic, so the length of time from infected -> recovered
    is the same as sick->infectious = infectious -> recovered
    -dsick is the percent who get sick after being infected
    -x specifies the number of executives used
    further arguments explained in apl_extra_event_executive
    '''

    # ev_exec arguments - 'args, unknownargs = parser.parse_known_args()' may help for splitting
    # unknown currently how to implement efficiently
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
    
    args = parser.parse_args()

    random.seed(args.random_Seed)
    #if randstate == None:
    #randstate = random.getstate()
    #random.setstate(randstate)
    np.random.default_rng(args.random_Seed)
    #print('first int  from Sim', random.randint(1, 200))    
    
    MYAgent_LP.r0 = args.dr0  # set the 'global class variables' for each parameter
    MYAgent_LP.infected = args.dinfected
    MYAgent_LP.vaccinated = args.dvacc
    
    MYAgent_LP.length_time = args.dlength_time
    MYAgent_LP.sick = args.dsick
    MYAgent_LP.dead = args.ddead
    MYAgent_LP.adj_sick = math.exp(
        math.log(1-MYAgent_LP.sick)/MYAgent_LP.length_time)
    # math.exp(math.log(1-MYAgent_LP.r0)/MYAgent_LP.length_time)
    MYAgent_LP.use_area = args.use_area
    MYAgent_LP.adj_r0 = MYAgent_LP.r0/MYAgent_LP.length_time 
    num_executives = args.num_executives
    
    
    distribution = 5
    spread = [0 for i in range(distribution + 1)]
    for i in range(1, distribution):
        spread[i] += i*math.floor(args.sim_Time/distribution)
        
    spread[distribution] = args.sim_Time
    
        #math.exp(math.log(1-MYAgent_LP.r0)/MYAgent_LP.length_time)
    # below is the calculation for dying, over the time it takes to get sick
    # it is more convoluted since it depends on infections instead of sickness
    # why this design decision? that number is much easier to come by
    MYAgent_LP.adj_dead = math.exp(
        math.log(1-MYAgent_LP.dead)/MYAgent_LP.length_time)

    # adjusted sick accounts for the actual length of time for each sick day
    # so the total amount sick is not high: formula adj_sick=e^(ln(1-sick)/lt)

    args.lim_Latency = 1
    args.fixed_Latency = True
    if not time_set == None:
        args.sim_Time = time_set
    # with this simulation, these values should always be consistent as time
    # should change, but latency should stay constant

    # pass the rest of the args in to the EventExecutive

    #LPList = ex.Get_List_Copy()

    ex_arr = []
        
    def Initialize(LPList_Initial):
        total = len(LPList_Initial)
        if ex_arr[0].Get_VERBOSE():
            print('starting infections')
        new_infected = math.ceil(MYAgent_LP.infected*total)
        new_vacc= math.floor(MYAgent_LP.vaccinated*total)
        if new_infected+new_vacc > total:
            new_vacc = total - new_infected
            print('overriding infected with vaccinations')
        #print('list')
        #print(LPList_Initial)
        #print('number infected: {}'.format(MYAgent_LP.infected))
        #print('total number: {}'.format(total))
        #print('expected number infected: {}'.format(MYAgent_LP.infected*total))
        item_iter = iter(LPList_Initial)
        item = [None, None]
        # count = 0
        nomore = False
        for i in range(new_vacc):
            try: 
                item = next(item_iter)
            except StopIteration:
                print('iteration was stopped, something probably went wrong')
                nomore = True
                break #nothing else to infect, file should stop
            
            item[1].state = State(7)
        if not nomore:
            for i in range(new_infected):
                try: 
                    item = next(item_iter)
                except StopIteration:
                    print('iteration was stopped, something probably went wrong')
                    
                    break #nothing else to infect, file should stop
                
                item[1].InitializeInfection()
        
            
    
    LP_arr_List_Initial = []
    for i in range (num_executives):
        ex_arr.append(ev_exec.MYEventExecutive(args, spread, randstate))
        LP_arr_List_Initial.append(ex_arr[i].create_LPs(MYAgent_LP))
        if not ev_exec.MYEventExecutive.setstate:
            ev_exec.MYEventExecutive.randstate = random.getstate()
            ev_exec.MYEventExecutive.setstate = True
        
        random.setstate(ev_exec.MYEventExecutive.randstate)
            #random.setstate(randstate)
        if (len(LP_arr_List_Initial[i]) > 0):
            Initialize(LP_arr_List_Initial[i])
    
    if len(ex_arr) > 1 and ex_arr[0].Get_VERBOSE():
        print("-dr0 {:<10} (r0)".format(MYAgent_LP.r0))
        print("-dinfected {:<10} (% infected)".format(MYAgent_LP.infected))
        print("-dlength_time {:<10} (infection to healthy time length)".format
              (MYAgent_LP.length_time))
        print("-dsick {:<10} (% sick)".format(MYAgent_LP.sick))

    #CURRENT STOPPING POINT - necessary changes
    #TODO - allow stopping points to correlate between all executives
    # once each executive reaches a point, allow it to move forward
    # then, implement further details beyond the executive itself
    
    random.setstate(ev_exec.MYEventExecutive.randstate)
    ev_exec.MYEventExecutive.run_all_execs()

    #print(LP.r0, LP.infected, LP.length_time, LP.sick)
    #LPList_Final = ex.Get_List_Copy()
    if ex_arr[0].Get_VERBOSE():
        for i in range(len(ex_arr)):
            print('executive {ex} had {num} messages'.format(ex=i, num=(ex_arr[i].Get_Count())))
    
    return ex_arr, LP_arr_List_Initial, spread, randstate, args

    # set random generator seeds - per LP or just once  - up to you.
    # MySim_RandInit( ); # part of simulation executive.

if (__name__ == '__main__'):
    ex_arr, LP_arr_List_Initial, spread, randstate, args = MYSimInitApplication()

#cmap = get_cmap(len(State))
spread_str = ['' for i in range(len(spread))]
spread_str[0] = '0'
    
for i in range(len(spread)):
    spread_str[i] = str(spread[i])
    #spread_str[distribution] = str(spread[distribution])
    
counts = [[0 for j in range(len(spread))] for i in range(len(State))]
bar_count = [[0 for j in range(len(spread))] for i in range(len(State))]
viridismap = cm.get_cmap('viridis', len(State))

bars = []
for i in range(len(State)):
    bars.append(State(i+1).name())

def fill_bars(LPList_arr, temp_ex_arr, time_spread):
    for i in range(len(LPList_arr)):#LPList in LPList_arr:
        
        for LP in LPList_arr[i]:#LPList:
            for i in range(len(bars)):
                if bars[i] == LP[1].state.name():
                    counts[i][time_spread] += 1
                    bar_count[i][time_spread] += 1
        #for rem_LP in temp_ex_arr[i].removed_LPs:
        #    for i in range(len(bars)):
        #        if bars[i] == LP[1].state.name():
        #            counts[i][time_spread] += 1
        #            bar_count[i][time_spread] += 1
    
    for i in range(1, len(bars)):
        bar_count[i][time_spread] += bar_count[i-1][time_spread]



# fill_bars(LP_arr_List_Initial, ex_arr, len(spread) - 1)  # sets simulation time
# ev_exec.MYEventExecutive.Reset()
# the rest of the runs set up the graph fairly easily

# for i in range(len(spread) - 1):
#     temp_ex_arr, temp_LPList_arr, _, _ = MYSimInitApplication(spread[i], randstate)
    
#     fill_bars(temp_LPList_arr, temp_ex_arr, i)
#     #for i in range(len(ex_arr)):
#     #    ex_arr[i].Reset_Random() #resets seed so it starts over from the first runtime
#     ev_exec.MYEventExecutive.Reset()

def straight_fill(ex_arr, time_spread):
    for i in range(len(ex_arr)):#LPList in LPList_arr:
        for time_pos in range(len(ex_arr[i].LP_snapshot)):
            if ex_arr[i].LP_snapshot[time_pos] == None:
                print('something is wrong with:', ex_arr[i].LP_snapshot[time_pos])
            else:
                for LP in ex_arr[i].LP_snapshot[time_pos][0]:
                    for j in range(len(bars)):
                            if bars[j] == LP[1].state.name():
                                counts[j][time_pos] += 1
                                bar_count[j][time_pos] += 1
                for removed_LP in ex_arr[i].LP_snapshot[time_pos][1]:
                    for j in range(len(bars)):
                            if bars[j] == removed_LP[1].state.name():
                                counts[j][time_pos] += 1
                                bar_count[j][time_pos] += 1
    for time_pos in range(len(time_spread)):
        for i in range(1, len(bars)):
            bar_count[i][time_pos] += bar_count[i-1][time_pos]
        
            
        #for rem_LP in temp_ex_arr[i].removed_LPs:
        #    for i in range(len(bars)):
        #        if bars[i] == LP[1].state.name():
        #            counts[i][time_spread] += 1
        #            bar_count[i][time_spread] += 1
    

straight_fill(ex_arr, spread)    

fig, ax = plt.subplots()

#width = ex.sim_Time/(len(spread)-1) #

for i in range(len(bars)):
    if i == 0:
        ax.bar(spread_str, counts[i],  edgecolor='white', label=bars[i])
    else:
        ax.bar(spread_str, counts[i], bottom=bar_count[i-1],
               edgecolor='white', label=bars[i])
    if ex_arr[0].VERBOSE:
        #print(bar_count)
        print(counts[i], bars[i])

# , bbox_to_anchor=(1.05, 1)
plt.legend(bars, title='States', loc='upper left')
# no real idea what the above does, but it stops the legend from moving around
# https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot

# (xlim=(0, ex.sim_Time),

maxh = 0
for LPList in LP_arr_List_Initial:
    maxh += len(LPList)

ax.set(ylim=(0, maxh))

ax.set_ylabel('Total Agent Count (Population or LP)')
ax.set_xlabel('Simulation Time')
ax.set_title('Count of Total Group States vs. Time')
ax.legend()
plt.show()

#individual plots per exec
if args.iplot:
    ex_count = 0
    for ex in ex_arr:
        plt.clf()
        ind_counts = [[0 for j in range(len(spread))] for i in range(len(State))]
        ind_bar_count = [[0 for j in range(len(spread))] for i in range(len(State))]
        
        ind_bars = []
        for i in range(len(State)):
            ind_bars.append(State(i+1).name())
        
        def ind_straight_fill(ex, time_spread):
            
            for time_pos in range(len(ex.LP_snapshot)):
                if ex.LP_snapshot[time_pos] == None:
                    print('something is wrong with:', ex.LP_snapshot[time_pos])
                else:
                    for ind_LP in ex.LP_snapshot[time_pos][0]:
                        for j in range(len(ind_bars)):
                                if ind_bars[j] == ind_LP[1].state.name():
                                    ind_counts[j][time_pos] += 1
                                    ind_bar_count[j][time_pos] += 1
                    for ind_removed_LP in ex.LP_snapshot[time_pos][1]:
                        for j in range(len(ind_bars)):
                                if ind_bars[j] == ind_removed_LP[1].state.name():
                                    ind_counts[j][time_pos] += 1
                                    ind_bar_count[j][time_pos] += 1
            for time_pos in range(len(time_spread)):
                for i in range(1, len(ind_bars)):
                    ind_bar_count[i][time_pos] += ind_bar_count[i-1][time_pos]
                
                    
                #for rem_LP in temp_ex_arr[i].removed_LPs:
                #    for i in range(len(bars)):
                #        if bars[i] == LP[1].state.name():
                #            counts[i][time_spread] += 1
                #            bar_count[i][time_spread] += 1
            
        
        ind_straight_fill(ex, spread)    
        
        fig, ax = plt.subplots()
        
        #width = ex.sim_Time/(len(spread)-1) #
        
        for i in range(len(ind_bars)):
            if i == 0:
                ax.bar(spread_str, counts[i],  edgecolor='white', label=ind_bars[i])
            else:
                ax.bar(spread_str, counts[i], bottom=ind_bar_count[i-1],
                       edgecolor='white', label=ind_bars[i])
            if ex.VERBOSE:
                #print(bar_count)
                print(ind_counts[i], ind_bars[i])
        
        # , bbox_to_anchor=(1.05, 1)
        plt.legend(ind_bars, title='States', loc='upper left')
        # no real idea what the above does, but it stops the legend from moving around
        # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
        
        # (xlim=(0, ex.sim_Time),
        
        ind_maxh = 0
        for i in range(len(spread)):
            final_bar_pos = len(ind_bars)-1
            ind_maxh = max(ind_maxh, ind_bar_count[final_bar_pos - 1][i] + counts[final_bar_pos][i])
        
        ax.set(ylim=(0, ind_maxh))
        
        ax.set_ylabel('{} Executive Agent Count (Population or LP)'.format(ex_count))
        ax.set_xlabel('Simulation Time')
        ax.set_title('Count of Ex {} Group States vs. Time'.format(ex_count))
        ax.legend()
        plt.show()
        ex_count += 1
