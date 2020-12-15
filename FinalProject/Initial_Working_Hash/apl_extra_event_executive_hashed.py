# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 11:51:36 2020
@author: arthu
"""
#import argparse
import random
import numpy as np
from queue import PriorityQueue  # as PriorityQueue
import apl_executive as Executive
import MYSim_LP_Class as MYSim_LP
import math
import threading

#from dataclasses import dataclass, field
#from typing import Any

# @dataclass(order=True)
# class PrioritizedItem:
#    priority: int
#    item: Any=field(compare=False)

# class dictLP():
#     import MYSim_LP_Class as MYSim_LP

#     def __init__(self):
#         self.LP_dict = {}

#     def insert_LP(self, LP: MYSim_LP):
#         value_hash = hash(LP)
#         self.LP_dict[value_hash] = LP
#         return value_hash

#     def remove_LP(self, LP_remove_id: int):
#         self.LP_dict.pop(LP_remove_id)

#     def Get_List_Copy(self):
#         return dict(self.LP_dict).items()

#     def Get_List_Count(self):
#         return len(self.LP_dict) #not as time intensive as Get_List_Copy


class MYEventExecutive(Executive.Executive):

    #random_Seed = 42
    #sim_Time = 100
    #fixed_latency = True - currently does nothing
    #lim_Latency = 2
    #VERBOSE= True
    #LP_hash = None

    '''
    -r is the random seed
    -s is the simulation timespan
    -f is the latency time, currently not implemented
    -k is the limitation of the latency time
    -p is the number of processes
    -v is VERBOSE off
    '''

    def __init__(self, args):
        super().__init__(args)
        self.random_Seed = args.random_Seed
        self.sim_Time = args.sim_Time
        self.fixed_latency = args.fixed_latency
        self.lim_Latency = args.lim_Latency
        self.processes = args.processes
        self.VERBOSE = args.VERBOSE

        #self.LP_dict = {} - defined in super
        #self.message_count = 0 - defined in super
        # self.LP_list = [] #was originally implemented as a dict with hashed values, but this with lists in python as an array-type structure
        # this seems like a simpler implementation
        self.queue = PriorityQueue()
        

        # this probably doesn't need to be initialized here
        random.seed(self.random_Seed)
        self.init_random_state = random.getstate()
        self.Reset_Random() 
        #attempting without self.Reset_Random() does not produce repeatable results
        print('random seed is -exec ', self.random_Seed)
        # it also probably doesn't hurt to have it initialized here
        self.rng = np.random.default_rng(seed=self.random_Seed)

    # inserts a MYSim_LP into the list, then gives back the id
    def insert_LP(self, LP: MYSim_LP) -> int:
        # python 'type checking' done at LP_dict level: MYSim_LP
        # return self.LP_dict.insert_LP(LP)
        #value_hash = hash(LP)
        #self.LP_dict[value_hash] = LP
        # self.LP_list.append(LP)
        return super().insert_LP(LP)  # value_hash

    def putMessage(self, time: int, transmit_id: id, recipient_id: int, message: Executive.Event_Enum) -> bool:
        time += self.Get_Lat()
        self.queue.put((time, transmit_id, recipient_id, message))
        return True  # the message was sent, ideally should be a number of 'success' or 'error',
    # but that's beyond the scope of this project

    def run_exec(self):
        time_count = 0
        if self.VERBOSE:
            self.Be_Verbose()
        while(True):
            if not self.queue.empty():
                msg = self.queue.get()
                if msg[0] >= self.sim_Time:
                    if self.VERBOSE:
                        print('executive function is ending at time {sim_Time}'.format(
                            sim_Time=self.sim_Time))
                    break
                else:
                    if self.VERBOSE:
                        print('time', msg[0], 'transmitter', msg[1],
                              'recipient', msg[2], 'message', msg[3])
                    if not msg[2] in self.LP_dict:  # >=len(self.LP_list)
                        if self.VERBOSE:
                            print('unable to send above message')
                    else:
                        self.LP_dict[msg[2]].MYSimGetMsg(
                            msg[0], msg[1], msg[3])
                    #self.send_Message(msg[0], msg[1], msg[2], msg[3])
            else:
                # possibly (hopefully) unnecessary, but I don't know enough about threads to be sure
                time_count += 1
                if (time_count > self.sim_Time):
                    if self.VERBOSE:
                        print('executive function ending due to empty queue')
                    break
    
    
    
    def run_poly(self, polymerize, area, DEFAULT_CONCENTRATION):
        #def React(ex: ev_exec.MYEventExecutive, LP_list: list):
        temprxnlst = []
        tempcount = self.message_count
        for i in range(self.sim_Time):
            if self.message_count < tempcount + 2*len(temprxnlst):
                threading.Event.wait(2)
                #wait some time, not great for a PDES, but ok for this simple project
            tempcount = self.message_count
            molecules = len(self.LP_list)
            concentration = molecules/area
            to_react = polymerize*concentration/DEFAULT_CONCENTRATION
            num_reactions = math.floor(to_react)
            if random.random() < to_react-num_reactions:
                num_reactions += 1
            temprxnlst = []
            for j in range(num_reactions):
                tempreactingmol = random.random(molecules - len(temprxnlst))
                correction = temprxnlst.index(tempreactingmol)
                reactingmol = tempreactingmol + correction            
                temprxnlst.sortedinsert(reactingmol)
                self.LP_list[temprxnlst].Polymerize()
                #temprxnlst.append(reactingmol)
                #temprxnlst.sort()
        
        time_count = 0
        if self.VERBOSE:
            self.Be_Verbose()
        while(True):
            if not self.queue.empty():
                msg = self.queue.get()
                if msg[0] >= self.sim_Time:
                    if self.VERBOSE:
                        print('executive function is ending at time {sim_Time}'.format(
                            sim_Time=self.sim_Time))
                    break
                else:
                    if self.VERBOSE:
                        print('time', msg[0], 'transmitter', msg[1],
                              'recipient', msg[2], 'message', msg[3])
                    if not msg[2] in self.LP_dict:  # >=len(self.LP_list)
                        if self.VERBOSE:
                            print('unable to send above message')
                    else:
                        self.LP_dict[msg[2]].MYSimGetMsg(
                            msg[0], msg[1], msg[3])
                    #self.send_Message(msg[0], msg[1], msg[2], msg[3])
            else:
                # possibly (hopefully) unnecessary, but I don't know enough about threads to be sure
                time_count += 1
                if (time_count > self.sim_Time):
                    if self.VERBOSE:
                        print('executive function ending due to empty queue')
                    break

    def create_LPs(self, LPClass_func):
        for i in range(self.processes):
            # for better or worse, the class inserts it into this executive
            LPClass_func(self)
        return self.Get_List_Copy()

    def remove_LP(self, LP_remove_id: int):
        # self.LP_dict.remove_LP(LP_remove_id)
        self.LP_dict.pop(LP_remove_id)

    def send_Next(self, time: int, transmit_id: int, message: Executive.Event_Enum, rand_recip: bool = False):
        # simple function to put next message
        # time += self.Get_Lat() - now implemented in 'put'
        if time > self.sim_Time or len(self.LP_dict) - 1 < 1:
            if self.VERBOSE:
                print('message at {cur_time} was not sent'.format(
                    cur_time=time))
        else:
            # this is awful programming
            tempLP_list = list(self.LP_dict.keys())
            transmit_index = tempLP_list.index(transmit_id)
            if not rand_recip:
                recipient_id = tempLP_list[(
                    transmit_index+1) % len(self.LP_dict)]
            else:
                # random without sending back to same node
                temp_rand = random.randint(1, len(self.LP_dict) - 1)
                if temp_rand < transmit_index:
                    recipient_id = tempLP_list[temp_rand]
                else:
                    recipient_id = tempLP_list[(
                        temp_rand+1) % len(self.LP_dict)]
            if self.VERBOSE:
                print('recipient of', message, 'will be',
                      recipient_id, 'at time', time)
            self.putMessage(time, transmit_id, recipient_id, message)
            # the queue was implemented a bit late in the programming
            # self.LP_list[recipient_id].MYSimGetMsg(time, message, transmit_id) this function used to send directly

    def Be_Verbose(self):

        print("-r {:<10} (random_Seed)".format(self.random_Seed))
        print("-s {:<10} (sim_Time)".format(self.sim_Time))
        # if self.fixed_latency:
        #     print("-f (fixed latency)")
        print("-k {:<10} (lim_Latency)".format(self.lim_Latency))
        print("-p {:<10} (processes)".format(self.processes))

    def send_Message(self, time: int, transmit_id: int, recipient_id: int, message: Executive.Event_Enum):
        # old way of sending messages before implementing queue and/or list
        if time > self.sim_Time:
            if self.VERBOSE:
                print('a message has been stopped')
        else:
            #msgObject = self.LP_dict[recipient]
            self.message_count += 1

            self.putMessage(time, transmit_id, recipient_id, message)
            #self.LP_list[recipient_id].MYSimGetMsg(time, transmit_id, message)

    def Get_Lat(self) -> int:
        if self.fixed_latency:
            return self.lim_Latency
        else:
            return random.randint(1, self.lim_Latency)

    def Get_List_Copy(self):
        # return self.LP_dict.Get_List_Copy()
        return dict(self.LP_dict).items()

    def Get_List_Count(self):
        # return self.LP_dict.Get_List_count()
        return len(self.LP_dict)  # not as time intensive as Get_List_Copy

    def Get_VERBOSE(self) -> bool:
        return self.VERBOSE

    def Get_Count(self) -> int:
        return self.message_count
    
    def Reset_Random(self):
        random.setstate(self.init_random_state)
        self.Reset_Count()
        
    def Reset_Count(self):
        self.message_count = 0
