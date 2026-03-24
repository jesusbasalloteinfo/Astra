import { setLocale } from '$lib/paraglide/runtime.js';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const locale = event.cookies.get('locale') ?? 'en';
    setLocale(locale as 'en' | 'es');

    return resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });
};