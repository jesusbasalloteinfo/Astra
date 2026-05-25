<!-- src/routes/(app)/observation/[id]/+layout.svelte -->
<script lang="ts">
    import { page } from '$app/state';
    import { activeObs } from '$lib/stores/activeObservation.svelte';
    import { CircleAlert, LoaderCircle } from 'lucide-svelte';
    import { catalogStore } from '$lib/stores/skyCatalog.svelte';
    import { skyEngine } from '$lib/stores/skyEngine.svelte';
    import { timeEngine } from '$lib/stores/timeEngine.svelte';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { locStore } from '$lib/stores/location.svelte';
    import { authStore } from '$lib/stores/auth.svelte';
    import { goto } from '$app/navigation';
	import { m } from '$lib/paraglide/messages';

    let { children } = $props();

    $effect(() => {
        if (authStore.isLoading) return;

        if (locStore.all.length === 0) {
            goto('/dashboard/sessions');
            return;
        }

        const id = page.params.id;
        if (id) {
            catalogStore.isRunning = true;
            skyEngine.isRunning = true;
            activeObs.setSession(id);
        }
        return () => {
            console.log("Shutting down engines...");
            catalogStore.isRunning = false;
            skyEngine.isRunning = false;
            timeEngine.setLive(true);
            skyEngine.reset();
            catalogStore.reset();
            selectionStore.clear();
            activeObs.clear();
        };
    });
</script>

{#if activeObs.isLoading}
    <!-- Loading stores -->
    <div class="fixed inset-0 bg-secondary z-50 flex items-center justify-center p-6">
        <div class="w-full max-w-md p-12 bg-panel border border-border rounded-3xl text-center relative overflow-hidden">
            <div class="absolute -top-24 -left-24 w-48 h-48 bg-accent/10 blur-3xl rounded-full"></div>
            
            <div class="relative z-10">
                <div class="w-16 h-16 bg-accent/10 text-accent rounded-full flex items-center justify-center mx-auto mb-6">
                    <LoaderCircle class="animate-spin" size={32} />
                </div>
                <h2 class="text-xl font-bold text-copy-primary tracking-tight">
                    {m.obs_load_title()}
                </h2>
                <p class="text-sm text-copy-muted mt-2 mb-6 font-mono uppercase tracking-widest text-[10px]">
                    {m.obs_load_subtitle()}
                </p>
                <div class="w-full bg-border/30 h-1 rounded-full overflow-hidden">
                    <div class="bg-accent h-full animate-progress-loading w-1/3"></div>
                </div>
            </div>
        </div>
    </div>

{:else if activeObs.error}
    <!-- Error detected -->
    <div class="fixed inset-0 bg-secondary z-50 flex items-center justify-center p-6">
        <div class="w-full max-w-lg p-12 bg-panel border border-border rounded-3xl text-center">
            <div class="w-16 h-16 bg-danger/10 text-danger rounded-full flex items-center justify-center mx-auto mb-4">
                <CircleAlert size={32} />
            </div>
            <h2 class="text-xl font-bold text-copy-primary uppercase font-mono">{m.obs_error_load_title() }</h2>
            <p class="text-sm text-copy-muted max-w-sm mx-auto mt-2 mb-8">
                {activeObs.error || 'The requested observation is not available.'}
            </p>
            <a 
                href="/dashboard/sessions" 
                class="inline-flex items-center gap-2 px-6 py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-bold transition-all shadow-lg shadow-accent/20"
            >
                {m.obs_error_load_btn()}
            </a>
        </div>
    </div>

{:else if activeObs.current}
    {@render children()}
{/if}

<style>
    @keyframes progress-loading {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(300%); }
    }
    .animate-progress-loading {
        animation: progress-loading 1.5s infinite linear;
    }
</style>