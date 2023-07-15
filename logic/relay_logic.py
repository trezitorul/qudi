#-*- coding: utf-8 -*-
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

import time
import numpy as np
from qtpy import QtCore

from core.connector import Connector
from core.configoption import ConfigOption
from logic.generic_logic import GenericLogic
from interface.relay_logic_interface import RelayLogicInterface

class USB_RelayLogic(GenericLogic, RelayLogicInterface):

    relay = Connector(interface='USB_Relay')

    sigError = QtCore.Signal()
    sigError2 = QtCore.Signal(bool)
    

    def on_activate(self):
        self._relay = self.relay()

    
    def on_deactivate(self):
        pass

    def switchOn(self, chan):
        self._relay.switchOn(chan)

    def switchOff(self, chan):
        self._relay.switchOff(chan)

    def allOn(self):
        self._relay.allOn()

    def allOff(self):
        self._relay.allOff()

    def close(self):
        self._relay.close()