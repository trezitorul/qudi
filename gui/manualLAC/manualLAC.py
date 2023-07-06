import os
import numpy as np

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class ManualLACMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_manualLAC.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class ManualLACGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    laclogic = Connector(interface='LACLogic')

    # SIGNALS ################################################################
   

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        #return 0

    def on_activate(self): #output pos, input pos, start, stop
        """ 

        """

        # CONNECTORS PART 2 ###################################################
        self._laclogic = self.laclogic()

        self._mw = ManualLACMainWindow()

        # Buttons and spinboxes
        self._mw.startButton.clicked.connect(self.start)
        self._mw.stopButton.clicked.connect(self.stop)
        self._mw.posInput.valueChanged.connect(self.setPosInput)

        # Connect signals

        self._laclogic.sigUpdateLACDisplay.connect(self.updateDisplay)
        
    def updateDisplay(self):
        self._mw.posOutput.setText(str(round(self._laclogic.position, 3)))

    def setPosInput(self):
        self.posInput = self._mw.posInput.value()
        self._laclogic.set_pos(self.posInput)

    def start(self):
        self._laclogic.start()

    def stop(self):
        self._laclogic.stop()