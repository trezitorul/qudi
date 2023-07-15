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
import pyfirmata


class StepperMotorLogic(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """

    stepperMotor1 = Connector(interface='StepperMotor')
    stepperMotor2 = Connector(interface='StepperMotor')
    com_port = ConfigOption(name='com_port', missing='error')
    queryInterval = ConfigOption('query_interval', 100)

    # signals
    sigUpdateDisplay = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self.board = pyfirmata.Arduino(self.com_port)
        self._stepperMotor1 = self.stepperMotor1()
        self._stepperMotor2 = self.stepperMotor2()

        self._stepperMotor1.initialize(self.board)
        self._stepperMotor2.initialize(self.board)
        self.stopRequest = False
        self.position = (0, 0)
        self.rpm = 12

        # delay timer for querying hardware
        self.queryTimer = QtCore.QTimer()
        self.queryTimer.setInterval(self.queryInterval)
        self.queryTimer.setSingleShot(True)
        self.queryTimer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)

        self.start_query_loop()

    def on_deactivate(self):
        """ Deactivate modeule.
        """
        self.stop_query_loop()
        for i in range(5):
            time.sleep(self.queryInterval / 1000)
            QtCore.QCoreApplication.processEvents()

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
            self.log.exception("Exception in stepper motor status loop, throttling refresh rate.")

        self.queryTimer.start(qi)
        self.sigUpdateDisplay.emit()

    def move_abs(self, revolution=None):
        """
        :param position: Output position relative to zero position; sets as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo extension aka maxTravel.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
    
        self._stepperMotor.move_abs(revolution)

    
    def move_rel(self, axis, direction, step=1):
        if (axis == 0): self._stepperMotor1.move_rel(direction, step)
        if (axis == 1): self._stepperMotor2.move_rel(direction, step)



    def getPosition(self):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.
        Units: microns

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        positionX = self._stepperMotor1.get_pos()
        positionY = self._stepperMotor2.get_pos()
        return (positionX, positionY)
    

    def setRPM(self, rpm):
        self._stepperMotor1.set_rpm(rpm)
        self._stepperMotor2.set_rpm(rpm)
        self.rpm = rpm