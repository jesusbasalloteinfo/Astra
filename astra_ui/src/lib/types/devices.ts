export interface DeviceAccess {
    user_id: string;
    role: "owner" | "guest";
}

export interface Device {
    device_id: string;
    device_token: string;
    name: string;
    owner: string;
    linked: string; 
    access_list: DeviceAccess[];
}

export interface DeviceComponents {
    telescope: string[];
    camera: string[];
    focuser: string[];
    filter_wheel: string[];
    indi: string[];
}

export interface DeviceInfo extends Device {
    components: DeviceComponents;
}

export interface PairingRequest{
    pin: string
}

export interface PairingResponse{
    device_id: string
}

