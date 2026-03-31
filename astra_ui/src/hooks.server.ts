import { setLocale } from '$lib/paraglide/runtime.js';
import type { Handle } from '@sveltejs/kit';
import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

const SUPPORTED_LOCALES = AVAILABLE_LANGUAGES.map(l => l.code);


export const handle: Handle = async ({ event, resolve }) => {
    const urlLang = event.url.pathname.split('/')[1] as LanguageCode;
    let locale: LanguageCode;

    if (SUPPORTED_LOCALES.includes(urlLang)) {
        locale = urlLang;
    } else {
        // Use Paraglide's own cookie instead of ours
        const cookieLang = event.cookies.get('PARAGLIDE_LOCALE') as LanguageCode;
        locale = SUPPORTED_LOCALES.includes(cookieLang) ? cookieLang : 'en';
    }

    setLocale(locale);

    return resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });
};