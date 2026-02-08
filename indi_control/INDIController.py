import asyncio
from datetime import datetime
from indipyclient import IPyClient
from devices.INDIDeviceFactory import *
from utils.CoordinateHandler import CoordinateHandler, CoordinateTypes
from utils.logging import get_logger

import re

LOGGER=get_logger("INDIController")

class INDIClient(IPyClient):
    """
    INDI Client Class to handle events
    """

    def __init__(self, host, port, event_callback):
        super().__init__(host=host, port=port)
        self.event_callback = event_callback

        # Parses lines starting with "[LEVEL] Message" format.
        # Group 1: Log Category | Group 2: Remaining message text
        self.tag_re = re.compile(r'^\[(INFO|WARNING|ERROR|DEBUG)\]\s*(.*)', re.IGNORECASE)

    def format_position_messages(self, event):
        
        data = {"RA": event.vector["RA"], "DEC": event.vector["DEC"]}
        time=event.timestamp
        handler=CoordinateHandler()
        if event.vectorname == CoordinateTypes.ALTAZIMUTAL.value:
            # TODO: Coordinates missing!!
            data = handler.convert_from(time, map(float, (event.vector["ALT"], event.vector["AZ"])), (), CoordinateTypes.ALTAZIMUTAL)

        elif event.vectorname == CoordinateTypes.EQUATORIAL_EOD.value:
            data = handler.convert_from(time, map(float, (event.vector["RA"], event.vector["DEC"])), None, convert_from=CoordinateTypes.EQUATORIAL_EOD)
        
        return {"ra": data["RA"], "dec": data["DEC"]}

    async def rxevent(self, event):
        if event.eventtype == "Message":
            raw_msg = event.message
            match = self.tag_re.match(raw_msg)
            
            if match:
                level = match.group(1).upper()
                clean_msg = match.group(2)
            else:
                level = "INFO"  # Default level
                clean_msg = raw_msg

            await self.event_callback("LOG", {
                "level": level, 
                "msg": clean_msg, 
                "device": event.devicename
            })
        
        elif event.eventtype == "Set":
            if event.vectorname in CoordinateTypes.list_values():
                rta=self.format_position_messages(event)
                await self.event_callback("COORD_UPDATE", rta)

        elif event.eventtype == "Define":
            # Handled in INDIController, no need to send them
            pass

        elif event.eventtype == "Delete":
            # Handled in INDIController, no need to send them
            pass
        elif event.eventtype == "Busy":
            # Handled in INDIController, no need to send them
            pass
        await super().rxevent(event)


# TODO: IMPROVE CALLBACK !!

class INDIController:
    """
    Class to control an INDI client and server
    """

    def __init__(self, host="localhost", port=7624, event_callback=None):
        self._client:INDIClient = INDIClient(host, port, event_callback)
        
        self._devices_proxy:dict[INDIDevice] = {}

    async def start(self):
        """Start the async loop of the client"""
        return asyncio.create_task(self._client.asyncrun())
    
    async def _probe_device(self, device_name):
        """
        Connect the device for a moment to read its properties and create a proxy object
        """
        # Create as generic
        temp_device:INDIDevice= INDIDevice(self._client, device_name)

        try:
            proxy = INDIDeviceFactory.create(self._client, device_name)
        except Exception as e:
            LOGGER.error(f"Error creating proxy for {device_name}: {e}")
            proxy = temp_device
        
        return proxy

    async def _sync_proxies(self):
        """
        Synchronize proxies with INDI client state.
        """
        keys_indi = set(self._client.keys())
        keys_proxy = set(self._devices_proxy.keys())

        to_add = keys_indi - keys_proxy
        to_remove = keys_proxy - keys_indi

        if to_add or to_remove:
            LOGGER.debug(f"Device changes detected. New: {to_add}, Lost: {to_remove}")

        # Delete lost devices
        for name in to_remove:
            del self._devices_proxy[name]
        
        # Check existing Generic devicesz
        for name, proxy in list(self._devices_proxy.items()):
            if proxy.type == INDIDeviceType.GENERIC:
                LOGGER.debug(f"Added generic device to scan queue: {name}")
                del self._devices_proxy[name]
                to_add.add(name)

        if to_add:
            LOGGER.debug(f"Scanning devices: {to_add}")
            # Parallel to speed scanning
            tasks = [INDIDeviceFactory.create(self._client, name) for name in to_add]
            results = await asyncio.gather(*tasks)
            
            for proxy in results:
                self._devices_proxy[proxy.name] = proxy
                LOGGER.debug(f"Registered device: {proxy}")


    async def get_devices(self)->dict[list]:
        """
        Gets the connected devices by name and type
        """
        await self._sync_proxies()

        # Device types dict
        ret = {category.value: [] for category in INDIDeviceType}
        
        for proxy in self._devices_proxy.values():
            category_key = proxy.type.value           
            ret[category_key].append(proxy.name)

        return ret
    
    async def get_proxy(self, device_name: str) -> INDIDevice:
        """Return the proxy object"""
        await self._sync_proxies()
        if device_name not in self._devices_proxy:
            raise ValueError(f"Device {device_name} not found!")
        return self._devices_proxy.get(device_name)
    

    async def get_telescope(self, telescope_name) -> Telescope:
        """Helper to get the first available telescope"""
        return await self.get_proxy(telescope_name)
    
        # TODO: PENDING IF DELETED



