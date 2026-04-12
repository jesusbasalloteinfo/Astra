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