#-*- coding: utf-8 -*-
"""

Logic module to control a relay board while implementing a killswitch for if DAQ counts surpass a certain threshold.

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

import time
import numpy as np
from qtpy import QtCore

from core.connector import Connector
from core.configoption import ConfigOption
from logic.generic_logic import GenericLogic
from interface.relay_logic_interface import RelayLogicInterface

class USB_RelaySafetyLogic(GenericLogic, RelayLogicInterface):
    """ Logic module controlling USB relay board while checking if counts are safe.
    """

    # connectors
    relay = Connector(interface='USB_Relay')
    counter = Connector(interface='DaqCounter')

    # config
    _thresh = ConfigOption('thresh', 1000000, missing='warn')

    # signals
    sigError = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._relay = self.relay()
        self._counter = self.counter()
        self.thresh = int(self._thresh)
        
        self._counter.sigUpdateDisplay.connect(self.checkCounts)
    
    def on_deactivate(self):
        """ Deactivate modeule.
        """
        pass

    def switchOn(self, chan):
        """ Turns channel number 'chan' on.
        @param (int) chan: channel number to be turned on.
        """
        self._relay.switchOn(chan)

    def switchOff(self, chan):
        """ Turns channel number 'chan' off.
        @param (int) chan: channel number to be turned off.
        """
        self._relay.switchOff(chan)

    def allOn(self):
        """ Turns all channels on.
        """
        self._relay.allOn()

    def allOff(self):
        """ Turns all channels off.
        """
        self._relay.allOff()

    def close(self):
        """ Closes serial connection.
        """
        self._relay.close()

    def checkCounts(self):
        """ Checks if counts surpass threshold, signalled by counter module query loop.
        """
        if self._counter.counts > self.thresh:
            self.allOff()
            self.sigError.emit()
            self._counter.sigUpdateDisplay.disconnect(self.checkCounts)

    def getIsSafe(self):
        """Gets a boolean for whether counts are at a safe level.
        @return (bool) isSafe: boolean for if counts are at a safe level.
        """
        isSafe = not (self._counter.counts > self.thresh)

        if isSafe:
            self._counter.sigUpdateDisplay.connect(self.checkCounts)

        return isSafe