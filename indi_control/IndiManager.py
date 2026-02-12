import asyncio
from datetime import datetime
from indipyclient import IPyClient
from devices.INDIDeviceFactory import *
from utils.CoordinateHandler import CoordinateHandler, CoordinateTypes
from utils.logging import get_logger
from common.INDIModels import *

import re

LOGGER=get_logger("IndiManager")

class IndiClient(IPyClient):
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

        conversions = {}
        
        # Map of types and Pydantic models
        models = {
            CoordinateTypes.EQUATORIAL_J2000: EquatorialCoordModel,
            CoordinateTypes.EQUATORIAL_EOD: EquatorialCoordModel,
            CoordinateTypes.HORIZONTAL: HorizontalCoordModel
        }

        for convert_type, model_class in models.items():
            converted = CoordinateHandler.convert_coord(
                time, data, location, convert_from=orig_type, convert_to=convert_type
            )
            # Builds the objects with the properties names
            props = dict(zip(convert_type.get_properties(), converted))
            conversions[convert_type.value] = model_class(**props)

        # Final object
        data_event = CoordEventData(
            equatorial_j2000=conversions[CoordinateTypes.EQUATORIAL_J2000.value],
            equatorial_eod=conversions[CoordinateTypes.EQUATORIAL_EOD.value],
            horizontal=conversions[CoordinateTypes.HORIZONTAL.value]
        )
        
        return CoordEvent(device=event.devicename, data=data_event)

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
            device_type="indi" if not device_type or device_type else device_type.value

            payload=MessageEvent(device=device, device_type=device_type, data=data)

        elif event.eventtype == "Set":
            if event.vectorname in CoordinateTypes.list_values():
                # Coordinate UPDATE
                payload=self.format_coordinates(event)

        elif event.eventtype == "Define":
            # Handled in IndiManager, no need to send them
            return

        elif event.eventtype == "Delete":
            # Handled in IndiManager, no need to send them
            return
        elif event.eventtype == "Busy":
            # Handled in IndiManager, no need to send them
            return

        if payload:
            event_message=EventMessage(timestamp=event.timestamp, payload=payload)
            await self.send_event(event_message)

class IndiManager:
    """
    Class to manage an INDI client and server
    """

    def __init__(self, host="localhost", port=7624, context_provider=None, event_callback=None):
        self._client:IndiClient = IndiClient(host, port, context_provider, self.get_proxy_type, event_callback)
        
        self._devices_proxy:dict[INDIDevice] = {}
        self._client_task = None

    async def start(self):
        """Start the async loop of the client"""
        LOGGER.info(f"Starting INDI Client...")
        self._client_task = asyncio.create_task(self._client.asyncrun())
        # return asyncio.create_task(self._client.asyncrun())
    
    async def stop(self):
        """Stop the INDI client"""
        if self._client_task and not self._client_task.done():
            LOGGER.info("Stopping INDI Client...")
            
            self._client_task.cancel()
            
            try:
                # Wait for cleanup
                await self._client_task
            except asyncio.CancelledError:
                LOGGER.info("INDI Client task cancelled successfully.")
        
        # Opcional: Si tu clase IPyClient tiene un método disconnect() explícito, llámalo aquí
        # if hasattr(self._client, 'disconnect'):
        #     self._client.disconnect()
    
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



