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

import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { baseLocale } from '$lib/paraglide/runtime.js';
import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

const SUPPORTED_LOCALES = AVAILABLE_LANGUAGES.map(l => l.code);

export const load: LayoutServerLoad = ({ params }) => {
    if (!SUPPORTED_LOCALES.includes(params.lang as LanguageCode)) {
        redirect(302, `/${baseLocale}`);
    }

    return {
        starSeed: Math.random()
    };
};
