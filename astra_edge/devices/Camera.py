from devices.INDIDevice import INDIDevice, INDIDeviceType


class Camera(INDIDevice):

    def __init__(self, client, device_name):
        super().__init__(client, device_name)
        self._type:INDIDeviceType = INDIDeviceType.CAMERA

