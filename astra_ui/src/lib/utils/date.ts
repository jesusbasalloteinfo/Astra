import { getLocale } from '$lib/paraglide/runtime';

export function formatDate(date: string | Date, options: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
}) {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(getLocale(), options).format(d);
}


export function formatRelative(date: string | Date) {
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    
    return formatDate(d);
}