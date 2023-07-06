import os
import numpy as np

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

        self._daqcounter1.sigUpdateDisplay.connect(self.updatePlot)
        self._daqcounter2.sigUpdateDisplay.connect(self.updatePlot)

        self.timePass = 0
        # Plot labels for 1st channel.
        self._pw = self._mw.countTrace1

        self.plot1 = self._pw.plotItem
        self.plot1.setLabel('left', 'Power Output', units='W', color='#00ff00')
        self.plot1.setLabel('bottom', 'Steps passed')

        self.curvearr1 = []
        ## Create an empty plot curve to be filled later, set its pen
        self.curvearr1.append(self.plot1.plot())
        self.curvearr1[-1].setPen(palette.c1)

        self.countArr1 = []

        # Plot labels for 2nd channel
        self._pw = self._mw.countTrace2

        self.plot2 = self._pw.plotItem
        self.plot2.setLabel('left', 'Power Output', units='W', color='#00ff00')
        self.plot2.setLabel('bottom', 'Steps passed')

        self.curvearr2 = []
        ## Create an empty plot curve to be filled later, set its pen
        self.curvearr2.append(self.plot2.plot())
        self.curvearr2[-1].setPen(palette.c2)

        self.countArr2 = []

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


    def updatePlot(self):
        """ The function that grabs the data and sends it to the plot.
        """
        self.timePass += 1
        self.countArr1.append(self._daqcounter1.counts)
        self.countArr2.append(self._daqcounter2.counts)
        
        if (self.timePass < 300):
            self.curvearr1[0].setData(
                y = np.asarray(self.countArr1),
                x = np.arange(0, self.timePass)
                )
            self.curvearr2[0].setData(
                y = np.asarray(self.countArr2),
                x = np.arange(0, self.timePass)
                )
        else:
            self.curvearr1[0].setData(
                y = np.asarray(self.countArr1[self.timePass - 300:self.timePass]),
                x = np.arange(self.timePass - 300, self.timePass)
                )
            self.curvearr2[0].setData(
                y = np.asarray(self.countArr2[self.timePass - 300:self.timePass]),
                x = np.arange(self.timePass - 300, self.timePass)
                )

