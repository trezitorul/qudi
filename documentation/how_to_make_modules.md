# How to create modules  {#make-modules}


## Decide on the structure

A typical structure follows hardware->logic->GUI. In some cases where additional logic modules are needed, use connectors to share the logic. Logic modules are the only module type that can be connected to others of the same type. 

## Creating a hardware module

Basic structure of a hardware modules:
```python
from core.module import Base
from core.configoption import ConfigOption

class HardwareModule (Base):
    config = ConfigOption(name='config', missing='warn')
  
    def on_activate(self):
        # What the module must do on activation
  
    def on_deactivate(self):
        # What the module must do on deactivation

    # Other user-defined functions or inherited functions from interface
```

Use the hardware manufacturer's library if applicable. Depending on the desired logic, an interface (or multiple) can be used to abstract the hardware functions. If the interface is used, the hardware will inherit all of the abstract methods from the interface. There can also be additional, specific functions to the hardware that are not inherited from the interface. All hardware modules must inherit the Base class from core.module.

## Creating a logic module

Basic structure of a logic module:
```python
from logic.generic_logic import GenericLogic
from core.connector import Connector
from qtpy import QtCore
from core.configoption import ConfigOption   # Optional, if you need additional config options from .cfg files

class LogicModule(GenericLogic):
    # Either directly to the hardware module or use an interface
    harware_module = Connector(interface='HardwareModule')
    additional_config = ConfigOption(name='additional')
    
    sig_update_display = QtCore.Signal() # Signals for connecting modules
    
    def on_activate(self):
        self._hardware_module = self.hardware_module() # To use the hardware module's functions
        # Other steps the module must do on activation
    
    def on_deactivate(self):
        # What the module must do on deactivation
    
    # Other user-defined functions
    def use_functions_from_hardware(self):
        self._hardware_module.function_from_hardware()
  
```

Use a query loop to constantly perform a certain action (collect data, update display, etc.). A query loop cannot be started or stopped from another module, so a connector is not enough to call ```start_query_loop()``` or ```stop_query_loop()```. These functions must be called from the logic of triggered with signals. Below is an example for constantly collecting data and updating the display:
```python
from qtpy import QtCore
from logic.generic_logic import GenericLogic

class LogicModule(GenericLogic):
    # Connectors and ConfigOptions

    def on_activate(self):
        # Initialization
    
        self.stop_request = False
        self.buffer_length = 100
        self.query_timer = QtCore.QTimer()
        self.query_timer.setInterval(self.query_interval)
        self.query_timer.setSingleShot(True)
        self.query_timer.timeout.connect(self.check_loop, QtCore.Qt.QueuedConnection)
        
        self.start_query_loop()

    def on_deactivate(self):
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
        """ Get position and update display. """
        if self.stop_request:
            if self.module_state.can('stop'):
                self.module_state.stop()
            self.stop_request = False
            return
        qi = self.query_interval
        try:
            self.position = self.get_data() # User-defined data collection function

        except:
            qi = 3000
            self.log.exception("Exception in status loop, throttling refresh rate.")

        self.query_timer.start(qi)
        self.sig_update_display.emit()

    def get_data(self):
        # Get data
```

## Creating a GUI module

Start by making a .ui file for the main window. This can be easily done with the QtPy designer application. If Qudi is installed correctly, it should come with the environment and you can simply type designer in the terminal to open the app. In designer, various features can be added for the user to interact with or to display information. Change the object name of all relevant buttons or features to best reflect their purposes. The .ui file must be stored in the same folder as the GUI python file.

In the GUI python file, there is a class for the GUI module itself and a class for each QtWidgets window object. In most cases, the only window will be the main window. The main window is created and shown during activation. The new GUI class must inherit the GUIBase class.

Basic structure of a GUI module:
```python
import os

from gui.guibase import GUIBase
from core.connector import Connector
from qtpy import QtWidgets
from qtpy import uic

class ExampleMainWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_exampe_gui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class ExampleGUI(GUIBase):
    logic = Connector(interface='LogicModule')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        """ Definition and initialisation of the GUI."""
        self._logic = self.logic()

        self._mw = ExampleMainWindow()

        # Connect buttons and spinboxes to functions to handle user interactions. Feature name comes from .ui file.
        self._mw.myButton.clicked.connect(self.myFunction)
        self._mw.mySpinBox.valueChanged.connect(self.changeValue)

        # Connect signals (in this example, the GUI is triggered by the logic to update the display)
        self._logic.sigUpdateDisplay.connect(self.updateDisplay)

        self.show()

    def show(self):
        """Make main window visible and put it above all other windows. """
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()

    # Other user-defined functions

    def myFunction(self):
        # Does something to respond to user

    def changeValue(self):
        # Stores value from spinbox. Should then use value to perform an action.
        self.myValue = self._mw.mySpinbox.value() 

    def updateDisplay(self):
        # Displays a value that comes from the logic.
        self.displayLabel.setText(self._logic.value)
```

## Creating an interface

An interface allows different hardware devices to be interchanged, making logic modules reusable. Interfaces inherit the interface metaclass and only consist of abstract interface methods. These methods are empty and must be reimplemented in the hardware modules that inherit them.

Basic structure of an interface:
```python
from core.interface import abstract_interface_method
from core.meta import InterfaceMetaclass


class ExampleInterface(metaclass=InterfaceMetaclass):

    @abstract_interface_method
    def set_value(self, value):
        """ Set a value
        @param float value: desired new value
        """
        pass

    @abstract_interface_method
    def get_value(self):
        """ Get a value
        @return float
        """
        pass
```

## Creating an interfuse module

An interfuse is a type of logic module that inherits an interface. It allows a logic module to be used in a way that it was not initially intended to be used and essentially adds an extra layer between the main logic and the hardware. These have the same structure as a logic module but they also reimplement all of the functions that they inherit from their interface.
