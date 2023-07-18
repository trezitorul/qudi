# -*- coding: utf-8 -*-
"""
GUI module to test many hardware devices simultaneously.

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

import os
import numpy as np
import time

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class DashboardMainWindow(QtWidgets.QDialog):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_dashboard.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class DashboardGUI(GUIBase):
    """ Hardware testing dashboard main class.
    """
    
    # CONNECTORS #############################################################
    pmlogic = Connector(interface='PowerMeterLogic')
    pidlogic = Connector(interface='SoftPIDController')
    laclogic = Connector(interface='LACLogic')
    aptlogic = Connector(interface='APTpiezoLogic')
    flipperlogic = Connector(interface='FlipperMirrorLogic')
    daqcounter1 = Connector(interface='DaqCounter')
    daqcounter2 = Connector(interface='DaqCounter')
    galvologic = Connector(interface='GalvoLogic')

    # SIGNALS ################################################################
    sigStartGUI = QtCore.Signal()


    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        """ Initialize, connect and configure the relay board GUI.
        """

        # CONNECTORS PART 2 ###################################################
        self._pmlogic = self.pmlogic()
        self._pidlogic = self.pidlogic()
        self._laclogic = self.laclogic()
        self._aptlogic = self.aptlogic()
        self._flipperlogic = self.flipperlogic()
        self._daqcounter1 = self.daqcounter1()
        self._daqcounter2 = self.daqcounter2()
        self._galvologic = self.galvologic()

        self._mw = DashboardMainWindow()
        
        # Plot labels.
        self._pw = self._mw.positionTrace

        self.plot1 = self._pw.plotItem
        self.plot1.setLabel('left', 'Power Output', units='W', color='#00ff00')
        self.plot1.setLabel('bottom', 'Steps passed')

        self.curvearr = []
        ## Create an empty plot curve to be filled later, set its pen
        self.curvearr.append(self.plot1.plot())
        self.curvearr[-1].setPen(palette.c1)

        # Set default parameters
        self.timePass = 0
        self.powerOutputArr = []
        self._mw.StepSize.setValue(10)
        self._mw.k_P.setValue(self._pidlogic.kP)
        self._mw.k_I.setValue(self._pidlogic.kI)
        self._mw.k_D.setValue(self._pidlogic.kD)
        self.stepSize = 10
        self.position = [0, 0, 0]
        self.count1 = 0
        self.count2 = 0
        self.isPID = False

        self._mw.GalvoStepSize.setValue(10)
        self.galvoPosition = [0, 0]
        self.galvoStepSize = 10

        # Connect buttons to functions
        self._mw.upButton.clicked.connect(lambda: self.movePiezo(1,1))
        self._mw.downButton.clicked.connect(lambda: self.movePiezo(1,-1))
        self._mw.leftButton.clicked.connect(lambda: self.movePiezo(0,-1))
        self._mw.rightButton.clicked.connect(lambda: self.movePiezo(0,1))
        self._mw.zUpButton.clicked.connect(lambda: self.movePiezo(2,1))
        self._mw.zDownButton.clicked.connect(lambda: self.movePiezo(2,-1))

        self._mw.galvoUpButton.clicked.connect(lambda: self.moveGalvo(1,1))
        self._mw.galvoDownButton.clicked.connect(lambda: self.moveGalvo(1,-1))
        self._mw.galvoLeftButton.clicked.connect(lambda: self.moveGalvo(0,-1))
        self._mw.galvoDownButton.clicked.connect(lambda: self.moveGalvo(0,1))

        self._mw.startButton.clicked.connect(self.start)
        self._mw.stopButton.clicked.connect(self.stop)
        self._mw.manualButton.clicked.connect(self.manualMode)
        self._mw.PIDbutton.clicked.connect(self.PIDmode)

        self._mw.onButton_1.clicked.connect(lambda: self.flipOn(1))
        self._mw.onButton_2.clicked.connect(lambda: self.flipOn(2))
        self._mw.offButton_1.clicked.connect(lambda: self.flipOff(1))
        self._mw.offButton_2.clicked.connect(lambda: self.flipOff(2))

        # Connect spin boxes
        self._mw.StepSize.valueChanged.connect(self.piezoStepChanged)
        self._mw.GalvoStepSize.valueChanged.connect(self.galvoStepChanged)
        self._mw.powerInput.valueChanged.connect(self.setPowerInput)
        self._mw.posInput.valueChanged.connect(self.setPosInput)

        self._mw.k_P.valueChanged.connect(self.change_kP)
        self._mw.k_I.valueChanged.connect(self.change_kI)
        self._mw.k_D.valueChanged.connect(self.change_kD)

        # Connect signals
        self._pidlogic.sigUpdatePIDDisplay.connect(self.updateDisplay)
        self._pidlogic.sigUpdatePIDDisplay.connect(self.updatePlot)

        self._aptlogic.sigUpdateDisplay.connect(self.updatePiezoDisplay)

        self._daqcounter1.sigUpdateDisplay.connect(self.count)
        self._daqcounter2.sigUpdateDisplay.connect(self.count)
        self._galvologic.sigUpdateDisplay.connect(self.updateGalvoDisplay)

        self._pmlogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        self._pmlogic.sigUpdatePMDisplay.connect(self.updatePlot)

        self._laclogic.sigUpdateLACDisplay.connect(self.updateDisplay)



    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        return 0


    def updateDisplay(self):
        """Updates power output and lav position values.
        """
        if (self.isPID):
            self._mw.powerOutput.setText(str(round(self._pidlogic.pv, 3)))
            self._mw.posOutput.setText(str(round(self._pidlogic.cv, 3)))
        else:
            self._mw.powerOutput.setText(str(round(self._pmlogic.power, 3)))
            self._mw.posOutput.setText(str(round(self._laclogic.position, 3)))


    def updatePlot(self):
        """ The function that grabs the data and sends it to the power output plot.
        """
        if (self.isPID):
            self.timePass += 1
            self.powerOutputArr.append(self._pidlogic.pv)            
            self.curvearr[0].setData(
                y = np.asarray(self.powerOutputArr),
                x = np.arange(0, self.timePass)
                )
        else: 
            self.timePass += 1
            self.powerOutputArr.append(self._pmlogic.power)
            
            self.curvearr[0].setData(
                y = np.asarray(self.powerOutputArr),
                x = np.arange(0, self.timePass)
                )


    def setPowerInput(self):
        """Sets desired power meter value for PID process value using power input spinbox.
        """
        self.powerInput = self._mw.powerInput.value()
        self._pidlogic.set_setpoint(self.powerInput)


    def setPosInput(self):
        """Sets desired LAC position using position input spinbox.
        """
        self.posInput = self._mw.posInput.value()
        self._laclogic.set_pos(self.posInput)


    def PIDmode(self):
        """ Sets LAC control to PID mode (which uses powermeter).
        """
        self._laclogic.stop()
        self.isPID = True

    def manualMode(self):
        """ Sets LAC control to manual mode, allowing a desired position to be set instead of a power level.
        """
        self._pidlogic.sigStopPID.emit()
        self.isPID = False


    def start(self):
        """ Starts logic query loops.
        """
        if self.isPID:
            self._pidlogic.sigStartPID.emit()
        else:
            self._laclogic.start()

        self._pmlogic.start()

    def stop(self):
        """ Stops logic query loops.
        """
        if self.isPID:
            self._pidlogic.sigStopPID.emit()
        else:
            self._laclogic.stop()
        self._pmlogic.stop()

    def movePiezo(self, axis, direction):
        """Move piezo

        @param axis (int): 0->x, 1->y, 2->z
        @param direction (int): Step direction. Defaults to 1.
        """

        position = self.position
        position[axis] = self.position[axis] + self.stepSize * direction

        self._aptlogic.setPosition(position)

    def moveGalvo(self, axis, direction):
        """Move galvo

        @param: axis (int): 0->x, 1->y
        @param: direction (int): Step direction. Defaults to 1.
        """

        galvoPosition = self.galvoPosition
        galvoPosition[axis] = self.galvoPosition[axis] + self.galvoStepSize * direction

        self._galvologic.setPosition(galvoPosition)

    def piezoStepChanged(self):
        """Changes piezo step size using spinbox.
        """
        self.stepSize = self._mw.StepSize.value()

    def galvoStepChanged(self):
        """Changes galvo step size using spinbox.
        """
        self.galvoStepSize = self._mw.GalvoStepSize.value()

    def updatePiezoDisplay(self):
        """Updates piezo display with x, y, and z axis positions.
        """
        self.position = self._aptlogic.position
        self._mw.xVal.setText(str(self.position[0]))
        self._mw.yVal.setText(str(self.position[1]))
        self._mw.zVal.setText(str(self.position[2]))

    def updateGalvoDisplay(self):
        """Updates galvo display with x and y axis positions.
        """
        self.galvoPosition = self._galvologic.position
        self._mw.galvoXVal.setText(str(round(self.galvoPosition[0],3)))
        self._mw.galvoYVal.setText(str(round(self.galvoPosition[1],3)))
    
    def change_kP(self):
        """Change kP for PID loop using spinbox.
        """
        kp = self._mw.k_P.value()
        self._pidlogic.set_kp(kp)

    def change_kI(self):
        """Change kI for PID loop using spinbox.
        """
        ki = self._mw.k_I.value()
        self._pidlogic.set_ki(ki)

    def change_kD(self):
        """Change kD for PID loop using spinbox.
        """
        kd = self._mw.k_D.value()
        self._pidlogic.set_kd(kd)

    def flipOn(self, num):
        """Flips on one flipper mirror.
        @param (int) num: specifies which flipper mirror to turn on.
        """
        self._flipperlogic.set_mode('on', num)

    def flipOff(self, num):
        """Flips off one flipper mirror.
        @param (int) num: specifies which flipper mirror to turn off.
        """
        self._flipperlogic.set_mode('off', num)

    def count(self):
        """Updates daq display with counts.
        """
        self.count1 = self._daqcounter1.counts
        self.count2 = self._daqcounter2.counts
        self._mw.daq_channel1.setText(str(self.count1))
        self._mw.daq_channel2.setText(str(self.count2))