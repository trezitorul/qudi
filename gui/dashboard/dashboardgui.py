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
    """

    """
    
    # CONNECTORS #############################################################
    pmlogic = Connector(interface='PowerMeterLogic')
    pidlogic = Connector(interface='SoftPIDController')
    laclogic = Connector(interface='LACLogic')
    querylogic = Connector(interface='QueryLoopLogic')
    aptlogic = Connector(interface='APTpiezoLogic')

    # SIGNALS ################################################################
    sigStartGUI = QtCore.Signal()


    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        # CONNECTORS PART 2 ###################################################
        self._pmlogic = self.pmlogic()
        self._pidlogic = self.pidlogic()
        self._laclogic = self.laclogic()
        self._querylogic = self.querylogic()
        self._aptlogic = self.aptlogic()

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
        self.stepSize = 10
        self.position = [0, 0, 0]

        # Connect buttons to functions
        self._mw.StepSize.valueChanged.connect(self.stepChanged)
        self._mw.upButton.clicked.connect(lambda: self.move(1,1))
        self._mw.downButton.clicked.connect(lambda: self.move(1,-1))
        self._mw.leftButton.clicked.connect(lambda: self.move(0,-1))
        self._mw.rightButton.clicked.connect(lambda: self.move(0,1))
        self._mw.zUpButton.clicked.connect(lambda: self.move(2,1))
        self._mw.zDownButton.clicked.connect(lambda: self.move(2,-1))
        self._mw.startButton.clicked.connect(self.emitStartPID) #could also connect directly to logic
        self._mw.stopButton.clicked.connect(self.emitStopPID)
        self._mw.manualButton.clicked.connect(self.startManual)
        self._mw.PIDbutton.clicked.connect(self.startPID)

        # Connect spin box
        self._mw.powerInput.valueChanged.connect(self.setPowerInput)
        self._mw.posInput.valueChanged.connect(self.setPosInput)

        # Connect signals
        # self._pidlogic.sigUpdatePIDDisplay.connect(self.updateDisplay)
        # self._pidlogic.sigUpdatePIDDisplay.connect(self.updatePlot)

        self._querylogic.sigUpdateVariable.connect(self.updateDisplay)
        self._querylogic.sigUpdateVariable.connect(self.updatePlot)
        self._aptlogic.sigUpdateDisplay.connect(self.updatePiezoDisplay) #maybe change name in aptlogic too

        # self._pmlogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        # self._pmlogic.sigUpdatePMDisplay.connect(self.updatePlot)

        # self._laclogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        # self.sigStartPM.connect(self._pidlogic.startPID)


    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        #return 0


    def updateDisplay(self, is_PID):
        if (is_PID):
            self._mw.powerOutput.setText(str(round(self._pidlogic.pv, 3)))
            self._mw.posOutput.setText(str(round(self._pidlogic.cv, 3)))
        else:
            self._mw.powerOutput.setText(str(round(self._pmlogic.power, 3)))
            self._mw.posOutput.setText(str(round(self._laclogic.position, 3)))


    def updatePlot(self, is_PID):
        """ The function that grabs the data and sends it to the plot.
        """
        if (is_PID):
            self.timePass += 1
            self.powerOutputArr.append(self._pidlogic.pv)
            # self.powerOutputArr.append(self._pmlogic.power)
            
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
        self.powerInput = self._mw.powerInput.value()
        self._pidlogic.set_setpoint(self.powerInput)


    def setPosInput(self):

        self.posInput = self._mw.posInput.value()
        self._laclogic.set_pos(self.posInput)
        return


    def startPID(self):
        # self._querylogic.stop_query_loop()
        self._querylogic.sigStopQuery.emit()
        # time.sleep(3)
        # self.sigStartPM.emit()
        self._mw.startButton.setEnabled(True)
        self._mw.stopButton.setEnabled(True)
        # self._mw.startButton.clicked.connect(self.emitStartPID) #could also connect directly to logic
        # self._mw.stopButton.clicked.connect(self.emitStopPID)
        self._pidlogic.sigUpdatePIDDisplay.connect(self.updateDisplay)
        self._pidlogic.sigUpdatePIDDisplay.connect(self.updatePlot)
        # self._pidlogic.startFunc()
        # self._laclogic.stop_query_loop()
        # self._pmlogic.stop_query_loop()


    def emitStartPID(self):
        self._pidlogic.sigStartPID.emit()


    def emitStopPID(self):
        self._pidlogic.sigStopPID.emit()


    def startManual(self):
        self._pidlogic.sigStopPID.emit()
        # time.sleep(3)
        # Start loop
        # self._querylogic.start_query_loop()
        self._querylogic.sigStartQuery.emit()

        # Disable buttons
        self._mw.startButton.setEnabled(False)
        self._mw.stopButton.setEnabled(False)

        self._mw.posInput.valueChanged.connect(self.setPosInput)

    def move(self, axis, direction):
        """Move piezo

        Args:
            axis (int): 0->x, 1->y, 2->z
            direction (int, optional): Step direction. Defaults to 1.
        """

        position = self.position
        position[axis] = self.position[axis] + self.stepSize * direction

    def stepChanged(self):
        self.stepSize = self._mw.StepSize.value()

    def updatePiezoDisplay(self):
        self.position = self._aptlogic.position
        self._mw.xVal.setText(str(self.position[0]))
        self._mw.yVal.setText(str(self.position[1]))
        self._mw.zVal.setText(str(self.position[2]))