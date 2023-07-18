import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtWidgets
from qtpy import uic
from qtpy.QtCore import QTimer, Signal
from qtpy.QtCore import QTimer, Qt, QEvent



class StepperMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_stepper_motor.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()


class StepperGUI(GUIBase):
    """

    """
    
    # CONNECTORS #############################################################
    stepperlogic = Connector(interface='StepperMotorLogic')

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
        self._stepperlogic = self.stepperlogic()

        self._mw = StepperMainWindow()

        # Set default parameters
        self.position = [0, 0, 0]
        self._mw.StepSize.setValue(1)
        self.stepSize = 2048
        self.direction = 1
        self.axis = 0

        self._mw.rpmInput.setValue(12)
        self.rpm = 12

        # Connect buttons to functions        
        self._mw.StepSize.valueChanged.connect(self.stepChanged)
        self._mw.rpmInput.valueChanged.connect(self.rpmChanged)

        self._mw.leftButton.installEventFilter(self)  # Install event filter on the button
        self._mw.leftButton.clicked.connect(lambda: self.on_button_clicked(0, -1))

        self._mw.rightButton.installEventFilter(self)  # Install event filter on the button
        self._mw.rightButton.clicked.connect(lambda: self.on_button_clicked(0, 1))

        self._mw.upButton.installEventFilter(self)  # Install event filter on the button
        self._mw.upButton.clicked.connect(lambda: self.on_button_clicked(1, -1))

        self._mw.downButton.installEventFilter(self)  # Install event filter on the button
        self._mw.downButton.clicked.connect(lambda: self.on_button_clicked(1, 1))

        self.mouse_held = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_hold)

        # Connect update signal
        self._stepperlogic.sigUpdateDisplay.connect(self.updateDisplay)
        self.show()

    def eventFilter(self, obj, event):
        if (obj == self._mw.leftButton or obj == self._mw.rightButton
            or obj == self._mw.upButton or obj == self._mw.downButton) and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.mouse_held = True
                self.timer.start(150)  # Start the timer

        elif (obj == self._mw.leftButton or obj == self._mw.rightButton
            or obj == self._mw.upButton or obj == self._mw.downButton) and event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                self.mouse_held = False
                self.timer.stop()  # Stop the timer

        return self._mw.eventFilter(obj, event)


    def check_mouse_hold(self):
        if self.mouse_held:
            self.move(self.axis, self.direction)


    def on_button_clicked(self, axis, direction):
        self.move(axis, direction)
        self.axis = axis
        self.direction = direction


    def move(self, axis, direction):
        self._stepperlogic.move_rel(axis, direction, self.stepSize)


    def stepChanged(self):
        self.stepSize = int(self._mw.StepSize.value() * 2048)


    def rpmChanged(self):
        self.rpm = self._mw.rpmInput.value()
        self._stepperlogic.setRPM(self.rpm)


    def updateDisplay(self):
        self.positionX = self._stepperlogic.position[0]
        self.positionY = self._stepperlogic.position[1]
        self._mw.totalStepX.setText(str(self.positionX / 2048))
        self._mw.totalStepY.setText(str(self.positionY / 2048))


    def show(self):
        """Make main window visible and put it above all other windows. """
        # Show the Main GUI:
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()
