# -*- coding: utf-8 -*-

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

from PyQt5.QtCore import QObject
from core.module import Base
from hardware.motor.stepper import Stepper
from core.configoption import ConfigOption


class StepperMotor (Base):
    # def __init__(self):
    #     super().__init__()
    _motor_pin_1 = ConfigOption(name='motor_pin_1', missing='error')
    _motor_pin_2 = ConfigOption(name='motor_pin_2', missing='error')
    _motor_pin_3 = ConfigOption(name='motor_pin_3', missing='error')
    _motor_pin_4 = ConfigOption(name='motor_pin_4', missing='error')
    
    
    def on_activate(self):
        pass

    def initialize(self, board):
        self.board = board
        self.stepsPerRevolution = 2048
        self.rpm = 12
        self.position = 0

        self._Stepper = Stepper(self.board, self.stepsPerRevolution, self._motor_pin_1, self._motor_pin_3, self._motor_pin_2, self._motor_pin_4)
        self._Stepper.setSpeed(self.rpm)

    def on_deactivate(self):
        # self.move_abs(0)
        return

    
    def move_abs(self, revolution):
        """ Moves stage to absolute revolution (absolute movement)

        @param dict param_dict: dictionary, which passes all the relevant
                                parameters, which should be changed. Usage:
                                 {'axis_label': <the-abs-pos-value>}.
                                 'axis_label' must correspond to a label given
                                 to one of the axis.

        @return int: error code (0:OK, -1:error)
        """
        # if (revolution > 0):
        #     self._Stepper.step(revolution - self.revolution)
        #     self.revolution = revolution
        #     return 0
        # else: return -1
        pass


    def move_rel(self,  direction, step=1):
        """ Moves stage in given direction (relative movement)

        @param dict param_dict: dictionary, which passes all the relevant
                                parameters, which should be changed. Usage:
                                 {'axis_label': <the-abs-pos-value>}.
                                 'axis_label' must correspond to a label given
                                 to one of the axis.

        A smart idea would be to ask the position after the movement.

        @return int: error code (0:OK, -1:error)
        """

        self._Stepper.step(step * direction)
        self.position += step * direction


    def get_pos(self):
        """ Gets current position of the stage arms

        @param list param_list: optional, if a specific position of an axis
                                is desired, then the labels of the needed
                                axis should be passed in the param_list.
                                If nothing is passed, then from each axis the
                                position is asked.

        @return dict: with keys being the axis labels and item the current
                      position.
        """
        return self.position


    def get_rpm(self):
        """ Gets the current velocity for all connected axes.

        @param dict param_list: optional, if a specific velocity of an axis
                                is desired, then the labels of the needed
                                axis should be passed as the param_list.
                                If nothing is passed, then from each axis the
                                velocity is asked.

        @return dict : with the axis label as key and the velocity as item.
        """
        return self.rpm


    def set_rpm(self, rpm):
        """ Write new value for velocity.

        @param dict param_dict: dictionary, which passes all the relevant
                                parameters, which should be changed. Usage:
                                 {'axis_label': <the-velocity-value>}.
                                 'axis_label' must correspond to a label given
                                 to one of the axis.

        @return int: error code (0:OK, -1:error)
        """
        self._Stepper.setSpeed(rpm)
        self.rpm = rpm

