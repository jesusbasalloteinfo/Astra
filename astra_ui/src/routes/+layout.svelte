<!--
  ASTRA - Automated Smart Telescope Remote Assistant
  Copyright (C) 2026 Jesus Basallote
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
  
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script lang="ts">
	import './layout.css';
	import { onNavigate } from '$app/navigation';
	import { page } from '$app/state';

	let { children } = $props();

	onNavigate((navigation) => {
		if (!document.startViewTransition) return;

		const from = navigation.from?.url.pathname ?? '';
		const to = navigation.to?.url.pathname ?? '';

		// Exclude dashboard and observations
		const isInsideDashboard = from.includes('/dashboard') && to.includes('/dashboard');
		const isObservation = from.includes('/observation') || to.includes('/observation');
		if (isInsideDashboard || isObservation) {
			return;
		}

		// Apply only to landing and login/register
		const isLandingOrLoginNav = (from.includes('/login') || to.includes('/login') || from === '/' || to === '/' || /^\/[a-z]{2}(\/)?$/.test(from) || /^\/[a-z]{2}(\/)?$/.test(to));
		if (!isLandingOrLoginNav) {
			return;
		}

		return new Promise((resolve) => {
			document.startViewTransition(async () => {
				resolve();
				await navigation.complete;
			});
		});
	});

	$effect(() => {
        const currentPath = page.url.pathname;
        
        if (currentPath.startsWith('/tel')) return;

        fetch('/tel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                path: currentPath,
                action: 'SPA_NAVIGATION' 
            })
        }).catch(() => {});
    });
</script>

{@render children()}
