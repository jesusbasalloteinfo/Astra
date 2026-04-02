export interface Observation {
    id: string;
    name: string;
    description?: string;
    owner: string;
    creation: string;
    last_used: string;
}

export interface ObservationCreate {
    name: string;
    description?: string;
}

export interface ObservationUpdate {
    name?: string;
    description?: string;
}