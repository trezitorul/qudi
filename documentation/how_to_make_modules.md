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

  sig_update_display = QtCore.Signal() # To send a signal to update GUI display

  def on_activate(self):
    self._hardware_module = self.hardware_module() # To use the hardware module's functions
    # Other steps the module must do on activation

  def on_deactivate(self):
    # What the module must do on deactivation

  # Other user-defined functions
```


## Creating a GUI module

## Creating an interface

## Creating an interfuse module
