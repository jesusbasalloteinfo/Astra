<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';
    import { Plus } from 'lucide-svelte';
    import SessionCard from '$lib/components/session/SessionCard.svelte';
    import TelescopeStatus from '$lib/components/telescope/TelescopeStatus.svelte';
    import LocationStatus from '$lib/components/location/LocationStatus.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';

    // Dummy user
    const user = { name: 'Test string' };


    // Dynamic greeting message
    type Period = 'morning' | 'afternoon' | 'evening' | 'night';

    const getPeriod = (hour: number): Period => {
        if (hour >= 5 && hour < 12) return 'morning';
        if (hour >= 12 && hour < 18) return 'afternoon';
        if (hour >= 18 && hour < 22) return 'evening';
        return 'night';
    };

    let now = $state(new Date());
    let period = $derived(getPeriod(now.getHours()));

    const getGreeting = (p: Period, name: string) => {
        const key = `dash_main_greeting_${p}` as const;
        const subKey = `dash_main_sub_morning_${p}` as const;
        
        return {
            title: m[key]({ user: name }),
            subtitle: m[subKey]()
        };
    };
    
    // Update time for greeting
    onMount(() => {
        const interval = setInterval(() => {
            now = new Date();
        }, 60000); 
        return () => clearInterval(interval);
    });

    // Dummy recent sessions
    const recentSessions = [
        {
            id: '1',
            name: 'dummy 1 Orion Nebula Night',
            date: '28 Mar 2026',
            duration: '2h 34m',
            telescope: 'Celestron 8"',
            objectsObserved: 4,
            type: 'observation' as const,
        },
        {
            id: '2',
            name: 'dummy 2 Messier Marathon',
            date: '21 Mar 2026',
            duration: '5h 10m',
            telescope: 'Celestron 8"',
            objectsObserved: 18,
            type: 'observation' as const,
        },
        {
            id: '3',
            name: 'dummy 3 Learning: Moon phases',
            date: '15 Mar 2026',
            duration: '45m',
            telescope: 'Celestron 8"',
            objectsObserved: 1,
            type: 'learning' as const,
        },
    ];

    let telescopeModalOpen = $state(false);
    let locationModalOpen = $state(false);
    let greetings = $derived(getGreeting(period, user.name));
</script>

<svelte:head>
    <title>{m.dash_title({name: m.name().toUpperCase()})}</title>
    <meta name="description" content={m.dash_title({name: m.name().toUpperCase()})} />
</svelte:head>

<div class="max-w-4xl mx-auto">

    <!-- Welcome -->
    <div class="flex items-center justify-between mb-8">
        <div>
            <h1 class="text-2xl font-bold text-copy-primary">
                {greetings.title}
            </h1>
            <p class="text-sm text-copy-muted mt-1">{greetings.subtitle}</p>
        </div>
        <button class="cursor-pointer flex items-center gap-2 px-5 py-3 rounded-xl bg-accent hover:bg-accent-hover
                       text-white font-semibold transition-colors shadow-glow">
            <Plus size={18} />
            {m.dash_main_new_session()}
        </button>
    </div>

    <!-- Widgets row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <TelescopeStatus
            connected={false}
            name="Testing"
            onconfig={() => telescopeModalOpen = true} />
        <LocationStatus
            configured={false}
            name="Nullville, Nullandia"
            temperature={14}
            humidity={62}
            onconfig={() => locationModalOpen = true} />
    </div>

    <!-- Recent sessions -->
    <div>
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-copy-muted uppercase tracking-wider">{m.dash_main_recent()}</h2>
            <a href="/dashboard/sessions" class="text-xs text-accent hover:text-accent-hover transition-colors">
                {m.dash_main_view_sessions()}
            </a>
        </div>
        <div class="flex flex-col gap-3">
            {#each recentSessions as session}
                <SessionCard {...session} />
            {/each}
        </div>
    </div>
</div>

<!-- Modals -->
<Modal bind:open={telescopeModalOpen} title="Telescope configuration" size="md">
    <p class="text-copy-secondary text-sm">Telescope config coming soon.</p>
</Modal>

<Modal bind:open={locationModalOpen} title="Location" size="md">
    <p class="text-copy-secondary text-sm">Location config coming soon.</p>
</Modal>