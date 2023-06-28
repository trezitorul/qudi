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
    
    # signals
    sigUpdateDisplay = QtCore.Signal()

    # Connect signals

    def on_activate(self):
        """ Prepare logic module for work.
        """

        self._daq = self.daq()

        self.um=1
        self.nm=(self.um/1000)
        self.board_num = 0
        self.range = self._daq._range
        self.LUT = []
        self.mode = self._daq._mode
        self.setMode(self.mode)
        self.counterchannel = 0 #detecting either there is single photon (1) or not(0)
        self.thetaHigh=0
        self.thetaLow=1
        self.phiHigh=2
        self.phiLow=3
        self.VToA=10 #Volts per Optical Scan Angle (1/2 * 0.5 V per Mechanical Angle, Optical Scan Angle is 2X Mechanical Scan Angle)
        self.projectionDistance=10.63*self.um #1/tan(31) used for development only, corresponds to max displacement of the X axis at theta=31 degrees. Units can be chosen arbitrarily for now as um=1

        self.vArray = []
        self.outVal=0
        self.s=1
        self.ms=0.001
        self.hz=1
        self.f=1*self.hz 
        self.p=1/self.f
        self.ns=1e-9*self.s
        self.tArray=[]
        self.channel_X_high = [0,0] #[out channel, in channel]
        self.channel_X_low = [1,1]
        self.channel_Y_high = [2,2]
        self.channel_Y_low = [3,3]
        self.t = 0
        self.vArrayX =[]
        self.vArrayY = []
        self.vArrayX1 =[]
        self.vArrayY1 = []
        self.cArrayX=[]
        self.cArrayY=[]
        self.cArrayX1=[]
        self.cArrayY1=[]
        self.A=5# Volts


    def on_deactivate(self):
        """ Deactivate modeule.
        """
        pass

    
    def recordData(self):
        self._daq.setMode("differential")
        t=0
        for i in range(int(1e3)):
            tstart=time.perf_counter()

            self.tArray.append(t)
            voltageX = self.A * np.sin(((2*np.pi)/self.p)*t)
            voltageY = self.A * np.sin(((2*np.pi)/self.p)*t + np.pi/2)
            self.setDiffVoltage(self.channel_Y_high[0], self.channel_Y_low[0], voltageY)
            self.setDiffVoltage(self.channel_X_high[0], self.channel_X_low[0], voltageX)
            voltage_outY = self.getDiffVoltage(self.channel_Y_high[1], self.channel_Y_low[1])
            voltage_outX = self.getDiffVoltage(self.channel_X_high[1], self.channel_X_low[1])

            self.updateData(voltageX, voltageY, voltage_outX, voltage_outY)
            
            t = (time.perf_counter() - tstart) + t
        plt.plot(self.tArray, self.vArrayX, marker='+',c ='b', label="X")
        plt.plot(self.tArray, self.vArrayY, marker ='+',c ='r', label="Y")
        plt.plot(self.tArray, self.cArrayX,c ='b')
        plt.plot(self.tArray, self.cArrayY,c ='r')
        plt.legend()
        plt.show()
        # self._daq.setZero()



    def updateData(self, voltageX, voltageY, voltage_outX, voltage_outY):
        self.cArrayX.append(voltageX)
        self.cArrayY.append(voltageY)
        self.vArrayX.append(voltage_outX)
        self.vArrayY.append(voltage_outY)
        self.sigUpdateDisplay.emit()
    
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


    def getCounts(self,dt):
        '''
        Implementing electrical pulse countings on the Daq cards
        '''
        return self._daq.getCounts(dt)


    def rasterscan(self,intergration_t,dx,dy,n,spanx,spany, setx, sety):
        data1 = 0
        counts = []
        if (float(dx) < 1):
            num_points_row =  int(int(spanx) // float(dx)) + 2
        else:
            num_points_row = int(spanx) // float(dx) + 1

        y = int(sety) + int(spany) / 2 - float(dy) * (int(n) // num_points_row)

        if (n==0):
            x = int(setx) + int(spanx) * (-1) / 2

        #even row (x traverse right)
        elif ((int(n) // num_points_row) % 2 == 0):
            x = int(setx) + int(spanx) * (-1) / 2 + (int(n) % num_points_row) * float(dx)

        #odd row
        else:
            x = int(setx) + int(spanx) / 2 - ((int(n)) % num_points_row) * float(dx)

        if x>=-5 and x<=5 and y >=-5 and y<=5:
            if y >= (int(sety) - int(spany)/ 2):
                self.setX(x)
                self.setY(y)
                x=self.getX()
                y=self.getY()
                c=self.getCounts(intergration_t)
            else:
                return -1000, -1000, -1000
        return x, y, c