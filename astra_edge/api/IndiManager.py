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
INDI Client and Manager implementations for astra_edge.
"""
import asyncio
import re
from datetime import datetime
from indipyclient import IPyClient
from devices.INDIDeviceFactory import INDIDeviceFactory
from devices.INDIDevice import INDIDevice
from devices.INDITypes import INDIDeviceType
from utils.CoordinateHandler import CoordinateHandler, CoordinateTypes
from utils.logging import get_logger
from common.INDIModels import (
    EquatorialCoordModel, HorizontalCoordModel, CoordEventData, 
    CoordEvent, MessageEventData, MessageEvent, EventMessage
)

LOGGER = get_logger("IndiManager")

class IndiClient(IPyClient):
    """
    Custom INDI Client implementation that handles events and coordinate formatting.

    Extends IPyClient to provide specialized event processing, including 
    automatic coordinate transformation and log message parsing.
    """

    def __init__(self, host: str, port: int, context_provider: callable, device_type_provider: callable, send_event: callable):
        """
        Initializes the IndiClient.

        Args:
            host (str): INDI server hostname.
            port (int): INDI server port.
            context_provider (callable): Callback to get current location and time.
            device_type_provider (callable): Callback to get the type of a device.
            send_event (callable): Callback to emit events to the upper layers.
        """
        super().__init__(host=host, port=port)
        self.get_context = context_provider
        self.get_device_type = device_type_provider
        self.send_event = send_event

        # Parses lines starting with "[LEVEL] Message" format.
        # Group 1: Log Category | Group 2: Remaining message text
        self.message_regex = re.compile(r'^\[(INFO|WARNING|ERROR|DEBUG)\]\s*(.*)', re.IGNORECASE)
    
    def parse_message_level(self, raw_msg: str) -> tuple[str, str]:
        """
        Parses the level and message content from a raw INDI message.

        Args:
            raw_msg (str): The raw message string (e.g., "[INFO] Connected").

        Returns:
            tuple[str, str]: A tuple containing (level, content).
        """
        match = self.message_regex.match(raw_msg)
        if match:
            level = match.group(1).upper()
            clean_msg = match.group(2)
        else:
            level = "INFO"
            clean_msg = raw_msg
        return level, clean_msg

    def format_coordinates(self, event) -> CoordEvent:
        """
        Formats and converts INDI coordinate updates into a CoordEvent model.

        Args:
            event: The INDI 'Set' event containing coordinate data.

        Returns:
            CoordEvent: The formatted coordinate event containing multiple frames.
        """

        data = tuple(map(float, (event.vector.get("RA", "ALT"), event.vector.get("DEC", "AZ"))))
        time = event.timestamp
        location, _ = self.get_context()
        orig_type = CoordinateTypes.from_str(event.vectorname)

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
        Asynchronously processes an event received from the INDI server.

        Args:
            event: The INDI event object.
        """
        payload = None
        if event.eventtype == "Message":
            level, content = self.parse_message_level(event.message)
            data = MessageEventData(level=level, content=content)
            device = event.devicename if event.devicename else "indi"
            device_type_enum = await self.get_device_type(device)
            device_type = "indi" if not device_type_enum else device_type_enum.value

            payload = MessageEvent(device=device, device_type=device_type, data=data)

        elif event.eventtype == "Set":
            if event.vectorname in CoordinateTypes.list_values():
                # Coordinate UPDATE
                payload = self.format_coordinates(event)

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
            event_message = EventMessage(timestamp=event.timestamp, payload=payload)
            await self.send_event(event_message)

class IndiManager:
    """
    High-level manager for the INDI client and device lifecycle.

    Handles connection to the INDI server, discovery of devices, 
    and maintaining specialized device proxy objects.
    """

    def __init__(self, host="localhost", port=7624, context_provider=None, event_callback=None):
        """
        Initializes the IndiManager.

        Args:
            host (str): INDI server hostname.
            port (int): INDI server port.
            context_provider (callable): Callback to get current location and time.
            event_callback (callable): Callback for processed events.
        """
        self._client: IndiClient = IndiClient(host, port, context_provider, self.get_proxy_type, event_callback)
        
        self._devices_proxy: dict[str, INDIDevice] = {}
        self._client_task = None

    async def start(self):
        """
        Starts the asynchronous INDI client loop.
        """
        LOGGER.info(f"Starting INDI Client...")
        self._client_task = asyncio.create_task(self._client.asyncrun())
    
    async def stop(self):
        """
        Stops the INDI client and cleans up resources.
        """
        if self._client_task and not self._client_task.done():
            LOGGER.info("Stopping INDI Client...")
            
            self._client_task.cancel()
            
            try:
                # Wait for cleanup
                await self._client_task
            except asyncio.CancelledError:
                LOGGER.info("INDI Client task cancelled successfully.")

    async def _probe_device(self, device_name: str) -> INDIDevice:
        """
        Connects to a device temporarily to identify its type and properties.

        Args:
            device_name (str): The name of the device to probe.

        Returns:
            INDIDevice: A specialized device proxy instance.
        """
        # Create as generic
        temp_device: INDIDevice = INDIDevice(self._client, device_name)

        try:
            proxy = await INDIDeviceFactory.create(self._client, device_name)
        except Exception as e:
            LOGGER.error(f"Error creating proxy for {device_name}: {e}")
            proxy = temp_device
        
        return proxy

    async def _sync_proxies(self):
        """
        Synchronizes device proxies with the current INDI client state.

        Discovers new devices and removes disconnected ones.
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
        
        # Check existing Generic devices
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

    async def _get_proxy(self, device_name: str) -> INDIDevice:
        """
        Retrieves a device proxy by name.

        Args:
            device_name (str): The device name.

        Returns:
            INDIDevice: The device proxy instance.

        Raises:
            ValueError: If the device is not found.
        """
        await self._sync_proxies()
        if device_name not in self._devices_proxy:
            raise ValueError(f"Device {device_name} not found!")
        return self._devices_proxy.get(device_name)
    
    async def get_proxy_type(self, device_name: str) -> INDIDeviceType | None:
        """
        Gets the type of a device by its name.

        Args:
            device_name (str): The device name.

        Returns:
            INDIDeviceType | None: The device type enum member, or None if not found/indi.
        """
        try:
            if device_name == "indi":
                return None
            proxy = await self._get_proxy(device_name)
            return proxy.type
        except Exception as e:
            LOGGER.error(f"Error getting device type for {device_name}", details=e)
            return None


    async def get_devices(self) -> dict[str, list[str]]:
        """
        Gets a dictionary of connected devices grouped by their type.

        Returns:
            dict[str, list[str]]: Map of device types to lists of device names.
        """
        await self._sync_proxies()

        # Device types dict
        ret = {category.value: [] for category in INDIDeviceType}
        
        for proxy in self._devices_proxy.values():
            category_key = proxy.type.value           
            ret[category_key].append(proxy.name)

        return ret
        
    async def connect_device(self, device_name: str) -> INDIDevice:
        """
        Connects the specified device.

        Args:
            device_name (str): The device name.

        Returns:
            INDIDevice: The connected device proxy instance.
        """
        device = await self._get_proxy(device_name)
        await device.connect()
        return device

    async def disconnect_device(self, device_name: str):
        """
        Disconnects the specified device.

        Args:
            device_name (str): The device name.
        """
        device = await self._get_proxy(device_name)
        await device.disconnect()
