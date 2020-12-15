# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 17:22:30 2020

@author: arthu
"""
import apl_executive as Executive


class MYSim_LP():

    def __init__(self, ex: Executive.Executive, to_insert = True):  # makes IPing and IPong mostly unnecessary
        self.time = 0
        self.ex = ex #with multiple executives, this is necessary
        if to_insert:
            self.id = ex.insert_LP(self)
        self.count = 0
        self.msg_history = []

    def MYSimGetMsg(self, time: int, transmit_id: int, message: Executive.Event_Enum):
        print('poor message received')
        pass  # this should be overwritten
        # locates a message buffer
        # [you may not need this, this is one way of doing it]

    def MYSimSend(self, *args) -> bool:  # Sends a message (schedules an event)
        self.ex.send_Message(self, args)
        return True

    def MYSimNow(self) -> int:  # A function that returns the current simulation time, an int
        return self.time

    def MYSimLPMe(self) -> int:  # A function that returns the simulation object unique id
        return self.id

    # since C programming isn't used, it's not really important to have FPing and FPong memory cleanup