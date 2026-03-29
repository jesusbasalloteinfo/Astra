// src/params/lang.ts
import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

// Check if is a language
export function match(param: string): boolean {
    const validLocales = AVAILABLE_LANGUAGES.map(l => l.code);
    return validLocales.includes(param as LanguageCode);
}