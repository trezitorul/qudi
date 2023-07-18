# -*- coding: utf-8 -*-
""" Logic module for the DAQ counter
"""

import time
from core.configoption import ConfigOption
from core.connector import Connector
from logic.generic_logic import GenericLogic
from qtpy import QtCore


class DaqCounter(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """
    counter_channel = ConfigOption(name='counter_channel', missing='error')
    dt = ConfigOption('dt', .001)
    daq = Connector(interface='DAQ')
    query_interval = ConfigOption('query_interval', 100)
    counts = 0

    
    # signals
    sig_update_display = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work.
        """

        self._daq = self.daq()
        self._counter_channel = int(self.counter_channel)

        self.stop_request = False
        self.buffer_length = 100

        # delay timer for querying hardware
        self.query_timer = QtCore.QTimer()
        self.query_timer.setInterval(self.query_interval)
        self.query_timer.setSingleShot(True)
        self.query_timer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)

        self.start_query_loop()

    def on_deactivate(self):
        """ When the module is deactivated
        """
        self.stop_query_loop()
        for i in range(5):
            time.sleep(self.query_interval / 1000)
            QtCore.QCoreApplication.processEvents()

    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop. """
        self.module_state.run()
        self.query_timer.start(self.query_interval)

    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stop_request = True
        for i in range(10):
            if not self.stop_request:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.query_interval/1000)
    
    @QtCore.Slot()
    def check_loop(self):
        """ Get counts and update display. """
        if self.stop_request:
            if self.module_state.can('stop'):
                self.module_state.stop()
            self.stop_request = False
            return
        qi = self.query_interval
        try:
            self.counts = self.getCounts(self.dt)

        except:
            qi = 3000
            self.log.exception("Exception in piezo status loop, throttling refresh rate.")

        self.query_timer.start(qi)
        self.sig_update_display.emit()

    def getCounts(self,dt):
        '''
        Implementing electrical pulse countings on the Daq cards
        Args:
            dt (floats): time differential
        Return number of counts
        '''
        return self._daq.getCounts(dt, self._counter_channel) / self.dt
