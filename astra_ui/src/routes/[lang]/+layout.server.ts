import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

const SUPPORTED_LOCALES = ['en', 'es'];

export const load: LayoutServerLoad = ({ params }) => {
    if (!SUPPORTED_LOCALES.includes(params.lang)) {
        redirect(302, '/en');
    }
};