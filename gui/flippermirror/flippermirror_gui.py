import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class FlipperMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_flippermirror_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class FlipperGUI(GUIBase):
    """
    Flipper mirror gui.
    """

    #Connector
    flipperlogic = Connector(interface='FlipperMirrorLogic')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        self._flipperlogic = self.flipperlogic()

        self._mw = FlipperMainWindow()

        self._mw.onButton_1.clicked.connect(lambda: self.flipOn(1))
        self._mw.onButton_2.clicked.connect(lambda: self.flipOn(2))
        self._mw.offButton_1.clicked.connect(lambda: self.flipOff(1))
        self._mw.offButton_2.clicked.connect(lambda: self.flipOff(2))

        self.show()

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()

    def flipOn(self, num):
        self._flipperlogic.set_mode('on', num)
        # pass

    def flipOff(self, num):
        self._flipperlogic.set_mode('off', num)
        # pass

    def show(self):
        """Make main window visible and put it above all other windows. """
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()