export const endpoints = {
    apiBase: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
    auth: {
        login:   '/login',
        logout:  '/logout',
        session: '/session',
        user_details: 'users/me'
    },
    user:{
        locations: 'users/me/locations',
        location_get: (id: string) => `users/me/locations/${id}`,
    },
    observations: {
        base:   '/observations',
        detail: (id: string) => `/observations/${id}`,
    },
    chat: {
        session: (observation_id: string) => `/chat/session/${observation_id}`,
        stream: (session_id: string) => `/chat/stream/${session_id}`,
    },
    devices:{
        pairDevice: 'devices/pair',
        getDevices: 'devices',
        getDeviceInfo: (id: string) => `devices/${id}`,
        getTelescopePos: (id: string) => `devices/${id}/telescope/position`,
        slewTelescope: (id: string) => `devices/${id}/telescope/slew`,
        abortTelescope: (id: string) => `devices/${id}/telescope/abort`,
    }
} as const;



export const siderisEndpoints = {
    base: '/sideris',
    sidereal: {
        sync: '/sideris/sidereal/sync',
        constellations: '/sideris/sidereal/constellations',
        metadata: '/sideris/sidereal/metadata',
        object: (id: string) => `/sideris/sidereal/${id}`
    },
    planetary: {
        sync: '/sideris/planetary/sync',
        metadata: '/sideris/planetary/metadata',
        object: (id: string) => `/sideris/planetary/${id}`
    }
} as const;