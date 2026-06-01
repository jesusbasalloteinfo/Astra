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

// src/routes/(app)/+layout.ts
import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';
import type { LayoutLoad } from './$types';

import { getLocale } from '$lib/paraglide/runtime.js'; 

export const load: LayoutLoad = async ({ url }) => {
    if (browser) {
        const token = localStorage.getItem('auth');
        
        if (!token) {
            const locale = getLocale(); 
            
            const gotoPath = encodeURIComponent(url.pathname + url.search);
            redirect(302, `/${locale}/login?goto=${gotoPath}`);
        }
    }
};