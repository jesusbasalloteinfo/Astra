<!-- src/routes/(app)/dashboard/+layout.svelte -->
<script lang="ts">
    import Sidebar from '$lib/components/dashboard/Sidebar.svelte';
    import { fade } from 'svelte/transition';
    import { page } from '$app/state'; 
    let { children } = $props();
</script>

<div class="min-h-screen flex bg-primary text-copy-primary">
    <Sidebar />
    <main class="flex-1 min-w-0 p-8">
        {#key page.url.pathname}
            <div in:fade={{ duration: 300, delay: 50 }}>
                {@render children()}
            </div>
        {/key}
    </main>
</div>