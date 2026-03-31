// src/routes/(app)/+layout.ts
import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';
import type { LayoutLoad } from './$types';

import { getLocale } from '$lib/paraglide/runtime.js'; 

export const load: LayoutLoad = async ({ url }) => {
    if (browser) {
        const token = localStorage.getItem('token');
        
        if (!token) {
            const locale = getLocale(); 
            
            const gotoPath = encodeURIComponent(url.pathname + url.search);
            redirect(302, `/${locale}/login?goto=${gotoPath}`);
        }
    }
};