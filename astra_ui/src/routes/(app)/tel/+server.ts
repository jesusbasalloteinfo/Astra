/*
 * ASTRA - Automated Smart Telescope Remote Assistant
 * Copyright (C) 2026 Jesus Basallote
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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