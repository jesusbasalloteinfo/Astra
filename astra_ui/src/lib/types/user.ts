export interface UserLocation {
    id: string;
    label: string;
    lat: number;     
    lng: number;     
    elevation: number;
    timezone: number; 
    is_default: boolean;
}

export interface LocationCreate {
    label: string;
    lat: number;     
    lng: number;     
    elevation: number;
    timezone: number; 
    is_default: boolean;
}

export interface User {
    username: string;
    locations: UserLocation[];
    creation: string;
}
