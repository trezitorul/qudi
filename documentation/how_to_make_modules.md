# How to create modules  {#make-modules}


## Decide on the structure

A typical structure follows hardware->logic->GUI. In some cases where additional logic modules are needed, use connectors to share the logic. This is the only module that can be connected to others with the same type. 

## Creating a hardware module

Basic structure of a hardware modules:
```
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

Basic structure of a hardware modules:
```
from logic.generic_logic import GenericLogic
from core.connector import Connector
from qtpy import QtCore
from core.configoption import ConfigOption   # Optional, if you need additional config options from .cfg files

class LogicModule(GenericLogic):
  harware_module = Connector(interface='HardwareModule')
  additional_config = ConfigOption(name='additional')

  sig_update_display = QtCore.Signal() # Signals for connecting modules
  
  def on_activate(self):
    self._hardware_module = self.hardware_module() # To use the hardware module's functions
    # Other steps the module must do on activation

  def on_deactivate(self):
    # What the module must do on deactivation

  # Other user-defined functions
```

Use start a query loop and constantly perform a certatin actions (collect data, update display, etc.) Below is for constantly getting data and updating the display:
```
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

```


## Creating a GUI module

## Creating an interface

## Creating an interfuse module
