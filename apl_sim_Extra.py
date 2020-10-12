# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 22:35:29 2020

@author: arthu
"""
import random
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
import math
import apl_extra_event_executive as ev_exec
#import MYSim_LP_Class as MYSim_LP

import argparse

class MYSim_LP():
    
    def __init__(self, ex: ev_exec.MYEventExecutive): #makes IPing and IPong mostly unnecessary
        self.time = 0
        self.ex = ex
        self.id = ex.insert_LP(self)
        self.count = 0
        self.msg_history = []
    
    def MYSimGetMsg(self, time: int, transmit_id: int, message: ev_exec.Event_Enum):
        print('poor message received')
        pass #this should be overwritten
        #locates a message buffer 
		#[you may not need this, this is one way of doing it]

    def MYSimSend(self, *args) -> bool: 	#Sends a message (schedules an event)
        self.ex.send_Message(self, args)
        return True
    
    def MYSimNow(self) -> int:	#A function that returns the current simulation time, an int
        return self.time
    
    def MYSimLPMe(self) -> int: 	#A function that returns the simulation object unique id
        return self.id



class State(ev_exec.Event_Enum):
    Healthy = 1
    Infected  = 2
    Sick = 3
    Infectious = 4
    Recovered = 5
    Dead = 6
    
    def name(self) -> str:
        if(self.value == 1):
            return 'Healthy'
        elif(self.value == 2):
            return 'Infected' #can transmit, may get sick
        elif(self.value == 3):
             return 'Sick'
        elif(self.value == 4):
             return 'Infectious' #finished sick, still can transmit
        elif(self.value == 5):
            return 'Recovered'
        elif(self.value == 6):
             return 'Dead'
        else:
            return 'not a State' #with explicitly defined states, this shouldn't happen

class MYAgent_LP(MYSim_LP):
    
    #def __init__(self, ex: MYSim_LP.ev_exec.MYEventExecutive):
    #    self.msg_history = [(int, int, State)]
    
    r0=1.5
    infected = 0.05
    length_time = 5
    sick = 0.2
    area = 40 #arbitrary units, helps determine how many contacts per 'day' of infection
    DEFAULT_CONCENTRATION = 50/50
    adj_sick=math.exp(math.log(1-0.2)/5) #computed later, value affected by sick and length_time
    adj_r0=1.5/5
    
    def __init__(self, ex: ev_exec.MYEventExecutive, state: State=State(1)):
        #self.time = 0
        #self.ex = ex
        #self.id = self.ex.insert_LP(self)
        #self.msg_history = []
        super().__init__(ex)
        self.state = state
        
        self.msg_history = [(int, int, State)]
        
    def MYSimGetMsg(self, time: int, transmit_id: int, state: State): 
            #overwriting message behavior to convert to pingpong
        self.msg_history.append((transmit_id, time, state))
        temp_state = self.state
        self.time = time
        if self.state.value>State.Healthy.value and self.state.value < State.Recovered.value:
            
            if self.state.value + 1 == state.value:
                self.state = state
            if state==State.Recovered or state==State.Dead:
                self.state = state
                
        if self.state== State.Healthy:
            self.state = state
        
        if not temp_state == self.state: #if the state was changed
            if self.ex.Get_VERBOSE():
                print(self.id, 'in state', temp_state, 'is now', self.state, 'at time', time)
            
            if self.state == State.Infected or self.state == State.Infectious:
                self.InfectionCycle()
            elif self.state == State.Sick:
                self.Sick()
            elif self.state == State.Dead:
                self.Dead()
        
            #Infected can go to sick, which can go to infectious
            #only non-stepwise are recovered and dead
            #also you can't start being infected again after being infected
            #same for sick, or infectious
            
        
        
    def __repr__(self):
        return str(self.id) + ' Object ' + str(self.state)
    
    def GetState(self) -> str:
        return self.state.name()
    
    def GetCount(self) -> int:
        return self.count
    
    def Circle(self):
        self.count += 1
        if self.ex.Get_VERBOSE():
            print(str(self),"received message at time", self.time)
        self.ex.send_Next(self.time, self.id, self.state)
    
    def DailyInfection(self, time_in_future):
        concentration = self.ex.Get_List_Count()/self.area
        to_infect = self.adj_r0*concentration/self.DEFAULT_CONCENTRATION
        num_spread = math.floor(to_infect)
        if random.random() < to_infect-num_spread:
            num_spread += 1
        for i in range(num_spread):
            #ISSUES: SICK STILL IN 'POOL' OF PEOPLE TO INFECT
            self.ex.send_Next(self.time + time_in_future, self.id, State.Infected, rand_recip = True)
    
    def Dead(self):
        self.ex.remove_LP(self.id)
        if self.ex.Get_VERBOSE():
            print(self.id, 'died at', self.time)
    
    def Sick(self):
        if self.ex.Get_VERBOSE():
            print(self.id,' is sick at time', self.time)
        for i in range(self.length_time):
            if random.random()>=self.adj_dead:
                self.ex.send_Message(self.time+i, self.id, self.id, State.Dead)
        self.ex.send_Message(self.time+self.length_time, self.id, self.id, State.Infectious)
        #after length_time, this Agent will recover from being sick
    
    def InfectionCycle(self):
        if self.ex.Get_VERBOSE():
            print('starting infection cycle for object', self.id,'at', self.time)
        sick = False
        for i in range(self.length_time):
            self.DailyInfection(i)
            
            if self.state == State.Infected and random.random()>=self.adj_sick:
                self.ex.send_Message(self.time+i, self.id, self.id, State.Sick)
                sick = True
                break
                #send a message to self at the proper time that this Agent will
                #become sick
                #a sick member will isolate
                
        if not sick:
            self.ex.send_Message(self.time+self.length_time, self.id, self.id, State.Recovered)
            
    def InitializeInfection(self): #initial start to pingpong
        if self.ex.Get_VERBOSE():
            print(self.id,'was infected at time',self.time)
        self.state = State.Infected
        self.InfectionCycle()
        #self.MySimSend(self.time, self.state, dest)
    
    def PingPong(self, state: State, transmit_id: int):
        
        self.count += 1
        if self.ex.Get_VERBOSE():
            print(str(self),"received message at time", self.time)
        transmit_state = State((self.state.value+1)%len(State))
        self.ex.send_Next(self.time, self.id, transmit_state)
        #self.ex.send_Message(self.time, self.id, self.state, transmit_id)
        #self.MySimSend(self.time, self.state, transmit_id)
            
    def IPingPong(self, dest: MYSim_LP): #initial start to pingpong
        if self.ex.Get_VERBOSE():
            print('starting ' + self.state.name())
        transmit_state = State((self.state.value+1)%len(State))
        self.ex.send_Next(self.time, self.id, transmit_state)
    
    
    
    #alternate to MYSimSend - direct through ex - self.ex.send_Message(self, self.state, transmit_id)
    
    

def MYSimInitApplication(time_set = None): # int argc, char ** argv 
    parser = argparse.ArgumentParser()
    parser.add_argument('-dr0', action="store", dest="dr0", #no double type in python, only numpy
                        default=1.5,   type=float) #stores the r0, the d is meant to allow differentiation
    #from r, so it will always be different instead of -r storing for -r0
    parser.add_argument('-dinfected', action="store", dest="dinfected",
                        default=0.05,	type=float) #stores initial percentage of infected
    parser.add_argument('-dlength_time', action="store", dest="dlength_time",
                        default=5,	type=int) #time spent having the disease
    parser.add_argument('-dsick', action="store", dest="dsick",
                        default=0.2,	type=float) #percent once infected get sick
    parser.add_argument('-ddead', action="store", dest="ddead",
                        default=0,	type=float) #percent that die once sick
    
    #dr0 = 1.5 for concentration of 50 people per area (default area is 20 units)
    #dinfected = 0.05
    #dlength_time = 5
    #dsick = 0.2
    #VERBOSE= True
    #LP_hash = None
    
    
    '''
    -dr0 is the r0 of the disease
         dr0 for a concentration of 50 people per area (default area is 20 units)
    -dinfected is the percent of population that is infected
    -dlength_time is the length of time of time before becoming 'recovered'
    this model is simplistic, so the length of time from infected -> recovered
    is the same as sick->infectious = infectious -> recovered
    -dsick is the percent who get sick after being infected
    further arguments explained in apl_extra_event_executive
    '''
    
    
    #ev_exec arguments - 'args, unknownargs = parser.parse_known_args()' may help for splitting
    #unknown currently how to implement efficiently
    parser.add_argument('-r', action="store", dest="random_Seed",
                        default=42,	type=int)
    parser.add_argument('-s', action="store", dest="sim_Time",
                        default=5, 	    type=int)
    parser.add_argument('-f', action="store_true", dest="fixed_latency",
                        default=False)
    parser.add_argument('-k', action="store", dest="lim_Latency",
                        default=2,   type=int)
    parser.add_argument('-v', action="store_false", dest="VERBOSE", default=True)
    parser.add_argument('-p', action="store", dest="processes", default=2,   type=int)
    
    args = parser.parse_args()
    
    random.seed(args.random_Seed)
    
    MYAgent_LP.r0 = args.dr0 #set the 'global class variables' for each parameter
    MYAgent_LP.infected = args.dinfected
    MYAgent_LP.length_time = args.dlength_time
    MYAgent_LP.sick = args.dsick
    MYAgent_LP.dead = args.ddead
    MYAgent_LP.adj_sick =math.exp(math.log(1-MYAgent_LP.sick)/MYAgent_LP.length_time)
    MYAgent_LP.adj_r0 = MYAgent_LP.r0/MYAgent_LP.length_time #math.exp(math.log(1-MYAgent_LP.r0)/MYAgent_LP.length_time)
    #below is the calculation for dying, over the time it takes to get sick
    #it is more convoluted since it depends on infections instead of sickness
    #why this design decision? that number is much easier to come by
    MYAgent_LP.adj_dead =math.exp(math.log(1-MYAgent_LP.dead)/MYAgent_LP.length_time) 
    
    #adjusted sick accounts for the actual length of time for each sick day
    #so the total amount sick is not high: formula adj_sick=e^(ln(1-sick)/lt)
    
    args.lim_Latency = 1
    args.fixed_Latency = True
    if not time_set==None:
        args.sim_Time = time_set
    #with this simulation, these values should always be consistent as time
    #should change, but latency should stay constant
    
    ex = ev_exec.MYEventExecutive(args) #pass the rest of the args in to the EventExecutive
        
    LPList_Initial = ex.create_LPs(MYAgent_LP)
    if ex.Get_VERBOSE():
        print ("-dr0 {:<10} (r0)".format(MYAgent_LP.r0))
        print ("-dinfected {:<10} (% infected)".format(MYAgent_LP.infected))
        print ("-dlength_time {:<10} (infection to healthy time length)".format\
               (MYAgent_LP.length_time))
        print ("-dsick {:<10} (% sick)".format(MYAgent_LP.sick))
        print(LPList_Initial)
    
    #LPList = ex.Get_List_Copy()
    
    def Initialize(total: int):
        if ex.Get_VERBOSE():
            print('starting infections')
        new_infected = math.ceil(MYAgent_LP.infected*total)
        for i in range(new_infected):
            LPList_Initial[i].InitializeInfection()
            #ex.send_Next(self.time, self.id, self.state)
        #self.MySimSend(self.time, self.state, dest)
    
    if (len(LPList_Initial) > 0):
        Initialize(len(LPList_Initial))
    

    ex.run_exec()

    
    #print(LP.r0, LP.infected, LP.length_time, LP.sick)
    print('this simulation had {num} messages'.format(num=(ex.Get_Count())))
    
    return ex, LPList_Initial
    
    # set random generator seeds - per LP or just once  - up to you.
    #MySim_RandInit( ); # part of simulation executive.



if (__name__ == '__main__'):
    ex, LPList_Initial = MYSimInitApplication()    

#cmap = get_cmap(len(State))
distribution = 5
spread = [0 for i in range(distribution + 1)]
spread_str = ['' for i in range(distribution + 1)]
spread_str[0] = '0'
for i in range(1, distribution):
    spread[i] += i*math.floor(ex.sim_Time/distribution)
    spread_str[i] = str(spread[i])
spread[distribution] = ex.sim_Time
spread_str[distribution] = str(spread[distribution])

          
counts = [[0 for j in range(len(spread))] for i in range(len(State))]
bar_count = [[0 for j in range(len(spread))] for i in range(len(State))]
bars = []
for i in range(len(State)):
    bars.append(State(i+1).name())

def fill_bars(LPList, time_spread):
    for LP in LPList:
        for i in range(len(bars)):
            if bars[i] == LP.state.name():
                counts[i][time_spread] += 1
                bar_count[i][time_spread] += 1
                
    for i in range(1, len(bars)):
        bar_count[i][time_spread] += bar_count[i-1][time_spread]

fill_bars(LPList_Initial, len(spread) - 1) #sets simulation time
#the rest of the runs set up the graph fairly easily
for i in range(len(spread) - 1):
    _, temp_LPList = MYSimInitApplication(spread[i])
    fill_bars(temp_LPList, i)

fig, ax = plt.subplots()

#width = ex.sim_Time/(len(spread)-1) #

for i in range(len(bars)):
    if i==0:
        ax.bar(spread_str, counts[i],  edgecolor='white', label=bars[i])
    else:
        ax.bar(spread_str, counts[i], bottom = bar_count[i-1], edgecolor='white', label=bars[i])
    if ex.Get_VERBOSE():
        print(counts[i], bars[i])

plt.legend(bars, title='States', loc='upper left')#, bbox_to_anchor=(1.05, 1)
#no real idea what the above does, but it stops the legend from moving around
#https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot

#(xlim=(0, ex.sim_Time), 
ax.set (ylim=(0, len(LPList_Initial)))

ax.set_ylabel('Agent Count (Population or LP)')
ax.set_xlabel('Simulation Time')
ax.set_title('Count of Group States vs. time')
ax.legend()
plt.show()