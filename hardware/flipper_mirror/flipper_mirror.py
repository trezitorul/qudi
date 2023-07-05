# -*- coding: utf-8 -*-

"""
Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

from PyQt5.QtCore import QObject
from interface.motor_interface import MotorInterface
from interface.process_control_interface import ProcessControlInterface
from core.module import Base

import os
import time
import logging
import sys
import clr
# import matplotlib.pyplot as plt
# from scipy import signal
from core.configoption import ConfigOption
import numpy as np
from ctypes import *
# from System import Decimal

sys.path.append(r"C:\\Program Files\\Thorlabs\\Kinesis")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.FilterFlipperCLI.dll")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceNotReadyException 
from Thorlabs.MotionControl.FilterFlipperCLI import FilterFlipper

class FlipperMirror(Base):
    """ Hardware module for flipper mirror.
    """

    _deviceID = ConfigOption(name='deviceID', missing='error')

    def on_activate(self):
        self.deviceID = self._deviceID
        self._FlipperMirror = self.SetupDevice(self.deviceID)

        # Reset the flipper
        self.HomeMirror()
        self.SetMode("on")
        pass
    
    def on_deactivate(self):
        self.device.StopPolling()
        self.device.Disconnect(True)

    
    def SetupDevice(self,deviceID):
        '''
        Create mirrors
        '''
        DeviceManagerCLI.BuildDeviceList()

        self.device = FilterFlipper.CreateFilterFlipper(str(deviceID))

        self.device.Connect(deviceID) #this does not like the camera
        self.device.StartPolling(250)
        time.sleep(0.25)
        self.device.EnableDevice()
        time.sleep(0.25)
        return self.device
        # pass

    def SetMode(self,mode):
        '''
        turn the mirror 90 degrees in relative to the main body (on) or 0 degree (off)
        '''
        if mode == 'on':
            self.device.SetPosition(2,60000)
        elif mode == 'off':
            self.device.SetPosition(1,60000)
        else:
            print('wrong mode, try again')
        return
        # pass
    
    def HomeMirror(self):
        '''
        Home mirror
        '''
        self.device.Home(60000)
        return
'''
basic demo
'''
#deviceID = "37005466"
#Mirror = MFF101FlipperMirror(deviceID)
#Mirror.HomeMirror()
#Mirror.SetMode("on")
