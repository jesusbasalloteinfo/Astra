// src/routes/+page.server.ts
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ cookies }) => {
    const locale = cookies.get('locale') ?? 'en';
    redirect(302, `/${locale}`);
};