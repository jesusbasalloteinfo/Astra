export const endpoints = {
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