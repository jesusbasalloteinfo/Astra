import { setLocale, extractLocaleFromHeader } from '$lib/paraglide/runtime.js';
import type { Handle } from '@sveltejs/kit';
import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

const SUPPORTED_LOCALES = AVAILABLE_LANGUAGES.map(l => l.code);


export const handle: Handle = async ({ event, resolve }) => {
    const urlLang = event.url.pathname.split('/')[1] as LanguageCode;
    let locale: LanguageCode;
    
    // Logging
    const userIP = event.request.headers.get('x-forwarded-for') || 
        event.request.headers.get('x-real-ip') ||
        event.getClientAddress();
    const method = event.request.method;
    const path = event.url.pathname;

    console.log(`[${new Date().toISOString()}] IP: ${userIP} -> ${method} ${path}`);

    if (SUPPORTED_LOCALES.includes(urlLang)) {
        locale = urlLang;
    } else {
        const cookieLang = event.cookies.get('PARAGLIDE_LOCALE') as LanguageCode;
        if (SUPPORTED_LOCALES.includes(cookieLang)) {
            locale = cookieLang;
        } else {
            // Detect from Accept-Language header using Paraglide's built-in utility
            locale = extractLocaleFromHeader(event.request) || 'en';
        }
    }

    setLocale(locale);

    const response = await resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });

    // Sync the cookie with the resolved locale for future non-localized requests
    response.headers.append('set-cookie', event.cookies.serialize('PARAGLIDE_LOCALE', locale, {
        path: '/',
        maxAge: 31536000, // 1 year
        httpOnly: false, // Allow client-side access
        sameSite: 'lax'
    }));


    console.log(`[${new Date().toISOString()}] IP: ${userIP} <- ${response.status}`);

    return response;
};