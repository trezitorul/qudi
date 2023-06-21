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

from core.connector import Connector
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class PowerMeterLogic(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """

    powermeter = Connector(interface='PM100D')

    # signals
    sigUpdateDisplay = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._powermeter = self.powermeter()

    def on_deactivate(self):
        """ Deactivate modeule.
        """
        pass
