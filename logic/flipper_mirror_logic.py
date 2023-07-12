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

from core.configoption import ConfigOption
from core.connector import Connector
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class FlipperMirrorLogic(GenericLogic):
    """ Logic module for 2 flipper mirrors.
    """

    flipper1 = Connector(interface='FlipperMirror')
    flipper2 = Connector(interface='FlipperMirror')

    # signals
    sigUpdatePMDisplay = QtCore.Signal()

    # Connect signals

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._flipper1 = self.flipper1()
        self._flipper2 = self.flipper2()

        self.home_mirrors()


    def on_deactivate(self):
        """ Deactivate modeule.
        """
        pass


    def set_mode(self, mode, num):
        if num == 1:
            self._flipper1.SetMode(mode)
        else:
            self._flipper2.SetMode(mode)
            pass


    def home_mirrors(self):
        self._flipper1.HomeMirror()
        self._flipper2.HomeMirror()
        

