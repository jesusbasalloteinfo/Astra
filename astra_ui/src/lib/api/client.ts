// lib/api/client.ts
import axios from 'axios';
import { goto } from '$app/navigation';
import { endpoints } from './endpoints';
import { browser } from '$app/environment'; 

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
    headers: { 'Content-Type': 'application/json' },
});


// Redirects to /login saving the destination route as ?goto=
const redirectToLogin = () => {
    if (!browser) return; // Avoid Node.js execution
    const redirect = encodeURIComponent(window.location.pathname + window.location.search);
    goto(`/login?goto=${redirect}`);
};

api.interceptors.request.use((config) => {
    if (browser) {
        const token = localStorage.getItem('token');
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
        const isLogout = error.config?.url?.includes(endpoints.auth.logout);

        if (error.response?.status === 401 && !isLogout) {
            redirectToLogin();
        } else if (error.response?.status === 403) {
            redirectToLogin();
        }

        return Promise.reject(error);
    }
);