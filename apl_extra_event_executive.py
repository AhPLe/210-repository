# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 11:51:36 2020
@author: arthu
"""
#import argparse
#import MYSim_LP_Class as MYSim_LP
import enum
import random
import numpy as np
from queue import PriorityQueue #as PriorityQueue

#from dataclasses import dataclass, field
#from typing import Any

#@dataclass(order=True)
#class PrioritizedItem:
#    priority: int
#    item: Any=field(compare=False)


class Event_Enum(enum.Enum): #Enum class used as base class for individual implementation
# and 'type-checking' idea for python 3
    pass

class MYEventExecutive():
    
    #random_Seed = 42
    #sim_Time = 100
    #fixed_latency = False
    #lim_Latency = 2
    #VERBOSE= True
    #LP_hash = None
    
    
    '''
    -r is the random seed
    -s is the simulation timespan
    -f is the latency time
    -k is the limitation of the latency time
    -p is the number of processes
    -v is VERBOSE off
    '''
    
    def __init__(self, args):
    
        self.random_Seed = args.random_Seed
        self.sim_Time = args.sim_Time
        self.fixed_latency = args.fixed_latency
        self.lim_Latency = args.lim_Latency
        self.processes = args.processes
        self.VERBOSE = args.VERBOSE
        
        self.LP_list = [] #was originally implemented as a dict with hashed values, but this with lists in python as an array-type structure
        #this seems like a simpler implementation
        self.queue = PriorityQueue()
        self.message_count = 0
        
        random.seed(self.random_Seed) #this probably doesn't need to be initialized here
        # it also probably doesn't hurt to have it initialized here
        self.rng = np.random.default_rng(seed=self.random_Seed)
    
    def insert_LP(self, LP) -> int: #inserts a MYSim_LP into the list, then gives back the id
        self.LP_list.append(LP)
        return len(self.LP_list)-1
    
    def putMessage(self, time: int, transmit_id: id, recipient_id: int, message: Event_Enum) -> bool:
        time += self.Get_Lat()
        self.queue.put((time, transmit_id, recipient_id, message))
        return True #the message was sent, ideally should be a number of 'success' or 'error', 
    #but that's beyond the scope of this project
    
    def run_exec(self):
        time_count = 0
        if self.VERBOSE:
            self.Be_Verbose()
        while(True):
            if not self.queue.empty():
                msg = self.queue.get()
                if msg[0] >= self.sim_Time:
                    if self.VERBOSE:
                        print('executive function is ending at time {sim_Time}'.format(sim_Time=self.sim_Time))
                    break
                else:
                    if self.VERBOSE:
                        print('time', msg[0], 'transmitter', msg[1], 'recipient', msg[2], 'message', msg[3])
                    if msg[2] >=len(self.LP_list):
                        if self.VERBOSE:
                            print('unable to send above message')
                    else:
                        self.message_count += 1
                        self.LP_list[msg[2]].MYSimGetMsg(msg[0], msg[1], msg[3])
                    #self.send_Message(msg[0], msg[1], msg[2], msg[3])
            else:
                time_count += 1 #possibly (hopefully) unnecessary, but I don't know enough about threads to be sure
                if (time_count > self.sim_Time):
                    if self.VERBOSE:
                        print('executive function ending due to empty queue')
                    break
    
    def create_LPs(self, LPClass_func):
        for i in range(self.processes):
            LPClass_func(self) #for better or worse, the class inserts it into this executive
        return self.Get_List_Copy()
    
    def remove_LP(self, LP_remove_id: int):
        self.LP_list.pop(LP_remove_id)
    
    def send_Next(self, time: int, transmit_id: int, message: Event_Enum, rand_recip: bool = False):
        #simple function to put next message
        #time += self.Get_Lat() - now implemented in 'put'
        if time > self.sim_Time or len(self.LP_list) - 1 < 1:
            if self.VERBOSE:
                print('message at {cur_time} was not sent'.format(cur_time=time))
        else:
            if not rand_recip:
                recipient_id = (transmit_id+1)%len(self.LP_list)
            else:
                temp_rand = random.randint(1, len(self.LP_list) - 1) #random without sending back to same node
                if temp_rand < transmit_id:
                    recipient_id = temp_rand
                else:
                    recipient_id = (temp_rand+1)%len(self.LP_list) 
            if self.VERBOSE:
                print('recipient of',message,'will be', recipient_id,'at time', time)
            self.putMessage(time, transmit_id, recipient_id, message)
            #the queue was implemented a bit late in the programming
            #self.LP_list[recipient_id].MYSimGetMsg(time, message, transmit_id) this function used to send directly

    def Be_Verbose(self):
        
        print ("-r {:<10} (random_Seed)".format(self.random_Seed))
        print ("-s {:<10} (sim_Time)".format(self.sim_Time))
        if self.fixed_latency:
            print ("-f (fixed latency)")
        print ("-k {:<10} (lim_Latency)".format(self.lim_Latency))
        print ("-p {:<10} (processes)".format(self.processes))
        
    def send_Message(self, time: int, transmit_id: int, recipient_id: int, message: Event_Enum):
        #old way of sending messages before implementing queue and/or list
        if time > self.sim_Time:
            if self.VERBOSE:
                print('a message has been stopped')
        else:
            #msgObject = self.LP_dict[recipient]
            
            
            self.putMessage(time, transmit_id, recipient_id, message)
            #self.LP_list[recipient_id].MYSimGetMsg(time, transmit_id, message)
    
    def Get_Lat(self) -> int:
        if self.fixed_latency:
            return self.lim_Latency
        else:
            return random.randint(1, self.lim_Latency)
        
    def Get_List_Copy(self):
        return self.LP_list.copy()
    
    def Get_List_Count(self):
        return len(self.LP_list) #not as time intensive as Get_List_Copy
    
    def Get_VERBOSE(self) -> bool:
        return self.VERBOSE
    
    def Get_Count(self) -> int:
        return self.message_count
    