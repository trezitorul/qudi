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
        self._stepperlogic = self.stepperlogic()

        self._mw = StepperMainWindow()

        # Set default parameters
        self.position = [0, 0, 0]
        self._mw.StepSize.setValue(1)
        self.stepSize = 1
        self.is_step = True
        self.is_pull = False


        # Connect buttons to functions        
        self._mw.StepSize.valueChanged.connect(self.stepChanged)

        self._mw.posDirButton.installEventFilter(self)  # Install event filter on the button
        self._mw.posDirButton.clicked.connect(lambda: self.on_button_clicked(1))
        self.setCentralWidget(self._mw.posDirButton)

        self._mw.negDirButton.installEventFilter(self)  # Install event filter on the button
        self._mw.negDirButton.clicked.connect(lambda: self.on_button_clicked(-1))
        self.setCentralWidget(self._mw.negDirButton)
        
        self.mouse_held = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_hold)

        # Connect update signal
        self._stepperlogic.sigUpdateDisplay.connect(self.updateDisplay)
        self.show()

    def eventFilter(self, obj, event):
        if obj == self.button and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.mouse_held = True
                self.timer.start(150)  # Start the timer

        elif obj == self.button and event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                self.mouse_held = False
                self.timer.stop()  # Stop the timer

        return super().eventFilter(obj, event)


    def check_mouse_hold(self, direction):
        if self.mouse_held:
            self.move(direction)


    def on_button_clicked(self, direction):
        self.move(direction)


    def move(self, direction):
        self._stepperlogic.move_rel(direction, self.step)


    def stepChanged(self):
        self.stepSize = self._mw.StepSize.value()


    def updateDisplay(self):
        self.position = self._stepperlogic.position
        self._mw.totalRev.setText(self.position)

    def show(self):
        """Make main window visible and put it above all other windows. """
        # Show the Main GUI:
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()
