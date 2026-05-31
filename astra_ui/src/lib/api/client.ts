// lib/api/client.ts
import axios from 'axios';
import { goto } from '$app/navigation';
import { endpoints } from './endpoints';
import { browser } from '$app/environment'; 

/**
 * Axios instance configured for the Astra API.
 * Includes base URL, common headers, and fetch adapter.
 */
export const api = axios.create({
    baseURL: endpoints.apiBase,
    headers: { 'Content-Type': 'application/json' },
    adapter: 'fetch'
});


/**
 * Redirects the user to the login page while preserving the current route for post-login redirection.
 * Handles locale-prefixed routes automatically.
 * @returns {void}
 */
const redirectToLogin = () => {
    if (!browser) return; // Avoid Node.js execution
    
    const path = window.location.pathname;
    const segments = path.split('/');
    // Simple check: if first segment is a locale (en, es, ca)
    const locale = ['en', 'es', 'ca'].includes(segments[1]) ? segments[1] : '';
    const loginPath = locale ? `/${locale}/login` : '/login';

    const redirect = encodeURIComponent(path + window.location.search);
    
    // Prevent redirecting if we are already at the login page
    if (path.includes('/login')) return;

    goto(`${loginPath}?goto=${redirect}`);
};

api.interceptors.request.use((config) => {
    if (browser) {
        const token = localStorage.getItem('auth');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

// Response interceptor 
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || '';
        const isAuthRequest = url.includes(endpoints.auth.login) || url.includes(endpoints.auth.register);
        const isLogout = url.includes(endpoints.auth.logout);

        if (error.response?.status === 401 && !isAuthRequest && !isLogout) {
            redirectToLogin();
        } else if (error.response?.status === 403 && !isAuthRequest) {
            redirectToLogin();
        }

        return Promise.reject(error);
    }
);