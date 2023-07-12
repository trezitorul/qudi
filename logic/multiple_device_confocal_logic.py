import numpy as np
import time

from logic.generic_logic import GenericLogic
from core.connector import Connector
from core.configoption import ConfigOption
from interface.confocal_scanner_interface import ConfocalScannerInterface


class MultConfocalLogic(GenericLogic, ConfocalScannerInterface):
    # connectors
    fitlogic = Connector(interface='FitLogic') 
    galvo = Connector(interface='GalvoLogic')
    piezo = Connector(interface='ConfocalDevInterface')
    counter = Connector(interface='DAQ')
    mirrors = Connector(interface='FlipperMirrorLogic')

    # config
    _clock_frequency = ConfigOption('clock_frequency', 100, missing='warn')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

        # Internal parameters

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
        z = [0, self._piezo.get_max_travel()]

        return [xy[0], xy[1], z]


    def set_position_range(self, myrange=None):
        """ Sets the physical range of the scanner.

        Deprecated : This range should not be accessible by logic. TODO: Discuss and remove from interface ?

        @param float [N][2] myrange: array of N ranges with an array containing lower and upper limit

        @return int: error code (0:OK, -1:error)
        """
        pass


    def set_voltage_range(self, myrange=None):
        """ Sets the voltage range of the NI Card.

        Deprecated : This range should not be accessible by logic. TODO: Discuss and remove from interface ?

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

        TODO: the clock_channel argument is unused and should not be known by the logic.
        TODO: Discuss and remove from interface ?

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
        """ Configures the actual scanner with a given clock.

        @param str counter_channels: if defined, these are the physical counting devices
        @param str sources: if defined, these are the physical channels where
                                  the photons are to count from
        @param str clock_channel: if defined, this specifies the clock for the
                                  counter
        @param str scanner_ao_channels: if defined, this specifies the analoque
                                        output channels

        @return int: error code (0:OK, -1:error)

        TODO: Again, should the multiple clocks controlled by logic be in this interface ?
        """
        self._mirrors.set_mode('off', 1)
        self._mirrors.set_mode('off', 2)
        return 0

    def scanner_set_position(self, x=None, y=None, z=None, a=None):
        """ Move stage to x, y, z, a (where a is the fourth channel).

        @param float x: position in x-direction (in axis unit)
        @param float y: position in y-direction (in axis unit)
        @param float z: position in z-direction (in axis unit)
        @param float a: position in a-direction (in axis unit)

        @return int: error code (0:OK, -1:error)

        If a value is not set or set to None, the actual value is implied.
        """
        self._galvo.setPosition((x, y))
        self._piezo.set_position(position=z)
        return 0


    def get_scanner_position(self):
        """ Get the current position of the scanner hardware.

        @return tuple(float): current position as a tuple. Ex : (x, y, z, a).
        """
        xy = self._galvo.getPosition()
        z = self._piezo.get_position()
        return [xy[0], xy[1], z]


    def scan_line(self, line_path=None, pixel_clock=False):
        """ Scans a line and returns the counts on that line.

        @param float[k][n] line_path: array k of n-part tuples defining the pixel positions
        @param bool pixel_clock: whether we need to output a pixel clock for this line

        TODO: Give a detail explanation of pixel_clock argument, how it is used in practice and why it is necessary.

        @return float[k][m]: the photon counts per second for k pixels with m channels
        """
        result = [[0 for y in range(2)] for x in range(len(line_path[0]))]
        # print(np.shape(line_path))
        # print(np.shape(result))

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
        """ Sets up the analoque output for scanning a line.

        @param int length: length of the line in pixel

        @return int: error code (0:OK, -1:error)
        """

        self._line_length = length

#        self.log.debug('ConfocalScannerInterfaceDummy>set_up_line')
        return 0


    def close_scanner(self):
        """ Closes the scanner and cleans up afterwards.

        @return int: error code (0:OK, -1:error)

        TODO: Give a detail explanation how it is used in practice and why it is necessary.
        """
        return self.reset_hardware()

    def close_scanner_clock(self, power=0):
        """ Closes the clock and cleans up afterwards.

        @return int: error code (0:OK, -1:error)

        TODO: Give a detail explanation how it is used in practice and why it is necessary.
        """
        return 0

############################################################################
#                                                                          #
#    the following two functions are needed to fluoreschence signal        #
#                             of the dummy NVs                             #
#                                                                          #
############################################################################


    def twoD_gaussian_function(self, x_data_tuple=None, amplitude=None,
                               x_zero=None, y_zero=None, sigma_x=None,
                               sigma_y=None, theta=None, offset=None):

        #FIXME: x_data_tuple: dimension of arrays

        """ This method provides a two dimensional gaussian function.

        @param (k,M)-shaped array x_data_tuple: x and y values
        @param float or int amplitude: Amplitude of gaussian
        @param float or int x_zero: x value of maximum
        @param float or int y_zero: y value of maximum
        @param float or int sigma_x: standard deviation in x direction
        @param float or int sigma_y: standard deviation in y direction
        @param float or int theta: angle for eliptical gaussians
        @param float or int offset: offset

        @return callable function: returns the function

        """
        # check if parameters make sense
        #FIXME: Check for 2D matrix
        if not isinstance( x_data_tuple,(frozenset, list, set, tuple, np.ndarray)):
            self.log.error('Given range of axes is no array type.')

        parameters = [amplitude, x_zero, y_zero, sigma_x, sigma_y, theta, offset]
        for var in parameters:
            if not isinstance(var, (float, int)):
                self.log.error('Given range of parameter is no float or int.')

        (x, y) = x_data_tuple
        x_zero = float(x_zero)
        y_zero = float(y_zero)

        a = (np.cos(theta)**2) / (2 * sigma_x**2) + (np.sin(theta)**2) / (2 * sigma_y**2)
        b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
        c = (np.sin(theta)**2) / (2 * sigma_x**2) + (np.cos(theta)**2) / (2 * sigma_y**2)
        g = offset + amplitude * np.exp(
            - (a * ((x - x_zero)**2)
                + 2 * b * (x - x_zero) * (y - y_zero)
                + c * ((y - y_zero)**2)))
        return g.ravel()

    def gaussian_function(self, x_data=None, amplitude=None, x_zero=None,
                          sigma=None, offset=None):
        """ This method provides a one dimensional gaussian function.

        @param array x_data: x values
        @param float or int amplitude: Amplitude of gaussian
        @param float or int x_zero: x value of maximum
        @param float or int sigma: standard deviation
        @param float or int offset: offset

        @return callable function: returns a 1D Gaussian function

        """
        # check if parameters make sense
        if not isinstance( x_data,(frozenset, list, set, tuple, np.ndarray)):
            self.log.error('Given range of axis is no array type.')

        parameters=[amplitude,x_zero,sigma,offset]
        for var in parameters:
            if not isinstance(var, (float, int)):
                self.log.error('Given range of parameter is no float or int.')
        gaussian = amplitude*np.exp(-(x_data-x_zero)**2/(2*sigma**2))+offset
        return gaussian
