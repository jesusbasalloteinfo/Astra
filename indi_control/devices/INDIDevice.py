from indipyclient import IPyClient
from devices.INDITypes import *

class INDIDevice:
    """Base INDI device proxy"""
    def __init__(self, client:IPyClient, name:str):
        self._client:IPyClient = client
        self._name:str = name
        self._type:INDIDeviceType = INDIDeviceType.GENERIC

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def type(self) -> INDIDeviceType:
        return self._type
    
    @property
    def _device_data(self) -> dict:
        """Gets the device data from indipyclient"""
        return self._client[self._name]

    def is_connected(self) -> bool:
        """Check if the device is connectet to the INDI client"""
        return self._device_data["CONNECTION"]["CONNECT"] in ["On", "ON"]
    
    async def connect(self):
        """Connect the device"""
        await self._client.send_newVector(self.name, "CONNECTION", members={"CONNECT": "On", "DISCONNECT": "Off"})

    async def disconnect(self):
        """Disconnect the device"""
        await self._client.send_newVector(self.name, "CONNECTION", members={"CONNECT": "Off", "DISCONNECT": "On"})
            

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        status = "🟢" if self.is_connected() else "🔴"
        return f"[{self._type.value.upper()}] {self._name} {status}"


