import numpy as np
import time
import matplotlib.pyplot as plt
import math

from core.configoption import ConfigOption
from core.connector import Connector
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class DaqCounter(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """
    _counterchannel = ConfigOption(name='counterchannel', missing='error')
    _dt = ConfigOption('dt', .001)

    daq = Connector(interface='DAQ')

    queryInterval = ConfigOption('query_interval', 100)

    counts = 0

    
    # signals
    sigUpdateDisplay = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """

        self._daq = self.daq()
        self.counterchannel = int(self._counterchannel)

        self.stopRequest = False
        self.bufferLength = 100

        # delay timer for querying hardware
        self.queryTimer = QtCore.QTimer()
        self.queryTimer.setInterval(self.queryInterval)
        self.queryTimer.setSingleShot(True)
        self.queryTimer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)

        self.start_query_loop()

    def on_deactivate(self):
        self.stop_query_loop()
        for i in range(5):
            time.sleep(self.queryInterval / 1000)
            QtCore.QCoreApplication.processEvents()

    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop. """
        self.module_state.run()
        self.queryTimer.start(self.queryInterval)

    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stopRequest = True
        for i in range(10):
            if not self.stopRequest:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.queryInterval/1000)
    
    @QtCore.Slot()
    def check_loop(self):
        """ Get counts and update display. """
        if self.stopRequest:
            if self.module_state.can('stop'):
                self.module_state.stop()
            self.stopRequest = False
            return
        qi = self.queryInterval
        try:
            self.counts = self.getCounts(self._dt)

        except:
            qi = 3000
            self.log.exception("Exception in piezo status loop, throttling refresh rate.")

        self.queryTimer.start(qi)
        self.sigUpdateDisplay.emit()

    def getCounts(self,dt):
        '''
        Implementing electrical pulse countings on the Daq cards
        '''
        return self._daq.getCounts(dt, self.counterchannel) / self._dt
