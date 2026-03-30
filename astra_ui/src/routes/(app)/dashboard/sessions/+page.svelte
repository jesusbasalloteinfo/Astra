<script lang="ts">
    import SessionCard from '$lib/components/session/SessionCard.svelte';
    import { Plus } from 'lucide-svelte';

    // Dummy data
    const sessions = [
        {
            id: '1',
            name: 'Session 1',
            date: '28 Mar 2026',
            duration: '2h 34m',
            telescope: 'Celestron 8"',
            objectsObserved: 4,
            type: 'observation' as const,
        },
        {
            id: '2',
            name: 'Session 2',
            date: '21 Mar 2026',
            duration: '5h 10m',
            telescope: 'Celestron 8"',
            objectsObserved: 18,
            type: 'observation' as const,
        },
        {
            id: '3',
            name: 'Learning: Moon phases',
            date: '15 Mar 2026',
            duration: '45m',
            telescope: 'Celestron 8"',
            objectsObserved: 1,
            type: 'learning' as const,
        },
        {
            id: '4',
            name: 'Session Saturn',
            date: '10 Mar 2026',
            duration: '1h 20m',
            telescope: 'Celestron 8"',
            objectsObserved: 2,
            type: 'observation' as const,
        },
    ];
</script>

<div class="max-w-3xl mx-auto">

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
        <div>
            <h1 class="text-2xl font-bold text-copy-primary">Sessions</h1>
            <p class="text-sm text-copy-muted mt-1">{sessions.length} sessions recorded</p>
        </div>
        <button class="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-accent hover:bg-accent-hover
                       text-white text-sm font-semibold transition-colors">
            <Plus size={15} />
            New session
        </button>
    </div>

    <!-- List -->
    <div class="flex flex-col gap-3">
        {#each sessions as session}
            <SessionCard {...session} />
        {/each}
    </div>

</div>