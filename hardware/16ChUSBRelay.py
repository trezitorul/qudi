import serial
import time

from core.module import Base
from core.configoption import ConfigOption

class USB_Relay(Base):
    
    channels = []
    for i in range(17):
        channels.append(0)
    channels[0] = {'off': b':FE0F00000010020000E1\r\n', 'on': b':FE0F0000001002FFFFE3\r\n'} #all channels
    channels[1] = {'off': b':FE0500000000FD\r\n', 'on': b':FE050000FF00FE\r\n'}
    channels[2] = {'off': b':FE0500010000FC\r\n', 'on': b':FE050001FF00FD\r\n'}
    channels[3] = {'off': b':FE0500020000FB\r\n', 'on': b':FE050002FF00FC\r\n'}
    channels[4] = {'off': b':FE0500030000FA\r\n', 'on': b':FE050003FF00FB\r\n'}
    channels[5] = {'off': b':FE0500040000F9\r\n', 'on': b':FE050004FF00FA\r\n'}
    channels[6] = {'off': b':FE0500050000F8\r\n', 'on': b':FE050005FF00F9\r\n'}
    channels[7] = {'off': b':FE0500060000F7\r\n', 'on': b':FE050006FF00F8\r\n'}
    channels[8] = {'off': b':FE0500070000F6\r\n', 'on': b':FE050007FF00F7\r\n'}
    channels[9] = {'off': b':FE0500080000F5\r\n', 'on': b':FE050008FF00F6\r\n'}
    channels[10] = {'off': b':FE0500090000F4\r\n', 'on': b':FE050009FF00F5\r\n'}
    channels[11] = {'off': b':FE05000A0000F3\r\n', 'on': b':FE05000AFF00F4\r\n'}
    channels[12] = {'off': b':FE05000B0000F2\r\n', 'on': b':FE05000BFF00F3\r\n'}
    channels[13] = {'off': b':FE05000C0000F1\r\n', 'on': b':FE05000CFF00F2\r\n'}
    channels[14] = {'off': b':FE05000D0000F0\r\n', 'on': b':FE05000DFF00F1\r\n'}
    channels[15] = {'off': b':FE05000E0000FF\r\n', 'on': b':FE05000EFF00F0\r\n'}
    channels[16] = {'off': b':FE05000F0000FE\r\n', 'on': b':FE05000FFF00FF\r\n'}

    status = b':FE0100200000FF\r\n'
    statusReturn = b':FE0100000010F1\r\n'

    com_port = ConfigOption(name='com_port', missing='error')
    
    def on_activate(self):
        """ Initialisation performed during activation of the module.
         """
        # Start serial connection
        self.ser = serial.Serial(
                        port = self.com_port,
                        baudrate = 9600,
                        timeout = 5
                )
        
    def on_deactivate(self):
        """
        Deinitialisation performed during deactivation of the module.
        """
        self.allOff()
        self.close()
                
    def switchOn(self, chan):
        self.ser.write(self.channels[chan]['on'])

    def switchOff(self, chan):
        self.ser.write(self.channels[chan]['off'])

    def allOn(self):
        self.ser.write(self.channels[0]['on'])

    def allOff(self):
        self.ser.write(self.channels[0]['off'])

    def close(self):
        self.ser.close()

    def getStatus(self):
        self.ser.write(self.statusReturn)
        return self.ser.readline()