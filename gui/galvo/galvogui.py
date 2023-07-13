import os
import time

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class GalvoMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_galvogui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class GalvoGUI(GUIBase):
    """
    Galvo gui.
    """

    #Connector
    galvologic = Connector(interface='GalvoLogic')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        self._galvologic = self.galvologic()

        self._mw = GalvoMainWindow()

        # Set default parameters
        self._mw.GalvoStepSize.setValue(10)
        self.galvoPosition = [0, 0]
        self._mw.posButton.setChecked(True)
        self.galvoStepSize = 10
        self.isPosMode = True

        # Units
        self.m=1
        self.um=self.m*1e-6

        # Connect buttons to functions
        self._mw.galvoUpButton.clicked.connect(lambda: self.moveGalvo(1,1))
        self._mw.galvoDownButton.clicked.connect(lambda: self.moveGalvo(1,-1))
        self._mw.galvoLeftButton.clicked.connect(lambda: self.moveGalvo(0,-1))
        self._mw.galvoRightButton.clicked.connect(lambda: self.moveGalvo(0,1))
        self._mw.posButton.clicked.connect(self.setPosMode)
        self._mw.voltButton.clicked.connect(self.setVoltMode)
        self._mw.moveButton.clicked.connect(self.manualMove)

        # Connect spinbox
        self._mw.GalvoStepSize.valueChanged.connect(self.galvoStepChanged)

        # Connect signals
        self._galvologic.sigUpdateDisplay.connect(self.updateGalvoDisplay)

        self.show()

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        
    def moveGalvo(self, axis, direction):
        """Move galvo

        Args:
            axis (int): 0->x, 1->y
            direction (int, optional): Step direction. Defaults to 1.
        """
        if self.isPosMode:
            self._galvologic.moveGalvoPos(axis, direction, self.galvoStepSize)
        else:
            self._galvologic.moveGalvoVolt(axis, direction, self.galvoStepSize)

    def manualMove(self):
        position = [self._mw.xInput.value(), self._mw.yInput.value()]

        if (self.isPosMode):
            self._galvologic.setPosition(position)
        else:
            # self._galvologic.setDiffVoltage(0,1,position[0])
            # self._galvologic.setDiffVoltage(2,3,position[1])
            self._galvologic.setVoltageScaled(position)

    def galvoStepChanged(self):
        self.galvoStepSize = self._mw.GalvoStepSize.value()

    def updateGalvoDisplay(self):
        self.galvoPosition = self._galvologic.position
        self.diffvolt = self._galvologic.diffvolt
        self._mw.galvoXVal.setText(str(round(self.galvoPosition[0]/self.um,3)))
        self._mw.galvoYVal.setText(str(round(self.galvoPosition[1]/self.um,3)))
        self._mw.galvoXVolt.setText(str(round(self.diffvolt[0],3)))
        self._mw.galvoYVolt.setText(str(round(self.diffvolt[1],3)))

    def setPosMode(self):
        self.isPosMode = True

    def setVoltMode(self):
        self.isPosMode = False

    def show(self):
        """Make main window visible and put it above all other windows. """
        # Show the Main GUI:
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()