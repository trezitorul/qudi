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
    # aptlogic = Connector(interface='APTpiezoLogic')

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
        self.position = [0, 0, 0]

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
        # self._aptlogic = self.aptlogic()

        self._mw = PiezoMainWindow()

        # Set default parameters
        self._mw.StepSize.setValue(10)

        # Connect buttons to functions
        self._mw.upButton.clicked.connect(lambda: self.move(1, 1))
        self._mw.downButton.clicked.connect(lambda: self.move(1, -1))
        self._mw.leftButton.clicked.connect(lambda: self.move(0, -1))
        self._mw.rightButton.clicked.connect(lambda: self.move(0, 1))
        self._mw.zUpButton.clicked.connect(lambda: self.move(2, 1))
        self._mw.zDownButton.clicked.connect(lambda: self.move(2, -1))
    
    def move(self, direction, stepSize=1):
        """Move piezo

        Args:
            direction (int): 0->x, 1->y, 2->z
            stepSize (int, optional): Step size. Defaults to 1.
        """
        self.position[direction] += stepSize
        self._mw.xVal.setText(str(self.position[0]))
        self._mw.yVal.setText(str(self.position[1]))
        self._mw.zVal.setText(str(self.position[2]))
        # print(self.position)
        