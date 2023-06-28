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

    daq = Connector(interface='DAQ')
    
    # signals
    sigUpdateDisplay = QtCore.Signal()

    # Connect signals

    def on_activate(self):
        """ Prepare logic module for work.
        """

        self._daq = self.daq()
        self.counterchannel = int(self._counterchannel)

    def on_deactivate(self):
        pass

    def getCounts(self,dt):
        '''
        Implementing electrical pulse countings on the Daq cards
        '''
        return self._daq.getCounts(dt, self.counterchannel)
