import os
import time

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
import pyqtgraph as pg
import numpy as np
from gui.colordefs import QudiPalettePale as palette

class TimeAxisItem(pg.AxisItem):
    """ pyqtgraph AxisItem that shows a HH:MM:SS timestamp on ticks.
        X-Axis must be formatted as (floating point) Unix time.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        """ Hours:Minutes:Seconds string from float unix timestamp. """
        return [time.strftime("%H:%M:%S", time.localtime(value)) for value in values]


class LtuneLaserMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_ltune_laser.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class LtuneLaserGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    ltunelaserlogic = Connector(interface='LtuneLaserLogic')

    # SIGNALS ################################################################
    enabled = False

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._ltunelaserlogic.disable_laser()
        self._mw.close()
        #return 0

    def on_activate(self):
        """ 

        """

        # CONNECTORS PART 2 ###################################################
        self._ltunelaserlogic = self.ltunelaserlogic()

        self._mw = LtuneLaserMainWindow()
        self._pw = self._mw.powerTrace

        # Connect buttons to functions
        self._mw.powerInput.setMaximum(1000)
        self._mw.powerInput.valueChanged.connect(self.setPower)
        self._mw.switchLaser.clicked.connect(self.updateButton)
        
        self.power = 0

        # Connect update signal
        # self._ltunelaserlogic.sigUpdateLaserDisplay.connect(self.updateDisplay)
        self._ltunelaserlogic.sigUpdateLaserDisplay.connect(self.updatePlot)

        # set up plot

        self.plot1 = self._pw.plotItem
        self.plot1.setLabel('left', 'Power Output', units='W', color='#00ff00')
        self.plot1.setLabel('bottom')

        self.curvearr = []
        ## Create an empty plot curve to be filled later, set its pen
        self.curvearr.append(self.plot1.plot())
        self.curvearr[-1].setPen(palette.c1)

        self.timePass = 0
        self.powerOutputArr = []



    def updatePlot(self):
        """ The function that grabs the data and sends it to the plot.
        """
        self.timePass += 1
        self.powerOutputArr.append(self._ltunelaserlogic.power)
        # self.powerOutputArr.append(self._pmlogic.power)
        if (self.timePass < 200):
            self.curvearr[0].setData(
                y = np.asarray(self.powerOutputArr),
                x = np.arange(0, self.timePass)
                )
        else:
            self.curvearr[0].setData(
                y = np.asarray(self.powerOutputArr)[self.timePass-200, self.timePass],
                x = np.arange(self.timePass-200, self.timePass)
                )


    def setPower(self):
        self.power = self._mw.powerInput.value()

        if (self.enabled):
            self._ltunelaserlogic.set_power(self.power)

    def updateButton(self):
        if (self.enabled == False):
            self._ltunelaserlogic.enable_laser()
            self.enabled = True
            if (self.power != 0):
                self._ltunelaserlogic.set_power(self.power)
            self._mw.switchLaser.setText("Disable Laser")
        else:
            self._ltunelaserlogic.disable_laser()
            self.enabled = False
            self._mw.switchLaser.setText("Enable Laser")
