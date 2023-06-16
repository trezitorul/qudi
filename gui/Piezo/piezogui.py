import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class PiezoMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_APTpiezo_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class PiezoGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    # voltagescannerlogic1 = Connector(interface='LaserScannerLogic')
    # savelogic = Connector(interface='SaveLogic')

    # SIGNALS ################################################################
    # sigStartScan = QtCore.Signal()
    # sigStopScan = QtCore.Signal()
    # sigChangeVoltage = QtCore.Signal(float)
    # sigChangeRange = QtCore.Signal(list)
    # sigChangeResolution = QtCore.Signal(float)
    # sigChangeSpeed = QtCore.Signal(float)
    # sigChangeLines = QtCore.Signal(int)
    # sigSaveMeasurement = QtCore.Signal(str, list, list)

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
        # self._voltscan_logic = self.voltagescannerlogic1()
        # self._savelogic = self.savelogic()

        # Use the inherited class 'Ui_VoltagescannerGuiUI' to create now the
        # GUI element:
        self._mw = PiezoMainWindow()

        # Add save file tag input box
        # self._mw.save_tag_LineEdit = QtWidgets.QLineEdit(self._mw)
        # self._mw.save_tag_LineEdit.setMaximumWidth(500)
        # self._mw.save_tag_LineEdit.setMinimumWidth(200)
        # self._mw.save_tag_LineEdit.setToolTip('Enter a nametag which will be\n'
        #                                       'added to the filename.')
        # self._mw.toolBar.addWidget(self._mw.save_tag_LineEdit)

        # Get the image from the logic
        # self.scan_matrix_image = pg.ImageItem(
        #     self._voltscan_logic.scan_matrix,
        #     axisOrder='row-major')

        # self.scan_matrix_image.setRect(
        #     QtCore.QRectF(
        #         self._voltscan_logic.scan_range[0],
        #         0,
        #         self._voltscan_logic.scan_range[1] - self._voltscan_logic.scan_range[0],
        #         self._voltscan_logic.number_of_repeats)
        # )