from enum import Enum

class INDIDeviceType(Enum):
    TELESCOPE = "telescope"
    CAMERA = "camera"
    FOCUSER = "focuser"
    FILTER_WHEEL = "filter_wheel"
    GENERIC = "indi"

    @classmethod
    def from_str(cls, value: str):
        """Get the type from a string"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.GENERIC

    def __str__(self):
        """Get the device value"""
        return self.value
