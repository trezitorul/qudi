# -*- coding: utf-8 -*-
"""
Powermeter GUI module that displays power output in mW.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

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
    """ Power meter GUI main class.
    """
    
    # CONNECTORS #############################################################
    pmlogic = Connector(interface='PowerMeterLogic')

    # SIGNALS ################################################################
   

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_deactivate(self):
        """ Reverse steps of activation

        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        #return 0

    def on_activate(self):
        """ Initialize, connect and configure the powermeter GUI.
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
        self._mw.startButton.clicked.connect(self._pmlogic.start) #could also connect directly to logic
        self._mw.stopButton.clicked.connect(self._pmlogic.stop)

        # Connect signals
        self._pmlogic.sigUpdatePMDisplay.connect(self.updateDisplay)
        self._pmlogic.sigUpdatePMDisplay.connect(self.updatePlot)


    def updateDisplay(self):
        """ Updates display text with current output power in mW.
        """
        self._mw.powerOutput.setText(str(round(self._pmlogic.power, 3)))


    def updatePlot(self):
        """ The function that grabs the power output data and sends it to the plot.
        """
        self.timePass += 1
        self.powerOutputArr.append(self._pmlogic.power)
        
        if (self.timePass < 200):
            self.curvearr[0].setData(
                y = np.asarray(self.powerOutputArr),
                x = np.arange(0, self.timePass)
                )
        else:
            self.curvearr[0].setData(
                y = np.asarray(self.powerOutputArr[self.timePass - 200:self.timePass]),
                x = np.arange(self.timePass - 200, self.timePass)
                )
