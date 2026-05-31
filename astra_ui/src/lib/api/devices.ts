// lib/api/devices.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { Device, DeviceInfo, PairingRequest, PairingResponse, TelescopePosition, SlewCommand} from '$lib/types/devices';

/**
 * Device API module for managing astronomical hardware devices and telescope control.
 */
export const deviceAPI = {
    /**
     * Pairs a new device with the user's account.
     * @param {PairingRequest} data - The pairing request data.
     * @returns {Promise<PairingResponse>} The result of the pairing operation.
     */
    pairDevice: async (data: PairingRequest): Promise<PairingResponse> =>{
        const response = await api.post<PairingResponse>(endpoints.devices.pairDevice, data);  
        return response.data
    },

    /**
     * Retrieves a list of all devices associated with the user.
     * @returns {Promise<Device[]>} A list of devices.
     */
    getDevices: async (): Promise<Device[]> => {
        const response = await api.get<Device[]>(endpoints.devices.getDevices);  
        return response.data
    },

    /**
     * Retrieves detailed information about a specific device.
     * @param {string} id - The unique identifier of the device.
     * @returns {Promise<DeviceInfo>} Detailed device information.
     */
    getDeviceInfo: async (id: string): Promise<DeviceInfo> => {
        const response = await api.get<DeviceInfo>(endpoints.devices.getDeviceInfo(id));  
        return response.data
    },

    /**
     * Updates a device's information.
     * @param {string} id - The unique identifier of the device.
     * @param {Object} data - The data to update.
     * @param {string} data.name - The new name for the device.
     * @returns {Promise<{success: boolean}>} Whether the update was successful.
     */
    updateDevice: async (id: string, data: { name: string }): Promise<{success: boolean}> => {
        const response = await api.patch(endpoints.devices.getDeviceInfo(id), data);  
        return response.data;
    },

    /**
     * Deletes a device from the user's account.
     * @param {string} id - The unique identifier of the device to delete.
     * @returns {Promise<void>}
     */
    deleteDevice: async (id: string): Promise<void> => {
        await api.delete(endpoints.devices.getDeviceInfo(id));  
    },

    /**
     * Retrieves the current coordinates (RA/Dec) of a telescope.
     * @param {string} id - The unique identifier of the device.
     * @param {string} telescope - The name of the telescope driver.
     * @returns {Promise<TelescopePosition>} The current telescope position.
     */
    getTelescopePos: async (id:string, telescope:string): Promise<TelescopePosition> => {
        const response = await api.get<TelescopePosition>(endpoints.devices.getTelescopePos(id), { params: { telescope } });  
        return response.data
    },

    /**
     * Commands the telescope to slew to specific coordinates.
     * @param {string} id - The unique identifier of the device.
     * @param {string} telescope - The name of the telescope driver.
     * @param {SlewCommand} data - The target coordinates for the slew operation.
     * @returns {Promise<void>}
     */
    slewTelescope: async (id: string, telescope: string, data: SlewCommand): Promise<void> => {
        await api.post(endpoints.devices.slewTelescope(id),
            data,
            { 
                params: { telescope }, 
                timeout: 1000 * 1000, 
            }
        );
    },

    /**
     * Aborts the current telescope motion.
     * @param {string} id - The unique identifier of the device.
     * @param {string} telescope - The name of the telescope driver.
     * @returns {Promise<void>}
     */
    abortTelescope: async (id: string, telescope: string): Promise<void> => {
        await api.post(endpoints.devices.abortTelescope(id), null, { 
            params: { telescope } 
        });
    }
};
