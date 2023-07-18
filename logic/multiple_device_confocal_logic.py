# -*- coding: utf-8 -*-

"""
A module for controlling a specific confocal scanner setup. It is used as a bridge between
the standard confocal scanner logic and the specific hardware devices.

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

from logic.generic_logic import GenericLogic
from core.connector import Connector
from core.configoption import ConfigOption
from interface.confocal_scanner_interface import ConfocalScannerInterface


class MultConfocalLogic(GenericLogic, ConfocalScannerInterface):
    """
    Control multiple hardware devices to perform a confocal scan.
    """

    # connectors
    m=1
    um=1e-6*m
    fitlogic = Connector(interface='FitLogic') 
    galvo = Connector(interface='GalvoLogic')
    piezo = Connector(interface='ConfocalDevInterface')
    counter = Connector(interface='DAQ')
    mirrors = Connector(interface='FlipperMirrorLogic')

    # config
    _clock_frequency = ConfigOption('clock_frequency', 100, missing='warn')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """

        self._fit_logic = self.fitlogic()
        self._galvo = self.galvo()
        self._piezo = self.piezo()
        self._counter = self.counter()
        self._mirrors = self.mirrors()

        self._line_length = None
        self._num_points = 500
        self._points = np.empty([self._num_points, 7])
        self._points_z = np.empty([self._num_points, 4])


    def on_deactivate(self):
        """ Deactivate properly the confocal scanner.
        """
        self.reset_hardware()


    def reset_hardware(self):
        """ Resets the hardware, so the connection is lost and other programs can access it.

        @return int: error code (0:OK, -1:error)
        """
        # self._piezo.set_position(position=0)
        self._counter.setZero()
        self._mirrors.set_mode('on', 1)
        self._mirrors.set_mode('on', 2)

        return 0


    def get_position_range(self): 
        """ Returns the physical range of the scanner.

        @return float [N][2]: array of N ranges with an array containing lower and upper limit, preferably in SI unit.

        """
        xy=self._galvo.get_position_range() ##################################################### F I X ######################################################### FIX
        # z = [0, self._piezo.get_max_travel()]
        z = [0, self._piezo.get_max_travel()*self.um]

        return [xy[0], xy[1], z]


    def set_position_range(self, myrange=None):
        """ Sets the physical range of the scanner.

        Deprecated : This range should not be accessible by logic. Inherited from interface.

        @param float [N][2] myrange: array of N ranges with an array containing lower and upper limit

        @return int: error code (0:OK, -1:error)
        """
        pass


    def set_voltage_range(self, myrange=None):
        """ Sets the voltage range of the NI Card.

        Deprecated : This range should not be accessible by logic. Inherited from interface.

        @param float [2] myrange: array containing lower and upper limit

        @return int: error code (0:OK, -1:error)
        """
        pass

    def get_scanner_axes(self):
        """ Find out how many axes the scanning device is using for confocal and their names.
 
        @return list(str): list of axis names
 
        Example:
          For 3D confocal microscopy in cartesian coordinates, ['x', 'y', 'z'] is a sensible value.
          For 2D, ['x', 'y'] would be typical.
          You could build a turntable microscope with ['r', 'phi', 'z'].
          Most callers of this function will only care about the number of axes, though.
 
          On error, return an empty list.
        """
        return ['x', 'y', 'z']

    def get_scanner_count_channels(self):
        """ Returns the list of channels that are recorded while scanning an image.

        @return list(str): channel names

        Most methods calling this might just care about the number of channels.
        """
        return [1, 2]

    def set_up_scanner_clock(self, clock_frequency=None, clock_channel=None):
        """ Configures the hardware clock of the hardware that controls the acquisition timing.

        @param float clock_frequency: if defined, this sets the frequency of the clock
        @param str clock_channel: if defined, this is the physical channel of the clock

        @return int: error code (0:OK, -1:error)
        """
        if clock_frequency is not None:
            self._clock_frequency = float(clock_frequency)

        return 0

    def set_up_scanner(self,
                       counter_channels=None,
                       sources=None,
                       clock_channel=None,
                       scanner_ao_channels=None):
        """ Configures the actual scanner (does not use the clock variables, but they are inherited from the interface).

        @param str counter_channels: if defined, these are the physical counting devices
        @param str sources: if defined, these are the physical channels where
                                  the photons are to count from
        @param str clock_channel: if defined, this specifies the clock for the
                                  counter
        @param str scanner_ao_channels: if defined, this specifies the analoque
                                        output channels

        @return int: error code (0:OK, -1:error)
        """
        self._mirrors.set_mode('off', 1)
        self._mirrors.set_mode('off', 2)
        return 0

    def scanner_set_position(self, x=None, y=None, z=None, a=None):
        """ Move stage to x, y, z, a (inherited from interface, a is not used).

        @param float x: position in x-direction (in axis unit)
        @param float y: position in y-direction (in axis unit)
        @param float z: position in z-direction (in axis unit)
        @param float a: position in a-direction (in axis unit)

        @return int: error code (0:OK, -1:error)

        If a value is not set or set to None, the actual value is implied.
        """
        self._galvo.setPosition((x/self.um, y/self.um))
        self._piezo.set_position(position=z/self.um)
        return 0


    def get_scanner_position(self):
        """ Get the current position of the scanner hardware.

        @return tuple(float): current position as a tuple. Ex : (x, y, z, a).
        """
        xy = self._galvo.getPosition()
        z = self._piezo.get_position()
        return [xy[0], xy[1], z*self.um]


    def scan_line(self, line_path=None, pixel_clock=False):
        """ Scans a line and returns the counts on that line.

        @param float[k][n] line_path: array k of n-part tuples defining the pixel positions
        @param bool pixel_clock: whether we need to output a pixel clock for this line >> NOT USED, inherited from interface

        @return float[k][m]: the photon counts per second for k pixels with m channels
        """
        result = [[0 for y in range(2)] for x in range(len(line_path[0]))]

        for k in range(len(line_path[0])):
            count1 = 0
            count2 = 0
            self.scanner_set_position(x=line_path[0][k], y=line_path[1][k], z=line_path[2][k])
            count1 += self._counter.getCounts(dt=1/self._clock_frequency, counterchannel=0)
            count2 += self._counter.getCounts(dt=1/self._clock_frequency, counterchannel=1)
            result[k][0] = count1
            result[k][1] = count2
        
        return np.array(result)


    def _set_up_line(self, length=100):
        """ Sets up the analogue output for scanning a line.

        @param int length: length of the line in pixel

        @return int: error code (0:OK, -1:error)
        """

        self._line_length = length

        return 0


    def close_scanner(self):
        """ Closes the scanner and cleans up afterwards.

        @return int: error code (0:OK, -1:error)
        """
        return self.reset_hardware()

    def close_scanner_clock(self, power=0):
        """ Closes the clock and cleans up afterwards.

        @return int: error code (0:OK, -1:error)
        """
        return 0