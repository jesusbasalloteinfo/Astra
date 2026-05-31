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
