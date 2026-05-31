"""
Camera device implementation.
"""
from devices.INDIDevice import INDIDevice, INDIDeviceType


class Camera(INDIDevice):
    """
    Proxy for an INDI Camera device.
    """

    def __init__(self, client, device_name):
        """
        Initializes the Camera proxy.

        Args:
            client (IPyClient): The INDI client instance.
            device_name (str): The unique name of the camera.
        """
        super().__init__(client, device_name)
        self._type: INDIDeviceType = INDIDeviceType.CAMERA
