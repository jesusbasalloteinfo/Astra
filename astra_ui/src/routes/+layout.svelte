<script lang="ts">
	import './layout.css';

	import { page } from '$app/state';
	let { children } = $props();

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
