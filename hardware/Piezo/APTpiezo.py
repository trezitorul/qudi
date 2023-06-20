# -*- coding: utf-8 -*-

import APTDevice_Piezo
import time

from core.module import Base
from core.configoption import ConfigOption


class APTPiezo(Base):
    """
    Initialise and open serial device for the ThorLabs APT controller.

    If the ``serial_port`` parameter is ``None`` (default), then an attempt to detect an APT device
    will be performed.
    The first device found will be initialised.
    If multiple devices are present on the system, then the use of the ``serial_number`` parameter
    will specify a particular device by its serial number.
    This is a `regular expression <https://docs.python.org/3/library/re.html>`_ match, for example
    ``serial_number="83"`` would match devices with serial numbers
    starting with 83, while ``serial_number=".*83$"`` would match devices ending in 83.

    Status updates can be obtained automatically from the device by setting ``status_updates="auto"``,
    which will request the controller to send regular updates, as well as sending the required "keepalive"
    acknowledgement messages to maintain the connection to the controller.
    In this case, ensure the :data:`keepalive_message` property is set correctly for the controller.

    To instead query the device for status updates on a regular basis, set ``status_updates="polled"``,
    in which case ensure the :data:`update_message` property is set correctly for the controller.

    The default setting of ``status_updates="none"`` will mean that no status updates will be
    performed, leaving the task up to sub-classes to implement.

    :param serial_port: Serial port device the device is connected to.
    :param vid: Numerical USB vendor ID to match.
    :param pid: Numerical USB product ID to match.
    :param manufacturer: Regular expression to match to a device manufacturer string.
    :param product: Regular expression to match to a device product string.
    :param serial_number: Regular expression to match to a device serial number.
    :param location: Regular expression to match to a device physical location (eg. USB port).
    :param controller: The destination :class:`EndPoint <thorlabs_apt_device.enums.EndPoint>` for the controller.
    :param bays: Tuple of :class:`EndPoint <thorlabs_apt_device.enums.EndPoint>`\\ (s) for the populated controller bays.
    :param channels: Tuple of indices (1-based) for the controller bay's channels.
    :param status_updates: Set to ``"auto"``, ``"polled"`` or ``"none"``.
    """
    _deviceID = ConfigOption(name='deviceID', missing='warn')
    _serial_port = ConfigOption(name='serial_port', missing='warn')
    _is_second_piezo = ConfigOption(name='is_second_piezo', default=False)
    

    def on_activate(self):
        """ Initialisation performed during activation of the module.
         """
        if (self._is_second_piezo):
            time.sleep(5)

        self.initialize()


    def on_deactivate(self):
        """
        Deinitialisation performed during deactivation of the module.
        """
        pass


    def initialize(self, channels=(1,2)):
        if (self._serial_port == None):
            self.piezo = APTDevice_Piezo.create(deviceID=self._deviceID, 
                                                channels=channels)
        else: 
            self.piezo = APTDevice_Piezo(serial_port=self._serial_port, deviceID=self._deviceID, 
                                        channels=channels)
    

    def set_position(self, position=None , bay=0, channel=0):
        """
        Set the position of the piezo.
        ONLY WORKS IN CLOSED LOOP MODE
        Units: microns

        :param position: Output position relative to zero position; sets as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo extension aka maxTravel.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # if (position == None):
        #     raise ValueError("MISSING INPUT FOR POSITION")

        # if (position < 0):
        #     raise ValueError("POSITION MUST BE POSITIVE")

        # currMode = self.piezo.info[channel]["mode"]

        # if (currMode != 0x02 and currMode != 0x04):
        #     raise ValueError("MUST BE IN CLOSED LOOP MODE")
        
        self.piezo.set_position(position=position, bay=bay, channel=channel)
        
        # max = self.piezo.info[channel]["maxTravel"]
        # positionOut=int((32767.0*position/max) * 10)

        # self.piezo.info[channel]["position"] = positionOut


    def get_position(self , bay=0, channel=0):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.
        Units: microns

        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        # currMode = self.piezo.info[channel]["mode"]

        # if (currMode != 0x02 and currMode != 0x04):
        #     raise ValueError("MUST BE IN CLOSED LOOP MODE")

        # position = self.piezo.info[channel]["position"]
        # maxTravel = self.piezo.info[channel]["maxTravel"]

        return round(self.piezo.get_position(bay=bay, channel=channel), 2)
