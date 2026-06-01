"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Enumerations for INDI device types used in astra_edge.
"""
from enum import Enum

class INDIDeviceType(Enum):
    """
    Enumeration of supported INDI device types.
    """
    TELESCOPE = "telescope"
    CAMERA = "camera"
    FOCUSER = "focuser"
    FILTER_WHEEL = "filter_wheel"
    GENERIC = "indi"

    @classmethod
    def from_str(cls, value: str):
        """
        Returns the matching INDIDeviceType for a given string.

        Args:
            value (str): The string representation of the device type.

        Returns:
            INDIDeviceType: The matching enum member, or GENERIC if no match is found.
        """
        try:
            return cls(value.lower())
        except ValueError:
            return cls.GENERIC

    def __str__(self):
        """
        Returns the string value of the enum member.

        Returns:
            str: The value of the device type (e.g., 'telescope').
        """
        return self.value
