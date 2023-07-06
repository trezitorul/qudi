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

class PolarMotorMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_polarization_motor.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class PolarMotordGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    polarlogic = Connector(interface='PolarMotorLogic')

    # SIGNALS ################################################################
    sigStartGUI = QtCore.Signal()


    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        # CONNECTORS PART 2 ###################################################
        self._polarlogic = self.polarlogic()

        self._mw = PolarMotorMainWindow()
        
        # Set default parameters


        # Connect spin boxes
        self._mw.inputDegree.valueChanged.connect(self.updatePosition)
        self._mw.moveButton.clicked.connect(self.setPosInput)

        # Connect signals
        self._polarlogic.sigUpdatePolarMotorDisplay.connect(self.updateDisplay)


    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()

    def updatePosition(self):
        self.posInput = self._mw.inputDegree.value()


    def setPosInput(self):
        self._polarlogic.set_position(self.posInput)


    def updateDisplay(self):
        self._mw.currDegree.setText(str(self._polarlogic.position))
