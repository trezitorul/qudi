import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import uic
from gui.colordefs import QudiPalettePale as palette

class RelayMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_relayboard_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class ErrorDialog(QtWidgets.QDialog):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_counts_error.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)

class RelayGUI(GUIBase):
    """

    """
    
    # connectors
    relaylogic = Connector(interface='RelayLogicInterface')

    # storing channel states

    isOn = []
    for i in range(17):
        isOn.append(False)


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
        self._relaylogic = self.relaylogic()

        self._mw = RelayMainWindow()
        self._dw = ErrorDialog()

        # Connect buttons to functions
        self.buttons = []
        for i in range(18):
            self.buttons.append(0)

        self.buttons[0] = self._mw.allOnButton
        self.buttons[1] = self._mw.pushButton_1
        self.buttons[2] = self._mw.pushButton_2
        self.buttons[3] = self._mw.pushButton_3
        self.buttons[4] = self._mw.pushButton_4
        self.buttons[5] = self._mw.pushButton_5
        self.buttons[6] = self._mw.pushButton_6
        self.buttons[7] = self._mw.pushButton_7
        self.buttons[8] = self._mw.pushButton_8
        self.buttons[9] = self._mw.pushButton_9
        self.buttons[10] = self._mw.pushButton_10
        self.buttons[11] = self._mw.pushButton_11
        self.buttons[12] = self._mw.pushButton_12
        self.buttons[13] = self._mw.pushButton_13
        self.buttons[14] = self._mw.pushButton_14
        self.buttons[15] = self._mw.pushButton_15
        self.buttons[16] = self._mw.pushButton_16
        self.buttons[17] = self._mw.allOffButton

        for i in range(1,17):
            self.buttons[i].clicked.connect(lambda: self.toggle(i))
            self.buttons[i].setStyleSheet("background-color : grey")
        
        # self._mw.pushButton_1.clicked.connect(lambda: self.toggle(1))
        # self._mw.pushButton_2.clicked.connect(lambda: self.toggle(2))
        # self._mw.pushButton_3.clicked.connect(lambda: self.toggle(3))
        # self._mw.pushButton_4.clicked.connect(lambda: self.toggle(4))
        # self._mw.pushButton_5.clicked.connect(lambda: self.toggle(5))
        # self._mw.pushButton_6.clicked.connect(lambda: self.toggle(6))
        # self._mw.pushButton_7.clicked.connect(lambda: self.toggle(7))
        # self._mw.pushButton_8.clicked.connect(lambda: self.toggle(8))
        # self._mw.pushButton_9.clicked.connect(lambda: self.toggle(9))
        # self._mw.pushButton_10.clicked.connect(lambda: self.toggle(10))
        # self._mw.pushButton_11.clicked.connect(lambda: self.toggle(11))
        # self._mw.pushButton_12.clicked.connect(lambda: self.toggle(12))
        # self._mw.pushButton_13.clicked.connect(lambda: self.toggle(13))
        # self._mw.pushButton_14.clicked.connect(lambda: self.toggle(14))
        # self._mw.pushButton_15.clicked.connect(lambda: self.toggle(15))
        # self._mw.pushButton_16.clicked.connect(lambda: self.toggle(16))

        self._mw.allOnButton.clicked.connect(self.allOn)
        self._mw.allOffButton.clicked.connect(self.allOn)

        self._dw.continueButton.clicked.connect(self.continueCheck)


        # Connect signals
        self._relaylogic.sigError.connect(self.errorHandling)
        self._relaylogic.sigError2.connect(self.continueCheck)

        self.show()


    def toggle(self, chan):
        """ 
        Toggle channels.
        """
        if self.isOn[chan]:
            self._relaylogic.switchOff(chan)
            self.isOn[chan] = False
            self.buttons[chan].setStyleSheet("background-color : grey")
        else:
            self._relaylogic.switchOn(chan)
            self.isOn[chan] = True
            self.buttons[chan].setStyleSheet("background-color : green")

    def allOn(self):
        self._relaylogic.allOn()
        for i in range(1,17):
            self.isOn[i] = True
            self.buttons[i].setStyleSheet("background-color : green")

    def allOff(self):
        self._relaylogic.allOff()
        for i in range(1,17):
            self.isOn[i] = False
            self.buttons[i].setStyleSheet("background-color : grey")

    def updateButton(self):
        if (self.is_manual == False):
            self.is_manual = True
            self._mw.switchMode.setText("Move by Input")
        else:
            self.is_manual = False
            self._mw.switchMode.setText("Move by Step")

    def errorHandling(self):
        for i in range(1,17):
            self.isOn[i] = False
            self.buttons[i].setStyleSheet("background-color : grey")
            self.buttons[i].setEnabled(False)

        self._dw.show()

        # self._mw.pushButton_1.setEnabled(False)
        # self._mw.pushButton_2.setEnabled(False)
        # self._mw.pushButton_3.setEnabled(False)
        # self._mw.pushButton_4.setEnabled(False)
        # self._mw.pushButton_5.setEnabled(False)
        # self._mw.pushButton_6.setEnabled(False)
        # self._mw.pushButton_7.setEnabled(False)
        # self._mw.pushButton_8.setEnabled(False)
        # self._mw.pushButton_9.setEnabled(False)
        # self._mw.pushButton_10.setEnabled(False)
        # self._mw.pushButton_11.setEnabled(False)
        # self._mw.pushButton_12.setEnabled(False)
        # self._mw.pushButton_13.setEnabled(False)
        # self._mw.pushButton_14.setEnabled(False)
        # self._mw.pushButton_15.setEnabled(False)
        # self._mw.pushButton_16.setEnabled(False)

        self._mw.allOnButton.setEnabled(False)
        self._mw.allOffButton.setEnabled(False)

    def continueCheck(self, isSafe=False):
        if not isSafe:
            self._dw.errorMessage.setText("Counts still too high! Try again!")
            self._relaylogic.continueCheck()
        else:
            # self._mw.pushButton_1.setEnabled(True)
            # self._mw.pushButton_2.setEnabled(True)
            # self._mw.pushButton_3.setEnabled(True)
            # self._mw.pushButton_4.setEnabled(True)
            # self._mw.pushButton_5.setEnabled(True)
            # self._mw.pushButton_6.setEnabled(True)
            # self._mw.pushButton_7.setEnabled(True)
            # self._mw.pushButton_8.setEnabled(True)
            # self._mw.pushButton_9.setEnabled(True)
            # self._mw.pushButton_10.setEnabled(True)
            # self._mw.pushButton_11.setEnabled(True)
            # self._mw.pushButton_12.setEnabled(True)
            # self._mw.pushButton_13.setEnabled(True)
            # self._mw.pushButton_14.setEnabled(True)
            # self._mw.pushButton_15.setEnabled(True)
            # self._mw.pushButton_16.setEnabled(True)

            # self._mw.allOnButton.setEnabled(True)
            # self._mw.allOffButton.setEnabled(True)

            for i in range(18):
                self.buttons[i].setEnabled(True)

    def show(self):
        """Make main window visible and put it above all other windows. """
        # Show the Main GUI:
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()
