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

class LACPIDMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_LAC_PID_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class LACPIDGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    pmlogic = Connector(interface='PowerMeterLogic')
    pidlogic = Connector(interface='SoftPIDController')
    laclogic = Connector(interface='LACLogic')
    # querylogic = Connector(interface='QueryLoopLogic')

    # SIGNALS ################################################################
    sigStartGUI = QtCore.Signal()


    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        # CONNECTORS PART 2 ###################################################
        self._pmlogic = self.pmlogic()
        self._pidlogic = self.pidlogic()
        self._laclogic = self.laclogic()
        # self._querylogic = self.querylogic()

        self._mw = LACPIDMainWindow()
        
        # Set default parameters
        self._mw.k_P.setValue(self._pidlogic.kP)
        self._mw.k_I.setValue(self._pidlogic.kI)
        self._mw.k_D.setValue(self._pidlogic.kD)

        # Connect buttons to functions
        self._mw.startButton.clicked.connect(self.start)
        self._mw.stopButton.clicked.connect(self.stop)

        # Connect spin boxes
        self._mw.powerInput.valueChanged.connect(self.setPowerInput)

        self._mw.k_P.valueChanged.connect(self.change_kP)
        self._mw.k_I.valueChanged.connect(self.change_kI)
        self._mw.k_D.valueChanged.connect(self.change_kD)

        # Connect signals
        self._pidlogic.sigUpdatePIDDisplay.connect(self.updateDisplay)
        # self._pidlogic.sigUpdatePIDDisplay.connect(self.updatePlot)

        # self._querylogic.sigUpdateVariable.connect(self.updateDisplay)
        # self._querylogic.sigUpdateVariable.connect(self.updatePlot)

        self._laclogic.sigUpdateLACDisplay.connect(self.updateDisplay)



    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        #return 0


    def updateDisplay(self):
        # self._mw.powerOutput.setText(str(round(self._pidlogic.pv, 3)))
        self._mw.posOutput.setText(str(round(self._pidlogic.cv, 3)))


    def setPowerInput(self):
        self.powerInput = self._mw.powerInput.value()
        self._pidlogic.set_setpoint(self.powerInput)


    def start(self):
        self._pidlogic.sigStartPID.emit()

        self._pmlogic.start()


    def stop(self):
        self._pidlogic.sigStopPID.emit()
        self._pmlogic.stop()


    def change_kP(self):
        kp = self._mw.k_P.value()
        self._pidlogic.set_kp(kp)


    def change_kI(self):
        ki = self._mw.k_I.value()
        self._pidlogic.set_ki(ki)


    def change_kD(self):
        kd = self._mw.k_D.value()
        self._pidlogic.set_kd(kd)
