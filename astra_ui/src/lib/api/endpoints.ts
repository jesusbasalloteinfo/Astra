export const endpoints = {
    auth: {
        login:   '/login',
        logout:  '/logout',
        session: '/session',
        user_details: 'users/me'
    },
    observations: {
        base:   '/observations',
        detail: (id: string) => `/observations/${id}`,
    }
} as const;