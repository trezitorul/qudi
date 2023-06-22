import os
import numpy as np

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class PowerMeterMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_powermeterui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class PowerMeterGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    #pmlogic = Connector(interface='PowerMeterLogic')
    pidlogic = Connector(interface='SoftPIDController')

    # SIGNALS ################################################################
    sigStartPM = QtCore.Signal()
    # sigStopScan = QtCore.Signal()
    # sigChangeVoltage = QtCore.Signal(float)
    # sigChangeRange = QtCore.Signal(list)
    # sigChangeResolution = QtCore.Signal(float)
    # sigChangeSpeed = QtCore.Signal(float)
    # sigChangeLines = QtCore.Signal(int)
    # sigSaveMeasurement = QtCore.Signal(str, list, list)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        #return 0

    def on_activate(self):
        """ 

        """

        # CONNECTORS PART 2 ###################################################
        #self._pmlogic = self.pmlogic()
        self._pidlogic = self.pidlogic()

        self._mw = PowerMeterMainWindow()
        
        # Plot labels.
        self._pw = self._mw.positionTrace

        self.plot1 = self._pw.plotItem
        self.plot1.setLabel('left', 'Power Output', units='W', color='#00ff00')
        self.plot1.setLabel('bottom', 'Step passed')

        self.curvearr = []
        ## Create an empty plot curve to be filled later, set its pen
        self.curvearr.append(self.plot1.plot())
        self.curvearr[-1].setPen(palette.c1)

        self.timePass = 0
        self.powerOutputArr = []
        # Set default parameters

        # Connect buttons to functions
        self._mw.startButton.clicked.connect(self.startGUI) #could also connect directly to logic
        
        # Connect spin box
        self._mw.powerInput.valueChanged.connect(self.setPowerInput)
        
        # Connect signals
        self._pidlogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        self._pidlogic.sigUpdatePMDisplay.connect(self.updateData)
        #self.sigStartPM.connect(self._pmlogic.start_query_loop)
        self.sigStartPM.connect(self._pidlogic.startFunc)


    def updateDisplay(self):
        self._mw.powerOutput.setText(str(self._pidlogic.pv))


    def updateData(self):
        """ The function that grabs the data and sends it to the plot.
        """
        self.timePass += 1
        self.powerOutputArr.append(self._pidlogic.pv)
        
        self.curvearr[0].setData(
            y = np.asarray(self.powerOutputArr),
            x = np.arange(0, self.timePass)
            )


    def setPowerInput(self):
        self.powerInput = self._mw.powerInput.value()
        self._pidlogic.set_setpoint(self.powerInput)


    def startGUI(self):
        self.sigStartPM.emit()
