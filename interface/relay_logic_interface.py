#-*- coding: utf-8 -*-
"""

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

from core.interface import abstract_interface_method
from core.meta import InterfaceMetaclass

class RelayLogicInterface(metaclass=InterfaceMetaclass):

    @abstract_interface_method
    def switchOn(self, chan):
        """
        Switch on one channel.
        """
        pass

    @abstract_interface_method
    def switchOff(self, chan):
        """
        Switch off one channel.
        """
        pass

    @abstract_interface_method
    def allOn(self):
        """
        Switch on all channels.
        """
        pass

    @abstract_interface_method
    def allOff(self):
        """
        Switch off all channels.
        """
        pass

    @abstract_interface_method
    def close(self):
        """
        Close serial connection.
        """
        pass