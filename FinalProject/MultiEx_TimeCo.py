# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 14:04:31 2020
Coordinates the timing between multiple executives
@author: arthu
"""

import apl_executive as Executive

class GlobalTime():
    
    def __init__(self):
        self.execlist = []
        
    def addexec(self, exec: Executive):
        self.execlist.append(exec)