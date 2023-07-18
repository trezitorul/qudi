# -*- coding: utf-8 -*-
"""
Logic module for polar motor

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

from core.configoption import ConfigOption
from core.connector import Connector
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class PolarMotorLogic(GenericLogic):
    """ Logic module for 2 flipper mirrors.
    """

    pmotor = Connector(interface='PolarizationMotor')
    query_interval = ConfigOption('query_interval', 100)
    
    # signals
    sig_update_polar_motor_display = QtCore.Signal()

    # Connect signals

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._pmotor = self.pmotor()

        self.home_motor()

        self.stop_request = False
        self.buffer_length = 100

        # delay timer for querying hardware
        self.query_timer = QtCore.QTimer()
        self.query_timer.setInterval(self.query_interval)
        self.query_timer.setSingleShot(True)
        self.query_timer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)

        self.start_query_loop()



    def on_deactivate(self):
        """ Deactivate modeule.
        """
        self.stop_query_loop()
        for i in range(5):
            time.sleep(self.query_interval / 1000)
            QtCore.QCoreApplication.processEvents()


    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop. """
        self.module_state.run()
        self.query_timer.start(self.query_interval)


    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stop_request = True
        for i in range(10):
            if not self.stop_request:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.query_interval/1000)


    @QtCore.Slot()
    def check_loop(self):
        """ Get position and update display. """
        if self.stop_request:
            if self.module_state.can('stop'):
                self.module_state.stop()
            self.stop_request = False
            return
        qi = self.query_interval
        try:
            self.position = self.get_position()

        except:
            qi = 3000
            self.log.exception("Exception in piezo status loop, throttling refresh rate.")

        self.query_timer.start(qi)
        self.sig_update_polar_motor_display.emit()


    def set_position(self, degree):
        '''
        turn the motor to the desired degree
        '''
        self._pmotor.set_position(degree)
        self.position = self._pmotor.position
        self.sig_update_polar_motor_display.emit()


    def get_position(self):
        """Get curent position

        Returns:
            float: current degree
        """
        return self._pmotor.get_position()


    def home_motor(self):
        """ To home the motor
        """
        self._pmotor.home_motor()
       

