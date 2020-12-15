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
#import threading
import waiting
import copy

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
    
    multi_exec_time = [] #contains a short array- [time, exec]
    TIMEPOS = 0
    EXECPOS = 1
    WAIT_TIME = 2
    randstate = None
    setstate = False
    
    collectedsnapshot1 = []
    snapshotpos = 0
    exec_switched = []
    allswitches = False
    spread = []
    #random_Seed = 42
    #sim_Time = 100
    #fixed_latency = True - currently does nothing
    #lim_Latency = 1
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

    def __init__(self, args, spread, randstate):
        super().__init__(args)
        self.random_Seed = args.random_Seed
        self.sim_Time = args.sim_Time
        self.fixed_latency = args.fixed_latency
        self.lim_Latency = args.lim_Latency
        self.processes = args.processes
        self.VERBOSE = args.VERBOSE
        self.switch = args.switch
        self.removed_LPs = {}
        self.LP_snapshot = [None for _ in range(len(spread))]
        self.collectedsnapshot = [False for _ in range(len(spread))]
        MYEventExecutive.spread = spread
        #MYEventExecutive.snapshotpos = 0
        
        
        #self.LP_dict = {} - defined in super
        #self.message_count = 0 - defined in super
        # self.LP_list = [] #was originally implemented as a dict with hashed values, but this with lists in python as an array-type structure
        # this seems like a simpler implementation
        self.queue = PriorityQueue()
        self.queue.put((self.sim_Time+1, None, None, None))
        #put a null message in the queue so the timer keeps on ticking through sim_Time
        #much of this program could be rewritten
        

        # this probably doesn't need to be initialized here
        #random.seed(self.random_Seed)
        #print('first random from ex', random.random())
        #print('first int  from ex', random.randint(1, 200))
        #if not self.set_state:
        #self.init_random_state = random.getstate()
        #random.setstate(randstate)
        #    self.set_state = True
        #self.Reset_Random() 
        #attempting without self.Reset_Random() does not produce repeatable results
        #print('random seed is -exec ', self.random_Seed)
        # it also probably doesn't hurt to have it initialized here
        self.rng = np.random.default_rng(seed=self.random_Seed)
        
        self.exec_id = len(self.multi_exec_time)
        #appended after so the len(list)-1 is not necessary
        self.current_time = -1
        self.multi_exec_time.append([self.current_time, self])
        MYEventExecutive.exec_switched = [False for _ in range (len(self.multi_exec_time))]
        self.WAIT_TIME = 2
        

    # inserts a MYSim_LP into the list, then gives back the id
    def insert_LP(self, LP: MYSim_LP, value_hash: int=-1) -> int:
        return super().insert_LP(LP, value_hash = value_hash)  # value_hash

    def putMessage(self, time: int, transmit_id: id, recipient_id: int, message: Executive.Event_Enum) -> bool:
        time += self.Get_Lat()
        self.queue.put((time, transmit_id, recipient_id, message))
        return True  # the message was sent, ideally should be a number of 'success' or 'error',
    # but that's beyond the scope of this project
    
    def collect_snapshots():
        #collects a snapshot of all the LPs
        for i in range (len(MYEventExecutive.multi_exec_time)):
            cur_exec = MYEventExecutive.multi_exec_time[i][MYEventExecutive.EXECPOS]
            
            #cur_exec.LP_snapshot[MYEventExecutive.snapshotpos] = (copy.deepcopy([*cur_exec.Get_List_Copy()]), cur_exec.removed_LPs.items())
            cur_exec.LP_snapshot[MYEventExecutive.snapshotpos] = (cur_exec.completeLPcopy(), cur_exec.completeremovedcopy())
            
            #print('checking', cur_exec.LP_snapshot)
            #print('checking type {} and type {}'.format(\
            #                type(cur_exec.LP_snapshot[MYEventExecutive.snapshotpos][0]), \
            #                    type(cur_exec.LP_snapshot[MYEventExecutive.snapshotpos][1])))
        MYEventExecutive.snapshotpos += 1
    
    def empty_queues() -> bool:
        for i in range(len(MYEventExecutive.multi_exec_time)):
            if not MYEventExecutive.multi_exec_time[i][MYEventExecutive.EXECPOS].queue.empty():
                return False
        return True
    
    def run_all_execs():
        #TODO: check and make sure other execs can process LPs that are improperly placed
        overtime_count = 0
        cur_exec_pos = 0
        cur_exec = MYEventExecutive.multi_exec_time[cur_exec_pos][MYEventExecutive.EXECPOS]
        while(True):
            if not cur_exec.queue.empty():
                msg = cur_exec.queue.get()
                
                if msg[0] > cur_exec.current_time:
                    if cur_exec.current_time > cur_exec.sim_Time: #msg[0] > 
                        if cur_exec.VERBOSE:
                            print('executive function is ending at time {sim_Time}'.format(
                                sim_Time=cur_exec.sim_Time))
                        break
                    cur_exec.multi_exec_time[cur_exec.exec_id][cur_exec.TIMEPOS] = cur_exec.current_time + 1
                    #if all current execution times are finished,
                    #show in the list it is ready for the next time increment
                    ex_min = MYEventExecutive.executive_min()
                    cur_exec.queue.put(msg)
                    
                    if ex_min > cur_exec.current_time and not MYEventExecutive.exec_switched[cur_exec.exec_id]:
                        #inch time forward, do cleanups and snapshots
                        cur_exec.switch_time()
                        #cur_exec.current_time = ex_min
                        #switch_time should update each current_time
                    else:
                        cur_exec_pos = (cur_exec_pos+1)%len(MYEventExecutive.multi_exec_time)
                        cur_exec = MYEventExecutive.multi_exec_time[cur_exec_pos][MYEventExecutive.EXECPOS]
                        
                        #the queue would not move forward if there is nothing
                        #so put in a dummy message
                        
                        #threading.Event.wait(self.WAIT_TIME)
                        #this should pause here until all threads have reached the correct time
                    
                else:
                    if cur_exec.VERBOSE and msg[1] != None:
                        print('time', msg[0], 'transmitter', msg[1],
                              'recipient', msg[2], 'message', msg[3])
                    if msg[1] != None and msg[2] in cur_exec.LP_dict:
                            cur_exec.LP_dict[msg[2]].MYSimGetMsg(\
                                msg[0], msg[1], msg[3])
                    elif msg[1] == None or msg[2] in cur_exec.removed_LPs:
                        #this is a null message or it is a message to a dead recipient
                        #it can safely be ignored
                        pass
                    else:
                        sent=False
                        for i in range(1, len(MYEventExecutive.multi_exec_time)):
                            #see if the LP is in another executives
                            if msg[2] in MYEventExecutive.multi_exec_time[(cur_exec_pos + i)%len(\
                               MYEventExecutive.multi_exec_time)][cur_exec.EXECPOS].LP_dict:
                                
                                MYEventExecutive.multi_exec_time[(cur_exec_pos + i)%len(\
                                    MYEventExecutive.multi_exec_time)][cur_exec.EXECPOS].LP_dict[msg[2]].MYSimGetMsg(\
                                    msg[0], msg[1], msg[3])
                                sent = True
                                break
                        if not sent:
                            print('unable to find message recipient for', msg)
                            #cur_exec.lost_LP(msg)
                    #self.send_Message(msg[0], msg[1], msg[2], msg[3])
            else:
                if not MYEventExecutive.empty_queues():
                    cur_exec_pos = (cur_exec_pos+1)%len(MYEventExecutive.multi_exec_time)
                    cur_exec = MYEventExecutive.multi_exec_time[cur_exec_pos][MYEventExecutive.EXECPOS]
                else:
                    # possibly (hopefully) unnecessary, but I don't know enough about threads to be sure
                    overtime_count += 1
                    if (overtime_count > cur_exec.sim_Time):
                        if cur_exec.VERBOSE:
                            print('executive function ending due to empty queue')
                        break
    
    def test_time_ex(self):
        if MYEventExecutive.executive_min() < self.current_time + 1:
            return False
        else:
            return True
    
    def executive_min():
        if len(MYEventExecutive.multi_exec_time)<1:
            return None
        ex_min = MYEventExecutive.multi_exec_time[0][MYEventExecutive.TIMEPOS]
        for i in range (1, len(MYEventExecutive.multi_exec_time)):
            if MYEventExecutive.multi_exec_time[i][MYEventExecutive.TIMEPOS] < ex_min:
                ex_min = MYEventExecutive.multi_exec_time[i][MYEventExecutive.TIMEPOS]
        return ex_min
    
    # def run_exec(self):
    #     #TODO: check and make sure other execs can process LPs that are improperly placed
    #     overtime_count = 0
    #     if self.VERBOSE:
    #         self.Be_Verbose()
    #     while(True):
    #         if not self.queue.empty():
    #             msg = self.queue.get()
    #             if msg[0] >= self.sim_Time:
    #                 if self.VERBOSE:
    #                     print('executive function is ending at time {sim_Time}'.format(
    #                         sim_Time=self.sim_Time))
    #                 break
    #             elif msg[0] > self.current_time:
    #                 self.multi_exec_time[self.exec_id][self.TIMEPOS] = self.current_time + 1
    #                 #if all current execution times are finished,
    #                 #show in the list it is ready for the next time increment
    #                 ex_min = MYEventExecutive.executive_min()
                    
    #                 if ex_min > self.current_time:
    #                     self.switch_time()
    #                     self.current_time = ex_min
    #                 else:
    #                     waiting.wait(self.test_time_ex)
    #                     #threading.Event.wait(self.WAIT_TIME)
    #                     #this should pause here until all threads have reached the correct time
    #             else:
    #                 if msg[0] > self.current_time + 1:
    #                     print('out of order event ', 'time', msg[0], 'transmitter', msg[1],
    #                           'recipient', msg[2], 'message', msg[3], 'occuring')
    #                 if self.VERBOSE:
    #                     print('time', msg[0], 'transmitter', msg[1],
    #                           'recipient', msg[2], 'message', msg[3])
    #                 if not msg[2] in self.LP_dict:  # >=len(self.LP_list)
    #                     if self.VERBOSE:
    #                         print('unable to send above message')
    #                 else:
    #                     self.LP_dict[msg[2]].MYSimGetMsg(
    #                         msg[0], msg[1], msg[3])
    #                 #self.send_Message(msg[0], msg[1], msg[2], msg[3])
    #         else:
    #             # possibly (hopefully) unnecessary, but I don't know enough about threads to be sure
    #             overtime_count += 1
    #             if (overtime_count > self.sim_Time):
    #                 if self.VERBOSE:
    #                     print('executive function ending due to empty queue')
    #                 break
    
    def test_poly_reaction(self, tempcount, rxnlen):
        if self.message_count < tempcount + 2*rxnlen:
            return False
        else:
            return True
    
    def run_poly(self, polymerize, area, DEFAULT_CONCENTRATION):
        #def React(ex: ev_exec.MYEventExecutive, LP_list: list):
        temprxnlst = []
        tempcount = self.message_count
        for i in range(self.sim_Time):
            waiting.wait(self.test_poly_reaction(tempcount, len(temprxnlst)))
            #if self.message_count < tempcount + 2*len(temprxnlst):
                
                #threading.Event.wait(2)
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
        
        overtime_count = 0
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
                overtime_count += 1
                if (overtime_count > self.sim_Time):
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
        self.removed_LPs[LP_remove_id] = self.LP_dict.pop(LP_remove_id)
        

    def send_Next(self, time: int, transmit_id: int, message: Executive.Event_Enum, rand_recip: bool = False):
        # simple function to put next message
        # time += self.Get_Lat() - now implemented in 'put'
        if time > self.sim_Time or len(self.LP_dict) - 1 < 1:
            if self.VERBOSE:
                print('message at {cur_time} was not sent'.format(
                    cur_time=time))
        else:
            tempLP_list = list(self.LP_dict.keys())
            transmit_index = tempLP_list.index(transmit_id)
            if not rand_recip:
                recipient_id = tempLP_list[(
                    transmit_index+1) % len(self.LP_dict)]
            else:
                # random without sending back to same node
                temp_rand = random.randint(0, len(self.LP_dict) - 2)
                if temp_rand < transmit_index:
                    recipient_id = tempLP_list[temp_rand]
                else:
                    recipient_id = tempLP_list[temp_rand+1]
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
            
    def switch_time(self):
        if not MYEventExecutive.exec_switched[self.exec_id]:
            #perform switch
            dbl_switches = self.switch*self.Get_List_Count()
            switches = math.floor(dbl_switches)
            switchrand = random.random()
            if dbl_switches-dbl_switches > switchrand:
                switches += 1
            if switches > 0 and len(self.multi_exec_time) > 1:
                LP_keys = [*self.LP_dict.keys()]
            else:
                LP_keys = []
                switches = 0
            for m in range (switches):
                
                if len(LP_keys)>0:
                    newexec = random.randint(0, len(self.multi_exec_time) - 2)
                    #print('newexec rand', newexec)
                    if newexec >= self.exec_id:
                        newexec += 1
                    switch_pos = random.randint(0, len(LP_keys) - 1)
                    #print('switchpos rand', switch_pos)
                    switch_key = LP_keys[switch_pos]
                    switch_LP = self.LP_dict[switch_key]
                    #change executive and id for the LP, add it to the exec dict
                    switch_LP.ex = self.multi_exec_time[newexec][self.EXECPOS]
                    
                    temptest = self.multi_exec_time[newexec][self.EXECPOS].insert_LP(self.LP_dict[switch_key], switch_LP.id)
                    if temptest != switch_LP.id:
                        raise ValueError('poor assignment of id {} to {}'.format(temptest, switch_LP.id))
                    #remove it from this exec, remove it from the list of keys
                    self.remove_LP(switch_key)
                    LP_keys.pop(switch_pos) #likely can improve efficiency of this
                else:
                    break
        MYEventExecutive.exec_switched[self.exec_id] = True
        cleanup = True
        for switchb in MYEventExecutive.exec_switched:
            if not switchb:
                cleanup = False
            #not all execs have finished cleanup
        if cleanup:    
            MYEventExecutive.exec_switched = [False for _ in range(len(self.multi_exec_time))]
            #reset the exec_switched array, check if a snapshot is needed
            if self.spread[self.snapshotpos] == self.current_time:
                MYEventExecutive.collect_snapshots()
            for ex_item in self.multi_exec_time:
                ex_item[self.EXECPOS].current_time = ex_item[self.TIMEPOS]
            # update the time for all items
                                
            
    def Get_Lat(self) -> int:
        if self.fixed_latency:
            return self.lim_Latency
        else:
            latrand = random.randint(1, self.lim_Latency)
            if self.VERBOSE:
                print('latrand is', latrand)
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
    
    def Get_Time(self):
        return self.current_time
    
    def Reset():
        MYEventExecutive.multi_exec_time = []
        MYEventExecutive.snapshotpos = 0
        #MYEventExecutive.set_state = False
        #MYEventExecutive.init_random_state = None
    
    def Reset_Random(self):
        random.setstate(self.init_random_state)
        self.Reset_Count()
        
    def Reset_Count(self):
        self.message_count = 0
        
    def completeLPcopy(self):
        LP_copy = []
        for key, LP in self.LP_dict.items():
            LP_copy.append((key, LP.GetCopy()))
        #print(LP_copy)
        return LP_copy
        
    def completeremovedcopy(self):
        removed_LP_copy = []
        for key, removed_LP in self.removed_LPs.items():
            removed_LP_copy.append((key, removed_LP.GetCopy()))
        #print(removed_LP_copy)
        return removed_LP_copy
