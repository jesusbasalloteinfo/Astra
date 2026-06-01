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

import { getLocale } from '$lib/paraglide/runtime';

/**
 * Formats a date string or Date object into a localized string.
 * 
 * @param date - The date to format (string or Date object).
 * @param options - Intl.DateTimeFormatOptions to customize the output.
 * @returns A localized date string.
 */
export function formatDate(date: string | Date, options: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
}) {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(getLocale(), options).format(d);
}


/**
 * Formats a date into a localized string (currently a wrapper around formatDate).
 * 
 * @param date - The date to format (string or Date object).
 * @returns A localized date string.
 */
export function formatRelative(date: string | Date) {
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    
    return formatDate(d);
}
