// src/routes/(app)/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, url }) => {
    const auth = cookies.get('auth');
    
    if (!auth) {
        const locale = cookies.get('locale') ?? 'en';
        const goto = encodeURIComponent(url.pathname + url.search);
        redirect(302, `/${locale}/login?goto=${goto}`);
    }
};