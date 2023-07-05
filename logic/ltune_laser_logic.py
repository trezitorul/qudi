#-*- coding: utf-8 -*-
"""
Laser management.

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

class LtuneLaserLogic(GenericLogic):

    laser = Connector(interface='LtuneLaser')
    
    # queryInterval = ConfigOption('query_interval', 100)
    sigUpdateLaserDisplay = QtCore.Signal()

    def on_activate(self):
        self._laser = self.laser()

    
    def on_deactivate(self):
        pass


    def enable_laser(self):
        self._laser.enable()

    def disable_laser(self):
        self._laser.disable()


    def set_power(self, power):
        '''
        turn the motor to the desired degree
        '''
        self._laser.set_outputPower(power)
        self.power = self._laser.power
        self.sigUpdateLaserDisplay.emit()


    def get_power(self):
        return self._laser.get_outputPower()

