// lib/api/devices.ts
import { api } from './client';
import { endpoints } from './endpoints';
import type { Device, DeviceInfo, PairingRequest, PairingResponse } from '$lib/types/devices';

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
    }
};
