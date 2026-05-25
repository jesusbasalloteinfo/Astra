<!-- src/routes/(app)/dashboard/sessions/+page.svelte -->
<script lang="ts">
    import SessionCard from '$lib/components/session/SessionCard.svelte';
    import { Plus } from 'lucide-svelte';
    import { obsStore } from '$lib/stores/observations.svelte';
    import * as m from '$lib/paraglide/messages.js';
	import { newObsStore } from '$lib/stores/newObservation.svelte';
    import { locStore } from '$lib/stores/location.svelte';
    import { authStore } from '$lib/stores/auth.svelte';
    import { MapPin, CircleAlert } from 'lucide-svelte';

    const hasLocation = $derived(locStore.all.length > 0);
    const isReady = $derived(!authStore.isLoading);
</script>

<div class="max-w-3xl mx-auto p-6">

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
        <div>
            <h1 class="text-2xl font-bold text-copy-primary">{m.dash_observ_title()}</h1>
            <p class="text-sm text-copy-muted mt-1">
                {m.dash_observ_found({count: obsStore.count})}
            </p>
        </div>
        
        <button
            onclick={() => (hasLocation && isReady) ? newObsStore.open() : null}
            disabled={!hasLocation || !isReady}
            class="flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all shadow-lg
                {(hasLocation && isReady)
                    ? 'bg-accent hover:bg-accent-hover text-white shadow-accent/20' 
                    : 'bg-border text-copy-muted cursor-not-allowed shadow-none'}">
            <Plus size={15} />
            {m.dash_observ_new_session()}
        </button>
    </div>

    {#if isReady && !hasLocation}
        <div class="mb-6 p-4 bg-danger-surface border border-danger/20 rounded-2xl flex items-start gap-4">
            <div class="p-2 bg-danger/10 rounded-xl text-danger">
                <CircleAlert size={20} />
            </div>
            <div>
                <h3 class="text-sm font-bold text-danger uppercase tracking-wider font-mono">
                    {m.dash_observ_no_location_title()}
                </h3>
                <p class="text-sm text-copy-muted mt-1">
                    {m.dash_observ_no_location_desc()}
                </p>
            </div>
        </div>
    {/if}

    <div class="flex flex-col gap-3">
        {#if obsStore.isLoading && obsStore.count === 0}
            {#each Array(3) as _}
                <div class="h-20 w-full bg-panel/50 animate-pulse rounded-xl border border-border"></div>
            {/each}
        {:else}
            {#each obsStore.items as session (session.id)}
                <SessionCard 
                    id={session.id}
                    name={session.name}
                    description={session.description}
                    creation={session.creation}
                />
            {:else}
                <div class="text-center py-12 border-2 border-dashed border-border rounded-2xl">
                    <p class="text-copy-muted">{m.dash_observ_not_found()}</p>
                </div>
            {/each}
        {/if}
    </div>
</div>