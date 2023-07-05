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
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.DCServoCLI.dll")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")
clr.AddReference('System')

from System import Decimal
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.GenericMotorCLI import GenericMotorCLI
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo

class PolarizationMotor(Base):
    """ Hardware module for polarization motor.
    """

    _deviceID = ConfigOption(name='deviceID', missing='error')
    _maxvelocity = ConfigOption(name='maxvelocity', missing='error')


    def on_activate(self):
        self.deviceID = self._deviceID
        self.maxvelocity = self._maxvelocity
        self.position = 0

        self._polarMotor = self.setup_device(self.deviceID)

        self.home_motor()
        self.set_velocity(self.maxvelocity)
        
    
    def on_deactivate(self):
            pass


    def setup_device(self,deviceID):
        '''
        Create motors
        '''
        DeviceManagerCLI.BuildDeviceList()
        self.device = KCubeDCServo.CreateKCubeDCServo(self.deviceID)
        self.device.Connect(self.deviceID)
        self.device.StartPolling(1)
        time.sleep(0.25)
        self.device.EnableDevice()
        time.sleep(0.25)
        self.config = self.device.LoadMotorConfiguration(deviceID)
        self.config.DeviceSettingsName = "MTS25"
        self.config.UpdateCurrentConfiguration()

        return self.device


    def set_position(self, degree):
        '''
        turn the motor to the desired degree
        '''
        self.device.MoveTo(Decimal(float(degree)), 10000)
        self.position = Decimal.ToDouble(self.device.Position)

    
    def get_position(self):
        return Decimal.ToDouble(self.device.Position)


    def home_motor(self):
        self.device.Home(60000)

    
    def set_velocity(self, max_velocity):
        velparams = self.device.GetVelocityParams()
        velparams.MaxVelocity = Decimal(float(max_velocity))
        self.device.SetVelocityParams(velparams)
