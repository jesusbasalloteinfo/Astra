// src/routes/tel/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, event }) => {
    try {
        const userIP = request.headers.get('x-forwarded-for') || 
                       request.headers.get('x-real-ip') || 
                       event?.getClientAddress?.() || 'UNKNOWN_IP';

        const { path, action } = await request.json();

        console.log(`[${new Date().toISOString()}] IP: ${userIP} -> ${path} (${action || 'CLICK_LINK'})`);

        return json({ success: true });
    } catch (e) {
        return json({ success: false }, { status: 500 });
    }
};