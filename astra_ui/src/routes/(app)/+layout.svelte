<!-- src/routes/(app)/+layout.svelte -->
<script lang="ts">
    import { authStore } from '$lib/stores/auth.svelte';
    import { obsStore } from '$lib/stores/observations.svelte';
    import { onMount } from 'svelte';
    import { fade } from 'svelte/transition';
    import SplashScreen from '$lib/components/SplashScreen.svelte';
	import NewSessionModal from '$lib/components/session/newSessionModal.svelte';

    let { children } = $props();

    let isAppReady = $state(false);

    onMount(async () => {
        const delay = new Promise(resolve => setTimeout(resolve, 2000)); // 2s

        try {
            await authStore.init();
            if (authStore.isAuthenticated) {
                await obsStore.load();
            }
        } catch (e) {
            console.error("Loading error:", e);
        } finally {
            // Await delay if api was faster
            await delay;
            isAppReady = true;
        }
    });

</script>

{#if !isAppReady}
    <div 
        out:fade={{ duration: 800 }} 
        class="fixed inset-0 z-9999"
    >
        <SplashScreen />
    </div>
{:else}
    {@render children()}
    <NewSessionModal />
{/if}