import asyncio

from devices.INDITypes import *
from devices.INDIDevice import *
from devices.Telescope import Telescope
from devices.Camera import Camera
from utils.logging import get_logger

LOGGER=get_logger("INDIDeviceFactory")

class INDIDeviceFactory:
    """
    Factory Pattern to create instances of the INDI devices.
    Includes logic to probe and identify devices.
    """

    @staticmethod
    def identify(client: IPyClient, device_name: str) -> INDIDevice:
        """
        Analize the device and create the specific device proxy
        """

        device_data = client[device_name]
                
        # - - - Fingerprinting logic - - -
        
        # Telescope
        target_keys = {"EQUATORIAL_EOD_COORD", "EQUATORIAL_COORD", "HORIZONTAL_COORD", "TELESCOPE_MOTION_NS", "TELESCOPE_PARK"}
        if not target_keys.isdisjoint(device_data.keys()):
            return Telescope(client, device_name)
            
        # Camera
        elif "CCD_EXPOSURE" in device_data:
            return Camera(client, device_name)
            
        # Focuser
        elif "ABS_FOCUS_POSITION" in device_data:
            # return Focuser(client, device_name)
            pass

        # Filter Wheel
        if "FILTER_SLOT" in device_data:
            # return FilterWheel(client, device_name)
            pass
            
        # Fallback
        return INDIDevice(client, device_name)


    @staticmethod
    async def create(client:IPyClient, device_name: str) -> INDIDevice:
        """
        Analize the device and create the specific device proxy, awaiting the key values
        """
        # Create as generic
        temp_device:INDIDevice= INDIDevice(client, device_name)
        was_connected=temp_device.is_connected()

        if not was_connected:
            LOGGER.debug(f"Connecting {device_name}...")
            await temp_device.connect()
        
        proxy = None
        
        async def wait_for_identity():
            while True:
                candidate = INDIDeviceFactory.identify(client, device_name)
                
                # Candidate identified
                if candidate.type != INDIDeviceType.GENERIC:
                    return candidate
                
                # Await if not identified
                await asyncio.sleep(0.2)

        try:
            proxy = await asyncio.wait_for(wait_for_identity(), timeout=5.0)
            
        except asyncio.TimeoutError:
            proxy = INDIDeviceFactory.identify(client, device_name)
            LOGGER.debug(f"⚠️ Timeout: {device_name} couldn't send the properties")

        if not was_connected:
            await temp_device.disconnect()
            await asyncio.sleep(0.2) 
        
        return proxy

