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
