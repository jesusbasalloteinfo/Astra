// lib/api/devices.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { Device, DeviceInfo, PairingRequest, PairingResponse, TelescopePosition} from '$lib/types/devices';

export const deviceAPI = {
    pairDevice: async (data: PairingRequest): Promise<PairingResponse> =>{
        const response = await api.post<PairingResponse>(endpoints.devices.pairDevice, data);  
        return response.data
    },
    getDevices: async (): Promise<Device[]> => {
        const response = await api.get<Device[]>(endpoints.devices.getDevices);  
        return response.data
    },
    getDeviceInfo: async (id: string): Promise<DeviceInfo> => {
        const response = await api.get<DeviceInfo>(endpoints.devices.getDeviceInfo(id));  
        return response.data
    },
    updateDevice: async (id: string, data: { name: string }): Promise<{success: boolean}> => {
        const response = await api.patch(endpoints.devices.getDeviceInfo(id), data);  
        return response.data;
    },
    deleteDevice: async (id: string): Promise<void> => {
        await api.delete(endpoints.devices.getDeviceInfo(id));  
    },
    getTelescopePos: async (id:string, telescope:string): Promise<TelescopePosition> => {
        const response = await api.get<TelescopePosition>(endpoints.devices.getTelescopePos(id), { params: { telescope } });  
        return response.data
    }
};
