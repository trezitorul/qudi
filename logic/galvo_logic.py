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

    # Connect signals

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


    def on_deactivate(self):
        """ Deactivate modeule.
        """
        pass

    def setPosition(self, position):

        self.setX(position[0])
        self.setY(position[1])

    def getPosition(self):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.
        Units: microns

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        position = [self.getX(), self.getY()]
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