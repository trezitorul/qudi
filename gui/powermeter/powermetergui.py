import os
import numpy as np

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
    sigStopPM = QtCore.Signal()
   

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
        
        # Plot labels.
        self._pw = self._mw.positionTrace

        self.plot1 = self._pw.plotItem
        self.plot1.setLabel('left', 'Power Output', units='W', color='#00ff00')
        self.plot1.setLabel('bottom', 'Steps passed')

        self.curvearr = []
        ## Create an empty plot curve to be filled later, set its pen
        self.curvearr.append(self.plot1.plot())
        self.curvearr[-1].setPen(palette.c1)

        self.timePass = 0
        self.powerOutputArr = []
        # Set default parameters

        # Connect buttons to functions
        self._mw.startButton.clicked.connect(self.startGUI) #could also connect directly to logic
        self._mw.stopButton.clicked.connect(self.stopGUI)

        # Connect signals
        self._pmlogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        self._pmlogic.sigUpdatePMDisplay.connect(self.updatePlot)

        self.sigStartPM.connect(self._pmlogic.start_query_loop)
        self.sigStopPM.connect(self._pmlogic.stop_query_loop)


    def updateDisplay(self):
        self._mw.powerOutput.setText(str(round(self._pmlogic.power, 3)))


    def updatePlot(self):
        """ The function that grabs the data and sends it to the plot.
        """
        self.timePass += 1
        self.powerOutputArr.append(self._pmlogic.power)
        
        self.curvearr[0].setData(
            y = np.asarray(self.powerOutputArr),
            x = np.arange(0, self.timePass)
            )

    def startGUI(self):
        self.sigStartPM.emit()

    def stopGUI(self):
        self.sigStopPM.emit()
