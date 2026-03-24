import { setLocale } from '$lib/paraglide/runtime.js';
import type { Handle } from '@sveltejs/kit';

const SUPPORTED_LOCALES = ['en', 'es'] as const;
type Locale = typeof SUPPORTED_LOCALES[number];

export const handle: Handle = async ({ event, resolve }) => {
    const urlLang = event.url.pathname.split('/')[1] as Locale;
    let locale: Locale;

    if (SUPPORTED_LOCALES.includes(urlLang)) {
        locale = urlLang;
    } else {
        // Use Paraglide's own cookie instead of ours
        const cookieLang = event.cookies.get('PARAGLIDE_LOCALE') as Locale;
        locale = SUPPORTED_LOCALES.includes(cookieLang) ? cookieLang : 'en';
    }

    setLocale(locale);

    return resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });
};