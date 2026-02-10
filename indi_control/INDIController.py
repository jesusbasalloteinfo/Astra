import asyncio
from datetime import datetime
from indipyclient import IPyClient
from devices.INDIDeviceFactory import *
from utils.CoordinateHandler import CoordinateHandler, CoordinateTypes
from utils.logging import get_logger
from common.INDIModels import *

import re

LOGGER=get_logger("INDIController")

class INDIClient(IPyClient):
    """
    INDI Client Class to handle events
    """

    def __init__(self, host:str, port:int, context_provider:callable, device_type_provider:callable, send_event:callable):
        super().__init__(host=host, port=port)
        self.get_context = context_provider
        self.get_device_type = device_type_provider
        self.send_event = send_event

        # Parses lines starting with "[LEVEL] Message" format.
        # Group 1: Log Category | Group 2: Remaining message text
        self.message_regex = re.compile(r'^\[(INFO|WARNING|ERROR|DEBUG)\]\s*(.*)', re.IGNORECASE)
    
    def parse_message_level(self, raw_msg:str) -> tuple[str, str]:
        """Parse the level and message of the raw message with format [LEVEL] Message"""
        match = self.message_regex.match(raw_msg)
        if match:
            level = match.group(1).upper()
            clean_msg = match.group(2)
        else:
            level = "INFO"
            clean_msg = raw_msg
        return level, clean_msg

    def format_coordinates(self, event):

        """ Formats and converts the coordinates to a message """

        data = tuple(map(float, (event.vector.get("RA", "ALT"), event.vector.get("DEC", "AZ"))))
        time=event.timestamp
        location, _ = self.get_context()
        orig_type=CoordinateTypes.from_str(event.vectorname)

        eq_j2000_ra, eq_j2000_dec =CoordinateHandler.convert_coord(time, data, location, convert_from=orig_type, convert_to=CoordinateTypes.EQUATORIAL_J2000)
        eq_eod_ra, eq_eod_dec=CoordinateHandler.convert_coord(time, data, location, convert_from=orig_type, convert_to=CoordinateTypes.EQUATORIAL_EOD)
        horiz_alt, horiz_az=CoordinateHandler.convert_coord(time, data, location, convert_from=orig_type, convert_to=CoordinateTypes.HORIZONTAL)

        msg_eq_j2000=EquatorialCoordModel(ra=eq_j2000_ra, dec=eq_j2000_dec)
        msg_eq_eod=EquatorialCoordModel(ra=eq_eod_ra, dec=eq_eod_dec)
        msg_horiz=HorizontalCoordModel(alt=horiz_alt, az=horiz_az)

        data=CoordEventData(equatorial_j2000=msg_eq_j2000, equatorial_eod=msg_eq_eod, horizontal=msg_horiz)
        return CoordEvent(device=event.devicename, data=data)

    async def rxevent(self, event):
        """
        Process an event from INDI
        """
        payload=None
        if event.eventtype == "Message":
            level, content=self.parse_message_level(event.message)
            data=MessageEventData(level=level, content=content)
            device=event.devicename if event.devicename else "indi"
            device_type= await self.get_device_type(device)
            device_type="indi" if not device_type else device_type.value

            payload=MessageEvent(device=device, device_type=device_type, data=data)

        elif event.eventtype == "Set":
            if event.vectorname in CoordinateTypes.list_values():
                # Coordinate UPDATE
                payload=self.format_coordinates(event)

        elif event.eventtype == "Define":
            # Handled in INDIController, no need to send them
            return

        elif event.eventtype == "Delete":
            # Handled in INDIController, no need to send them
            return
        elif event.eventtype == "Busy":
            # Handled in INDIController, no need to send them
            return

        if payload:
            event_message=EventMessage(timestamp=event.timestamp, payload=payload)
            await self.send_event(event_message)

# TODO: IMPROVE CALLBACK !!

class INDIController:
    """
    Class to control an INDI client and server
    """

    def __init__(self, host="localhost", port=7624, context_provider=None, event_callback=None):
        self._client:INDIClient = INDIClient(host, port, context_provider, self.get_proxy_type, event_callback)
        
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
    
    async def get_proxy_type(self, device_name: str) -> INDIDeviceType | None:
        """
        Get the type of a device by its name, returns None if not found
        """
        try:
            if device_name=="indi":
                return None
            proxy = await self.get_proxy(device_name)
            return proxy.type
        except Exception as e:
            LOGGER.error(f"Error getting device type for {device_name}", details=e)
            return None

    async def get_telescope(self, telescope_name) -> Telescope:
        """Helper to get the first available telescope"""
        return await self.get_proxy(telescope_name)
    
        # TODO: PENDING IF DELETED



