import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class DAQCounterMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_daqcounter_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class DAQCounterGUI(GUIBase):
    """
    DAQ Counter gui.
    """

    #Connector
    daqcounter1 = Connector(interface='DaqCounter')
    daqcounter2 = Connector(interface='DaqCounter')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        self._daqcounter1 = self.daqcounter1()
        self._daqcounter2 = self.daqcounter2()

        self._mw = DAQCounterMainWindow()

        self._daqcounter1.sigUpdateDisplay.connect(self.count)
        self._daqcounter1.sigUpdateDisplay.connect(self.count)

        # Set default parameters
        self.count1 = 0
        self.count2 = 0

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        #return 0

    def count(self):
        self.count1 = self._daqcounter1.counts
        self.count2 = self._daqcounter2.counts
        self._mw.daq_channel1.setText(str(self.count1))
        self._mw.daq_channel2.setText(str(self.count2))