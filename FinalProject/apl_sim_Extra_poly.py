# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 22:35:29 2020

@author: arthu
"""
import random
import aenum
#import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
import apl_poly_event_executive as ev_exec
import MYSim_LP_Class as MYSim_LP
#from enum import Enum

class State(MYSim_LP.ev_exec.Event_Enum, aenum.IntEnum):
    MONOMER = 1
    MER = 2
    POLYMER = 500
    
    def name(self) -> str:
        if(self.value < State['MONOMER'].value):
            return 'null-mer, you messed up' #0 length monomer, this shouldn't happen
        if(self.value < State['MER'].value):
            return 'monomer'
        elif(self.value > State['MER'].value - 1 and self.value < State['POLYMER'].value):
            return '-mer'
        else:
            return 'polymer'

class MYCircling_LP(MYSim_LP.MYSim_LP):
    
    #def __init__(self, ex: MYSim_LP.ev_exec.MYEventExecutive):
    #    self.msg_history = [(int, int, State)]
    
    def __init__(self, ex: MYSim_LP.ev_exec.MYEventExecutive, state: State=State(1)):
        #self.time = 0
        #self.ex = ex
        #self.id = self.ex.insert_LP(self)
        #self.msg_history = []
        super().__init__(ex)
        self.state = state
        self.rep_groups = 0 #here count does not mean the number of messages
        self.msg_history = [(int, int, State)]
        
    def MYSimGetMsg(self, time: int, transmit_id: int, state: State): #overwriting message behavior to convert to pingpong
        self.msg_history.append((transmit_id, time, state))
        self.rep_groups += state
        self.ex.remove_LP(transmit_id)
        #if self.ex.Get_VERBOSE():
        #    print(self.state, 'is now', state, 'at time', time)
        #self.state = state
        self.time = time
        self.Polymerize()
    
    def __repr__(self):
        return str(self.id) + ' Object'
    
    def GetState(self) -> str:
        return self.state.name()
    
    def GetCount(self) -> int:
        return self.count
    
    def Polymerize(self):
        self.count += 1
        if self.ex.Get_VERBOSE():
            print(str(self),"received message at time", self.time)
        self.ex.send_Next(self.time, self.id, self.rep_groups, rand_recip = True)
            
    def GetRepGroups(self):
        return self.rep_groups
        
    def Initialize(self): #initial start to pingpong
        if self.ex.Get_VERBOSE():
            print('starting ' + self.state.name())
        self.ex.send_Next(self.time, self.id, self.rep_groups, rand_recip = True)
        #self.MySimSend(self.time, self.state, dest)
    
    def PingPong(self, state: State, transmit_id: int):
        
        self.count += 1
        if self.ex.Get_VERBOSE():
            print(str(self),"received message at time", self.time)
        transmit_state = State((self.state.value+1)%len(State))
        print(transmit_state)
        self.ex.send_Next(self.time, self.id, transmit_state)
        #self.ex.send_Message(self.time, self.id, self.state, transmit_id)
        #self.MySimSend(self.time, self.state, transmit_id)
            
    def IPingPong(self, dest: MYSim_LP): #initial start to pingpong
        if self.ex.Get_VERBOSE():
            print('starting ' + self.state.name())
        transmit_state = State((self.state.value+1)%len(State))
        print(transmit_state)
        self.ex.send_Next(self.time, self.id, transmit_state)
    
    
    
    #alternate to MYSimSend - direct through ex - self.ex.send_Message(self, self.state, transmit_id)
    
    

def MYSimInitApplication(): # int argc, char ** argv   

    ex = ev_exec.MYEventExecutive()
    LPList = ex.create_LPs(MYCircling_LP)
    if ex.Get_VERBOSE():
        print(LPList)
    
    LPDict = ex.Get_LP_Dict()
    
    #LPList = ex.Get_List_Copy()
    
    #Pong = MYPingPong_LP(ex, State(2))
    if (len(LPList) > 0):
        LPDict[LPList[0]].Initialize()
    ex.run_exec()
    
    LPList = ex.Get_List_Copy()
    if ex.Get_VERBOSE():
        print(LPList)
    print('this circling simulation had {num} trips'.format(num=(ex.Get_Count())))
    
    #int IPing(), IPong(); 	# declare application handlers, the initializers.
    #int Ping(), Pong();   	# declare application handlers
    #int FPing(), FPong();  	# declare application wrap-up handlers
    
    #MYSim_numLPs = 2;       	# number of LPs that participate in simulation
    
    #MySim_LP[0].IProc  = IPing; 	# set initializer handler of LP 0  to IPing handler
    #MySim_LP[0].Proc   = Ping;  	# set 'regular'   handler of LP 0  to Ping handler
    #MySim_LP[0].FProc  = FPing; 	# set wrap-up     handler of LP 0  to FPing handler
    
    #MySim_LP[1].IProc  = IPong; 	# set initializer handler of LP 1  to IPong handler
    #MySim_LP[1].Proc   = Pong;  	# set 'regular'   handler of LP 1  to Pong handler
    #MySim_LP[1].FProc  = FPong; 	# set wrap-up     handler of LP 1  to FPong handler
    
    # set random generator seeds - per LP or just once  - up to you.
    #MySim_RandInit( ); # part of simulation executive.



#class Ping(PingPong):
#    def __init(self):
#        self.state = State(1)

#class Pong(PingPong):
#    def __init(self):
#        self.state = State(2)    




#def IPing(): #initializes ping LP
#    pass
#def IPong(): # initializes pong LP
#    pass
#def FPing(): # finishes ping
#    pass
#def FPong(): # finishes pong
#    pass

#variables and methods that hook to the simulation executive denoted by:
    #MYSim_
#def IProc(): # initializes
#    pass
#def Proc():  # regular message process received by an LP
#    pass
#def FProc(): # final
#    pass
#abstract the LPs - assign unique identification number, then map processes to
    #application LPs - similar to method in textbook - should know
    #should know memory area where to maintain simulation state
    #single global initialization handler
#def MYSimInitApplication(): #initialization
#    pass
if (__name__ == '__main__'):
    MYSimInitApplication()




# =============================================================================
# 
# 
# 
# 
# #Data Structures:
# #---------------
# 
# #define Num_LPS 2 ---> set number of LPs
# 
# # you need to keep state somewhere.
# struct MYSim_LPState  # allocate state 
#  {
#  struct MyVars CVars;  # name whatever you want.
#  }
# 
# struct MYSim_MsgData
# {
#   int some_data; # whatever data type you need for your simulation can be a struct/or class.
# }
# 
# #Initialization:
# #--------------
# 
# MYSimInitApplication( int argc, char ** argv )
# {
#   int IPing(), IPong(); 	# declare application handlers, the initializers.
#   int Ping(), Pong();   	# declare application handlers
#   int FPing(), FPong();  	# declare application wrap-up handlers
# 
#   MYSim_numLPs = 2;       	# number of LPs that participate in simulation
# 
#   MySim_LP[0].IProc  = IPing; 	# set initializer handler of LP 0  to IPing handler
#   MySim_LP[0].Proc   = Ping;  	# set 'regular'   handler of LP 0  to Ping handler
#   MySim_LP[0].FProc  = FPing; 	# set wrap-up     handler of LP 0  to FPing handler
# 
#   MySim_LP[1].IProc  = IPong; 	# set initializer handler of LP 1  to IPong handler
#   MySim_LP[1].Proc   = Pong;  	# set 'regular'   handler of LP 1  to Pong handler
#   MySim_LP[1].FProc  = FPong; 	# set wrap-up     handler of LP 1  to FPong handler
# 
#   # set random generator seeds - per LP or just once  - up to you.
#   MySim_RandInit( ); # part of simulation executive.
# }
# 
# 
# #Initialization Phase:
# #---------------------
# 
# # Ping - similar structure for Pong
# IPing( struct MYSim_State *SS ) 
# {
# struct MYSim_MsgData *MYSimMsg; # pointer to storage for messages
# 
# SS = MYSim_LP[ MYSimLPMe() ].State; # my local state [make sure it is allocated]
# 
# time_stamp = MySim_RandomExponential( some_seed, some_mean ); # optional to implement 
# MYSim_GetMsg( time_stamp, destination_LP, size_message ) ;     # pseudo-code 
# 							     # gets message buffer sets it
#                                                   # to MYSimMsg, send it to neighbor LP ex:
# 						  # MYSimLPMe() mod 2
# 
# #modify message to be sent
# MySim_Msg->some_content = MySimMsg->some_content +1;  # set message content.
# 
# MySim_Send(); # Send / Schedule Message
# 
# }
# 
# # event handler for Ping - similar one for Pong
# Ping( struct SimState *SS, struct Message *M ):
# {
# struct MYSim_MsgData *MYSimMsg; # pointer to storage for messages
# 
# # set state
# SS->CVars.some_data = SS->CVars.some_data + 1;
# 
# # bounce message back to Pong
# # generate a time stamp increment (fron now) perhaps randomly using a exponential distribution
# time_stamp = randomlygenerated();
# MYSim_GetMsg( time_stamp, destination_LP, size_message ) ;     # pseudo-code
# MySim_Msg->some_content = MySimMsg->some_content +1;  # set message content.
# MySim_Send(); # Send / Schedule Message
# 
# 
# }
# 
# FPing( struct SimState *SS, struct Message *M ) 
# {
# print out content of SS.
# }
# 
# 
# #Messages/Scheduling of events:
# #-----------------------------
# 
# #Sending message function:
# #Function: Enqueues Event into event queue.
# 
# MYSimGetMsg() 	#Allocates a message buffer 
# 		#[you may not need this, this is one way of doing it]
# 
# MySimSend() 	#Sends a message (schedules an event)
# 	   	#[schedules an event - and enqueues into the pending event queue]
# 
# #Other functions you may want to support:
# #---------------------------------------
# 
# MYSimNow() 	#A function that returns the current simulation time
# MYSimLPMe() 	#A function that returns my unique LP ID.
# 
# =============================================================================
