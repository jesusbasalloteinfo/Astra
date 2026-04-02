<script lang="ts">
    import SessionCard from '$lib/components/session/SessionCard.svelte';
    import { Plus } from 'lucide-svelte';
    import { obsStore } from '$lib/stores/observations.svelte';
    import * as m from '$lib/paraglide/messages.js';
	import { newObsStore } from '$lib/stores/newObservation.svelte';
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
            onclick={() => newObsStore.open()}
            class="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-accent hover:bg-accent-hover
                text-white text-sm font-semibold transition-colors shadow-lg shadow-accent/20">
            <Plus size={15} />
            {m.dash_observ_new_session()}
        </button>
    </div>

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