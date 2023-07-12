import numpy as np
import time
import matplotlib.pyplot as plt
import math

from core.configoption import ConfigOption
from core.connector import Connector
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class GalvoLogic(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """

    daq = Connector(interface='DAQ')
    queryInterval = ConfigOption('query_interval', 100)

    position = [0,0]


    # Connect signals
    sigUpdateDisplay = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """

        self._daq = self.daq()

        self.um=1
        self.nm=(self.um/1000)
        
        self.thetaHigh=0
        self.thetaLow=1
        self.phiHigh=2
        self.phiLow=3
        self.VToA=10 #Volts per Optical Scan Angle (1/2 * 0.5 V per Mechanical Angle, Optical Scan Angle is 2X Mechanical Scan Angle)
        self.projectionDistance=10.63*self.um #1/tan(31) used for development only, corresponds to max displacement of the X axis at theta=31 degrees. Units can be chosen arbitrarily for now as um=1

        self.stopRequest = False
        self.bufferLength = 100

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
            self.log.exception("Exception in galvo status loop, throttling refresh rate.")

        self.queryTimer.start(qi)
        self.sigUpdateDisplay.emit()

    def setPosition(self, voltage):

        # self.setX(position[0])
        # self.setY(position[1])
        self.setDiffVoltage(0,1,voltage[0])
        self.setDiffVoltage(2,3,voltage[1])

    def getPosition(self):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.
        Units: microns

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        position = [self.getDiffVoltage(0,1), self.getDiffVoltage(2,3)]
        return position
    
    def setMode(self,mode):
        '''
        Set the DAQ card to either "differential" or "single_ended"
        '''

        self._daq.setMode(mode)

    def getVoltage(self,channel_in):
        '''
        Return analog input channel's voltage
        '''
        return self._daq.getVoltage(channel_in)
    
    def setVoltage(self,channel_out,voltage):
        '''
        Set the analog output channel's voltage
        '''
        self._daq.setVoltage(channel_out,voltage)

    def setDiffVoltage(self,channel_high, channel_low,voltage):
        '''
        Set the analog output differential voltage between 2 channel
        '''
        self._daq.setDiffVoltage(channel_high, channel_low,voltage)

    def getDiffVoltage(self,channel_high,channel_low):
        '''
        Return differential voltage between 2 channels
        '''
        return self._daq.getDiffVoltage(channel_high,channel_low)
    
    def setThetaAngle(self, theta):
        '''
        Set optical angle in respect to X axis
        '''
        V_theta=self.VToA*theta
        self.setDiffVoltage(self.thetaHigh,self.thetaLow, V_theta)
        return 

    def setPhiAngle(self, phi):
        '''
        Set optical angle in respect to Y axis
        '''
        V_phi=self.VToA*phi
        self.setDiffVoltage(self.phiHigh,self.phiLow, V_phi)
        return 

    def setX(self, X):
        '''
        Set horizontal positon of laser
        '''
        theta=math.degrees(np.arctan(X/self.projectionDistance))
        self.setThetaAngle(theta)
        return

    def setY(self, Y):
        '''
        Set vertical position of laser
        '''
        phi=math.degrees(np.arctan(Y/self.projectionDistance))
        self.setPhiAngle(phi)
        return


    def getThetaAngle(self):
        '''
        Return optical angle in respect to X axis
        '''
        Xvolt = self.getDiffVoltage(self.thetaHigh,self.thetaLow)
        theta = Xvolt / self.VToA
        return theta


    def getX(self):
        '''
        Return horizontal positon of laser
        '''
        theta = self.getThetaAngle()
        X_position = math.tan(math.radians(theta)) * self.projectionDistance
        return X_position


    def getPhiAngle(self):
        '''
        Return optical angle in respect to Y axis
        '''
        Yvolt = self.getDiffVoltage(self.phiHigh,self.phiLow)
        phi = Yvolt / self.VToA
        return phi


    def getY(self):
        '''
        Return vertical position of laser
        '''
        phi = self.getPhiAngle()
        Y_position = math.tan(math.radians(phi)) * self.projectionDistance
        return Y_position


    def setZero(self):
        '''
        Reset Galvo config
        '''
        self._daq.setZero()

    def get_position_range(self): ###################### F I X ##################################################
        return [[-10,10], [-10,10]]