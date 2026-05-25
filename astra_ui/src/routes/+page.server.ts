// src/routes/+page.server.ts
import { redirect } from '@sveltejs/kit';
import { getLocale } from '$lib/paraglide/runtime.js';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
    // getLocale() already has the detected language from hooks.server.ts
    const locale = getLocale();
    redirect(302, `/${locale}`);
};