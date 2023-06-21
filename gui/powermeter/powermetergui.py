import os

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
    pmlogic = Connector(interface='PowerMeterLogic')

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
        self._pmlogic = self.pmlogic()

        self._mw = PowerMeterMainWindow()

        # Set default parameters

        # Connect buttons to functions
        self._mw.startButton.clicked.connect(self.startGUI) #could also connect directly to logic

        # Connect signals
        self._pmlogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        self.sigStartPM.connect(self._pmlogic.start_query_loop)

    def updateDisplay(self):
        self._mw.powerOutput.setText(str(self._pmlogic.power))

        return
    
    def startGUI(self):
        self.sigStartPM.emit()