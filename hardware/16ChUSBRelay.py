# -*- coding: utf-8 -*-
"""
Hardware module for 16 channel USB Relay Board from Sainsmart.

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

import serial
import time

from core.module import Base
from core.configoption import ConfigOption

class USB_Relay(Base):
    """ USB relay board with 16 channels.

    Example config for copy-paste:

    16Ch_Relay:
        module.Class: '16ChUSBRelay.USB_Relay'
        com_port: 'COM15'

    """
    
    # List of on/off byte commands for each channel
    channels = []
    for i in range(17):
        channels.append(0)
    channels[0] = {'off': b':FE0F00000010020000E1\r\n', 'on': b':FE0F0000001002FFFFE3\r\n'} #all channels
    channels[1] = {'off': b':FE0500000000FD\r\n', 'on': b':FE050000FF00FE\r\n'}
    channels[2] = {'off': b':FE0500010000FC\r\n', 'on': b':FE050001FF00FD\r\n'}
    channels[3] = {'off': b':FE0500020000FB\r\n', 'on': b':FE050002FF00FC\r\n'}
    channels[4] = {'off': b':FE0500030000FA\r\n', 'on': b':FE050003FF00FB\r\n'}
    channels[5] = {'off': b':FE0500040000F9\r\n', 'on': b':FE050004FF00FA\r\n'}
    channels[6] = {'off': b':FE0500050000F8\r\n', 'on': b':FE050005FF00F9\r\n'}
    channels[7] = {'off': b':FE0500060000F7\r\n', 'on': b':FE050006FF00F8\r\n'}
    channels[8] = {'off': b':FE0500070000F6\r\n', 'on': b':FE050007FF00F7\r\n'}
    channels[9] = {'off': b':FE0500080000F5\r\n', 'on': b':FE050008FF00F6\r\n'}
    channels[10] = {'off': b':FE0500090000F4\r\n', 'on': b':FE050009FF00F5\r\n'}
    channels[11] = {'off': b':FE05000A0000F3\r\n', 'on': b':FE05000AFF00F4\r\n'}
    channels[12] = {'off': b':FE05000B0000F2\r\n', 'on': b':FE05000BFF00F3\r\n'}
    channels[13] = {'off': b':FE05000C0000F1\r\n', 'on': b':FE05000CFF00F2\r\n'}
    channels[14] = {'off': b':FE05000D0000F0\r\n', 'on': b':FE05000DFF00F1\r\n'}
    channels[15] = {'off': b':FE05000E0000FF\r\n', 'on': b':FE05000EFF00F0\r\n'}
    channels[16] = {'off': b':FE05000F0000FE\r\n', 'on': b':FE05000FFF00FF\r\n'}

    status = b':FE0100200000FF\r\n'
    statusReturn = b':FE0100000010F1\r\n'

    com_port = ConfigOption(name='com_port', missing='error')
    
    def on_activate(self):
        """ Initialisation performed during activation of the module.
         """
        # Start serial connection
        self.ser = serial.Serial(
                        port = self.com_port,
                        baudrate = 9600,
                        timeout = 5
                )
        
    def on_deactivate(self):
        """
        Deinitialisation performed during deactivation of the module.
        """
        self.allOff()
        time.sleep(3)
        self.close()
                
    def switchOn(self, chan):
        """ Turns channel number 'chan' on.
        @param (int) chan: channel number to be turned on.
        """
        self.ser.write(self.channels[chan]['on'])

    def switchOff(self, chan):
        """ Turns channel number 'chan' off.
        @param (int) chan: channel number to be turned off.
        """
        self.ser.write(self.channels[chan]['off'])

    def allOn(self):
        """ Turns all channels on.
        """
        self.ser.write(self.channels[0]['on'])

    def allOff(self):
        """ Turns all channels off.
        """
        self.ser.write(self.channels[0]['off'])

    def close(self):
        """ Closes serial connection.
        """
        self.ser.close()

    def getStatus(self):
        """ Sends command to read status. Cannot understand the return message.
        @return bytes: a string of bytes from the relay board. (meaning unknown)
        """
        self.ser.write(self.statusReturn)
        return self.ser.readline()