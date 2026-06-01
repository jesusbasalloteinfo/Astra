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

// src/lib/config/languages.ts

import enSvg from '$lib/assets/flags/en.svg?raw';
import esSvg from '$lib/assets/flags/es.svg?raw';
import caSvg from '$lib/assets/flags/ca.svg?raw';


// Add here the available ones, but remember to also update paraglide config!
export const AVAILABLE_LANGUAGES = [
    { code: 'en', label: 'English', svg: enSvg },
    { code: 'ca', label: 'Català', svg: caSvg },
    { code: 'es', label: 'Español', svg: esSvg }
] as const;

// Type hints
export type LanguageCode = typeof AVAILABLE_LANGUAGES[number]['code'];