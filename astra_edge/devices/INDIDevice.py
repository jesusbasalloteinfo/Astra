"""
Base INDI device proxy implementation.
"""
from indipyclient import IPyClient
from devices.INDITypes import INDIDeviceType

class INDIDevice:
    """
    Base class for INDI device proxies.

    Provides common functionality for connecting, disconnecting, and 
    querying the status of an INDI device via an INDI client.

    Attributes:
        _client (IPyClient): The INDI client instance used for communication.
        _name (str): The unique name of the device.
        _type (INDIDeviceType): The type of device (defaults to GENERIC).
    """
    def __init__(self, client: IPyClient, name: str):
        """
        Initializes the INDIDevice proxy.

        Args:
            client (IPyClient): The INDI client instance.
            name (str): The unique name of the device.
        """
        self._client: IPyClient = client
        self._name: str = name
        self._type: INDIDeviceType = INDIDeviceType.GENERIC

    @property
    def name(self) -> str:
        """
        Returns the name of the device.

        Returns:
            str: The device name.
        """
        return self._name
    
    @property
    def type(self) -> INDIDeviceType:
        """
        Returns the type of the device.

        Returns:
            INDIDeviceType: The device type enum member.
        """
        return self._type
    
    @property
    def _device_data(self) -> dict:
        """
        Retrieves the raw device data from the INDI client.

        Returns:
            dict: The dictionary containing device properties and values.
        """
        return self._client[self._name]

    def is_connected(self) -> bool:
        """
        Checks if the device is currently connected to the INDI server.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._device_data["CONNECTION"]["CONNECT"] in ["On", "ON"]
    
    async def connect(self):
        """
        Sends a connection request to the device.
        """
        await self._client.send_newVector(self.name, "CONNECTION", members={"CONNECT": "On", "DISCONNECT": "Off"})

    async def disconnect(self):
        """
        Sends a disconnection request to the device.
        """
        await self._client.send_newVector(self.name, "CONNECTION", members={"CONNECT": "Off", "DISCONNECT": "On"})
            

    def __repr__(self):
        """
        Returns a string representation of the device.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns a user-friendly string representation of the device and its status.
        """
        status = "🟢" if self.is_connected() else "🔴"
        return f"[{self._type.value.upper()}] {self._name} {status}"
