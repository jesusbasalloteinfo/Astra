export interface DeviceAccess {
    user_id: string;
    role: "owner" | "guest";
}

export interface Device {
    device_id: string;
    name: string;
    owner: string;
    linked: string; 
    is_online: boolean;
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



// OPERATIONS

interface Coordinates {
  ra: number;
  dec: number;
}

interface HorizontalCoordinates {
  alt: number;
  az: number;
}

export interface TelescopePosition {
  equatorial_j2000: Coordinates;
  equatorial_eod: Coordinates;
  horizontal: HorizontalCoordinates;
}


export enum CoordinateTypes {
    EQUATORIAL_J2000 = "EQUATORIAL_COORD",
    EQUATORIAL_EOD = "EQUATORIAL_EOD_COORD",
    HORIZONTAL = "HORIZONTAL_COORD"
}

export type SlewMode = "SLEW" | "TRACK" | "SYNC";

export interface SlewCommand {
    coord: [number, number]; 
    input_type: CoordinateTypes;
    mode: SlewMode;
}