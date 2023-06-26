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


class PowerMeterLogic(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """

    powerMeter = Connector(interface='ProcessInterface')
    queryLoop = Connector(interface='QueryLoopLogic')
    # queryInterval = ConfigOption('query_interval', 100)

    # signals
    # sigUpdatePMDisplay = QtCore.Signal()

    # Connect signals

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._powermeter = self.powerMeter()
        self._queryLoop = self.queryLoop()

        # self.stopRequest = False
        # self.bufferLength = 100

        self.power = 0
        self._queryLoop.sigUpdateVariable.connect(self.get_power)

        # delay timer for querying hardware
        # self.queryTimer = QtCore.QTimer()
        # self.queryTimer.setInterval(self.queryInterval)
        # self.queryTimer.setSingleShot(True)
        # self.queryTimer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)


    def on_deactivate(self):
        """ Deactivate modeule.
        """
        # self.stop_query_loop()
        # for i in range(5):
        #     time.sleep(self.queryInterval / 1000)
        #     QtCore.QCoreApplication.processEvents()
        pass

    # @QtCore.Slot()
    # def start_query_loop(self):
    #     """ Start the readout loop. """
    #     self.module_state.run()
    #     self.queryTimer.start(self.queryInterval)

    # @QtCore.Slot()
    # def stop_query_loop(self):
    #     """ Stop the readout loop. """
    #     self.stopRequest = True
    #     for i in range(10):
    #         if not self.stopRequest:
    #             return
    #         QtCore.QCoreApplication.processEvents()
    #         time.sleep(self.queryInterval/1000)

    # @QtCore.Slot()
    # def check_loop(self):
    #     """ Get power and update display. """
    #     if self.stopRequest:
    #         if self.module_state.can('stop'):
    #             self.module_state.stop()
    #         self.stopRequest = False
    #         return
    #     qi = self.queryInterval
    #     try:
    #         self.power = self._powermeter.get_process_value()

    #     except:
    #         qi = 3000
    #         self.log.exception("Exception in power meter status loop, throttling refresh rate.")

    #     self.queryTimer.start(qi)
    #     self.sigUpdatePMDisplay.emit()


    def get_power(self):
        self.power = self._powermeter.get_process_value()
        return self.power