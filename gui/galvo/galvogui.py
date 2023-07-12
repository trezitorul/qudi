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
        self._mw.GalvoStepSize.setValue(1)
        self.galvoPosition = [0, 0]

        # Connect buttons to functions
        self._mw.galvoUpButton.clicked.connect(lambda: self.moveGalvo(1,1))
        self._mw.galvoDownButton.clicked.connect(lambda: self.moveGalvo(1,-1))
        self._mw.galvoLeftButton.clicked.connect(lambda: self.moveGalvo(0,-1))
        self._mw.galvoRightButton.clicked.connect(lambda: self.moveGalvo(0,1))

        # Connect spinbox
        self._mw.GalvoStepSize.valueChanged.connect(self.galvoStepChanged)

        # Connect signals
        self._galvologic.sigUpdateDisplay.connect(self.updateGalvoDisplay)

        self.setScale()

        self.galvoStepSize = self.scaleX

        self.show()

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()

    def setScale(self):
        self._galvologic.setPosition([1,1])
        time.sleep(.1)
        voltage = self._galvologic.getPosition()
        self.scaleX = 1 / voltage[0]
        self.scaleY = 1 / voltage[1]
        print("X")
        print(self.scaleX)
        print("Y")
        print(self.scaleY)
        self._galvologic.setPosition([0,0])

        
    def moveGalvo(self, axis, direction):
        """Move galvo

        Args:
            axis (int): 0->x, 1->y
            direction (int, optional): Step direction. Defaults to 1.
        """
        galvoPosition = self._galvologic.position
        galvoPosition = [galvoPosition[0]*self.scaleX, galvoPosition[1]*self.scaleY]
        print("CURRENT POSITION")
        print(galvoPosition)
        print("REQUESTED POSITION")

        galvoPosition[axis] = galvoPosition[axis] + self.galvoStepSize * direction
        print(galvoPosition)
        self._galvologic.setPosition(galvoPosition)

    def galvoStepChanged(self):
        self.galvoStepSize = self._mw.GalvoStepSize.value()*self.scaleX

    def updateGalvoDisplay(self):
        self.galvoPosition = self._galvologic.position
        self._mw.galvoXVal.setText(str(round(self.galvoPosition[0],3)))
        self._mw.galvoYVal.setText(str(round(self.galvoPosition[1],3)))

    def show(self):
        """Make main window visible and put it above all other windows. """
        # Show the Main GUI:
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()