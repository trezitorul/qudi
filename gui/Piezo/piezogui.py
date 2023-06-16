import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class PiezoMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_APTpiezo_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class PiezoGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    # voltagescannerlogic1 = Connector(interface='LaserScannerLogic')
    # savelogic = Connector(interface='SaveLogic')

    # SIGNALS ################################################################
    # sigStartScan = QtCore.Signal()
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
        # self._voltscan_logic = self.voltagescannerlogic1()
        # self._savelogic = self.savelogic()


        self._mw = PiezoMainWindow()

        # Set default parameters
        self._mw.StepSize.setValue(10)

        # Connect buttons to functions
        self._mw.StepSize.valueChanged.connect(self.stepChanged)
        self._mw.upButton.clicked.connect(lambda: self.move("up"))
        self._mw.downButton.clicked.connect(lambda: self.move("down"))
        self._mw.leftButton.clicked.connect(lambda: self.move("left"))
        self._mw.rightButton.clicked.connect(lambda: self.move("right"))
        self._mw.zUpButton.clicked.connect(lambda: self.move("zUp"))
        self._mw.zDownButton.clicked.connect(lambda: self.move("zDown"))
        self._mw.zDownButton.clicked.connect(self.updateDisplay) # this was just to make sure the update worked
    
    def move(self, name):
        print(name)
    
    def stepChanged(self):
        # Must edit for correct connector
        self._pid_logic.set_kp(self._mw.P_DoubleSpinBox.value())

    def updateDisplay(self):
        self._mw.xVal.setText("yuh")
        
    