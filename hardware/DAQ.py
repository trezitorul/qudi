import os
import sys
from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import ULRange
from mcculw.ul import ULError
import time
import matplotlib.pyplot as plt
import numpy as np
import math
from pylab import *

# from core.configoption import ConfigOption
# from core.connector import Connector
# from logic.generic_logic import GenericLogic
# from qtpy import QtCore

from core.module import Base
from core.configoption import ConfigOption


class DAQ(Base):
    _range = ConfigOption(name='range', missing='error')
    _mode = ConfigOption(name='mode', missing='error')

    def on_activate(self):
        """ Initialisation performed during activation of the module.
         """
        self.board_num = 0
        self.mode=self._mode
        if self._range == "BIP10VOLTS":
            self.range = (1, -10., 10.)

        self.setMode(self.mode)
        # self.setZero()


    def on_deactivate(self):
        """
        Deinitialisation performed during deactivation of the module.
        """
        # self.setZero()
        pass


    def setMode(self,mode):
        '''
        Set the DAQ card to either "differential" or "single_ended"
        '''
        if mode == "differential":
            ul.a_input_mode(self.board_num, 0)
            self.mode = mode
            return 
        elif mode == "single_ended":
            ul.a_input_mode(self.board_num, 1)
            self.mode = mode
            return 
        else:
            print("error, please use either differential or single_ended")
            return "null"
    

    def getVoltage(self,channel_in):
        '''
        Return analog input channel's voltage
        '''
        value_in = ul.a_in(self.board_num, channel_in, self.range)
        voltage = ul.to_eng_units(self.board_num, self.range, value_in)
        return voltage
    

    def setVoltage(self,channel_out,voltage):
        '''
        Set the analog output channel's voltage
        '''
        voltage_pk = 10
        if abs(voltage) > abs(voltage_pk):
            print("invalid voltage on" + str(channel_out)+" of " + str(voltage) + "please reenter correct voltage")
            return
        else:
            print(voltage)
            voltVal=ul.from_eng_units(self.board_num, self.range, voltage)
            value_out = ul.a_out(self.board_num, channel_out, self.range,voltVal)
            return


    def setDiffVoltage(self,channel_high, channel_low,voltage):
        '''
        Set the analog output differential voltage between 2 channel
        '''
        voltage_pk = 20
        if abs(voltage) > abs(voltage_pk):
            print("invalid voltage please reenter correct voltage")
            return
        else:
            differential_voltage = voltage * 1/2
            voltValHigh=ul.from_eng_units(self.board_num, self.range, differential_voltage)
            voltValLow=ul.from_eng_units(self.board_num, self.range, -1 * differential_voltage)
            value_high = ul.a_out(self.board_num, channel_high, self.range,voltValHigh)
            value_low = ul.a_out(self.board_num, channel_low, self.range,voltValLow)
            return 


    def getDiffVoltage(self,channel_high,channel_low):
        '''
        Return differential voltage between 2 channels
        '''
        mode = self.mode
        if mode == "single_ended":
            return self.getVoltage(channel_high) - self.getVoltage(channel_low)
        elif mode == "differential": 
            if channel_low == channel_high + 1 and channel_high % 2 == 0:
                return self.getVoltage(channel_high // 2)
            else:
                print("please use correct channels, refer to manual to connect to correct pin in differential mode")
                return "null"
        else:
            print("please use correct mode, single_ended or differential")
            return "null"

    def setZero(self):
        '''
        Reset Galvo config
        '''
        for i in range(4):
            self.setVoltage(i,0)
        ul.release_daq_device(self.board_num)
        return


    def getCounts(self,dt, counterchannel):
        '''
        Implementing electrical pulse countings on the Daq cards
        '''
        # daq_dev_info = DaqDeviceInfo(self.board_num)
        # ctr_info = daq_dev_info.get_ctr_info()
        # if counterchannel != ctr_info.chan_info[counterchannel].channel_num:
        #     print("wrong channel")
        #     return "null"
        # else:
        print("counting")
        ul.c_clear(self.board_num, counterchannel)
        t=0
        while t <= dt:
            tstart= time.perf_counter()
            counts = ul.c_in_32(self.board_num, counterchannel)
            t = (time.perf_counter() - tstart) + t
        return counts