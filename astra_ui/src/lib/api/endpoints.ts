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