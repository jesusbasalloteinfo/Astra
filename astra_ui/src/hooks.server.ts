import { setLocale } from '$lib/paraglide/runtime.js';
import type { Handle } from '@sveltejs/kit';

// Definimos los idiomas como una constante inmutable para tener Type Safety
const SUPPORTED_LOCALES = ['en', 'es'] as const;
type Locale = typeof SUPPORTED_LOCALES[number];

export const handle: Handle = async ({ event, resolve }) => {
    const urlLang = event.url.pathname.split('/')[1] as Locale;
    let locale: Locale;

    if (SUPPORTED_LOCALES.includes(urlLang)) {
        // ESCENARIO A: Landing Page (Ej. /es/pricing)
        locale = urlLang;
        // Guardamos la cookie de forma segura
        event.cookies.set('locale', locale, { 
            path: '/', 
            maxAge: 31536000, 
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production' // Solo HTTPS en prod
        });
    } else {
        // ESCENARIO B: SaaS Privado (Ej. /dashboard)
        const cookieLang = event.cookies.get('locale') as Locale;
        // Validación crítica: asegurarnos de que la cookie no ha sido manipulada
        locale = SUPPORTED_LOCALES.includes(cookieLang) ? cookieLang : 'en';
    }

    // Le pasamos el idioma resuelto a Paraglide
    setLocale(locale);

    return resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });
};