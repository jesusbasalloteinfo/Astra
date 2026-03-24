import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, cookies }) => {
    const { locale } = await request.json();
    const supported = ['en', 'es'];
    
    // Solo configuramos la cookie si el idioma es válido
    if (supported.includes(locale)) {
        cookies.set('locale', locale, { 
            path: '/', 
            maxAge: 31536000, 
            httpOnly: false, // Falso para que Paraglide u otros scripts puedan leerla si es necesario
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production'
        });
    }
    
    return json({ success: true });
};