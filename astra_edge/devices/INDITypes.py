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
