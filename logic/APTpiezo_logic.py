# -*- coding: utf-8 -*-
"""
Buffer for simple data

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

import numpy as np
import time

from core.connector import Connector
from core.configoption import ConfigOption
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class APTpiezoLogic(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """

    aptpiezo1 = Connector(interface='APTpiezoInterface')
    aptpiezo2 = Connector(interface='APTpiezoInterface')
    queryInterval = ConfigOption('query_interval', 100)

    position = [0,0,0]

    # signals
    sigUpdateDisplay = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._aptpiezo1 = self.aptpiezo1()
        self._aptpiezo2 = self.aptpiezo2()
        self.stopRequest = False
        self.bufferLength = 100

        # delay timer for querying hardware
        self.queryTimer = QtCore.QTimer()
        self.queryTimer.setInterval(self.queryInterval)
        self.queryTimer.setSingleShot(True)
        self.queryTimer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)

        self.start_query_loop()

    def on_deactivate(self):
        """ Deactivate modeule.
        """
        pass

    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop. """
        self.module_state.run()
        self.queryTimer.start(self.queryInterval)

    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stopRequest = True
        for i in range(10):
            if not self.stopRequest:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.queryInterval/1000)
    
    @QtCore.Slot()
    def check_loop(self):
        """ Get position and update display. """
        if self.stopRequest:
            if self.module_state.can('stop'):
                self.module_state.stop()
            self.stopRequest = False
            return
        qi = self.queryInterval
        try:
            self.position = self.getPosition()

        except:
            qi = 3000
            self.log.exception("Exception in piezo status loop, throttling refresh rate.")

        self.queryTimer.start(qi)
        self.sigUpdateDisplay.emit()

    # def getMaxTravel(self, bay=0, channel=0, timeout=10):
    #     """
    #     Get maximum travel distance.

    #     :param bay: Index (0-based) of controller bay to send the command.
    #     :param channel: Index (0-based) of controller bay channel to send the command.
    #     """
    #     # self._log.debug(f"Gets maxTravel on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
    #     # self._loop.call_soon_threadsafe(self._write, apt.pz_req_maxtravel(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

    #     # self.message_event.wait(timeout=timeout)
    #     # self.message_event.clear()

    #     # return self.info[channel]["maxTravel"]
    #     return self._aptpiezo1.get_maxTravel()


    def setPosition(self, position=None):
        """
        Set the position of the piezo.
        ONLY WORKS IN CLOSED LOOP MODE
        Units: microns

        :param position: Output position relative to zero position; sets as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo extension aka maxTravel.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
    
        self._aptpiezo1.set_position(position=position[0], channel=0)
        self._aptpiezo1.set_position(position=position[1], channel=1)
        self._aptpiezo2.set_position(position=position[2], channel=0)


    def getPosition(self , bay=0, channel=0, timeout=10):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.
        Units: microns

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # currMode = self.info[channel]["mode"]

        # if (currMode != 0x02 and currMode != 0x04):
        #     raise ValueError("MUST BE IN CLOSED LOOP MODE")

        # self._log.debug(f"Sets position on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputpos(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        # self.message_event.wait(timeout=timeout)
        # self.message_event.clear()

        # position = self.info[channel]["position"]
        # maxTravel = self._aptpiezo1.info[channel-1]["maxTravel"]

        # return position/32767*maxTravel/10
        # position = [self._aptpiezo1.get_position(channel=0)/32767*maxTravel/10, self._aptpiezo1.get_position(channel=1)/32767*maxTravel/10, self._aptpiezo2.get_position(channel=0)/32767*maxTravel/10]
        position = [self._aptpiezo1.get_position(channel=0), self._aptpiezo1.get_position(channel=1), self._aptpiezo2.get_position(channel=0)]
        return position


    def set_zero(self , bay=0, channel=0):
        """
        Reads current position, and use that as reference for position 0.

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        # self._log.debug(f"Zero on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_set_zero(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        pass


    def get_ChannelState(self, bay=0, channel=0, timeout=10):
        """
        Get the current channel state. 

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        :param timeout: maximum delay for event to happpen
        """

        # self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.mod_req_chanenablestate(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        # self.message_event.wait(timeout=timeout)
        # self.message_event.clear()

        # return self.info[channel]["state"]
        pass


    def set_ChannelState(self, bay=0, channel=0, state=1):
        """
        Set the channel state. 

        :param state: state of the piezo's state. (1: Enabled; 2: Disabled)
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # if (state != 1 and state != 2):
        #     raise ValueError("ENABLED : 1; DISABLED: 2")

        # self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.mod_set_chanenablestate(source=EndPoint.HOST, dest=EndPoint.USB, chan_ident=self.channels[channel], enable_state=state))

        # self.info[channel]["state"] = state
        pass


    def set_controlMode(self, bay=0, channel=0, mode=1):
        """
        Set the control Mode. 
        0x01 Open Loop (no feedback)
        0x02 Closed Loop (feedback employed)
        0x03 Open Loop Smooth
        0x04 Closed Loop Smooth

        :param mode: Mode of the piezo
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        # if (mode < 0x01 or mode > 0x04):
        #     raise ValueError("CONTROL MODE MUST BE 0x01, 0x02, 0x03, or 0x04")

        # self._log.debug(f"Set Channel {channel} mode to {mode} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_set_positioncontrolmode(source=EndPoint.HOST, dest=EndPoint.USB, chan_ident=self.channels[channel], mode=mode))
        # self.info[channel]["mode"] = mode
        pass


    def get_controlMode(self, bay=0, channel=0, timeout=10):
        """
        Get current control mode. 
        0x01 Open Loop (no feedback)
        0x02 Closed Loop (feedback employed)
        0x03 Open Loop Smooth
        0x04 Closed Loop Smooth

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_req_positioncontrolmode(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        # self.message_event.wait(timeout=timeout)
        # self.message_event.clear()

        # return self.info[channel]["mode"]
        pass


    def set_voltage(self, voltage=None, bay=0, channel=0):
        """
        Set the piezo voltage. Must be in Open Loop Mode, and must be manually set to this mode beforehand in the main or it will not work.

        :param voltage: Set current voltage as an integer in the range 
                        from 0 to 32767, correspond to 0-100% of piezo's max voltage.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # currMode = self.info[channel]["mode"]

        # if (currMode != 0x01 and currMode != 0x03):
        #     raise ValueError("MUST BE IN OPEN LOOP MODE")

        # if (voltage == None):
        #     raise ValueError("PLEASE INPUT VOLTAGE")

        # currMax = self.info[channel]["maxVoltage"]
        # voltageOut=int(32767*(voltage/currMax))

        # self._log.debug(f"Sets output voltage {voltage} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltageOut))

        # self.info[channel]["voltage"] = voltage
        pass


    def get_voltage(self, bay=0, channel=0, timeout=10):
        """
        Get the piezo voltage.

        :param voltage: Get current voltage as an integer in the range 
                        from 0 to 32767, correspond to 0-100% of piezo's max voltage.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # self._log.debug(f"Gets voltage on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        # self.message_event.wait(timeout=timeout)
        # self.message_event.clear()

        # voltage = self.info[channel]["voltage"]
        # maxVoltage = self.info[channel]["maxVoltage"]

        # return voltage/32767*maxVoltage
        pass


    def get_serial(self, bay=0, timeout=10):
        """
        Get serial number.

        :param bay: Index (0-based) of controller bay to send the command.
        """    
        # self._log.debug(f"Gets serial number [bay={self.bays[bay]:#x}.")
        # self._loop.call_soon_threadsafe(self._write, apt.hw_req_info(source=EndPoint.HOST, dest=self.bays[bay]))

        # self.message_event.wait(timeout=timeout)
        # self.message_event.clear()

        # return str(self.info[0]["serial_number"])
        pass
