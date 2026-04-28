<!-- src/routes/(app)/dashboard/+page.svelte -->
<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';
    import { Plus } from 'lucide-svelte';
    import SessionCard from '$lib/components/session/SessionCard.svelte';
    import LocationWidget from '$lib/components/location/LocationWidget.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
	import { obsStore } from '$lib/stores/observations.svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { newObsStore } from '$lib/stores/newObservation.svelte';
	import { locStore } from '$lib/stores/location.svelte';
    import { Globe } from 'lucide-svelte';
	import DeviceWidget from '$lib/components/devices/DeviceWidget.svelte';

    // Dynamic greeting message
    type Period = 'morning' | 'afternoon' | 'evening' | 'night';

    const getPeriod = (hour: number): Period => {
        if (hour >= 5 && hour < 12) return 'morning';
        if (hour >= 12 && hour < 18) return 'afternoon';
        if (hour >= 18 && hour < 22) return 'evening';
        return 'night';
    };

    let now = $state<Date | null>(null);
    let period = $derived(now ? getPeriod(now.getHours()) : 'night'); 

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
        now = new Date();

        const interval = setInterval(() => {
            now = new Date();
        }, 60000); 
        return () => clearInterval(interval);
    });

    let telescopeModalOpen = $state(false);
    let greetings = $derived(getGreeting(period, authStore.user?.username || ""));
    const recentSessions = $derived(obsStore.items.slice(0, 3));
</script>

<svelte:head>
    <title>{m.dash_title({name: m.name().toUpperCase()})}</title>
    <meta name="description" content={m.dash_title({name: m.name().toUpperCase()})} />
</svelte:head>

<div class="max-w-4xl mx-auto transition-opacity duration-300 {now ? 'opacity-100' : 'opacity-0'}">
    <!-- Welcome -->
    <div class="flex items-center justify-between mb-8">
        <div>
            <h1 class="text-2xl font-bold text-copy-primary">
                {greetings.title}
            </h1>
            <p class="text-sm text-copy-muted mt-1">{greetings.subtitle}</p>
        </div>
        
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
    <!-- Widgets row -->
    {#if locStore.active}

        <DeviceWidget/>
        <LocationWidget
            temperature={14}
            humidity={62}/>
    {:else}
        <!-- Zero State -->
        <div class="col-span-full p-12 bg-panel border-2 border-dashed border-border rounded-3xl text-center">
            <div class="w-16 h-16 bg-accent/10 text-accent rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe size={32} />
            </div>
            <h2 class="text-xl font-bold text-copy-primary">{ m.dash_main_zeroconf_welcome() }</h2>
            <p class="text-sm text-copy-muted max-w-sm mx-auto mt-2 mb-6">
                { m.dash_main_zeroconf_info() }
            </p>
            <a href="/dashboard/location" class="px-6 py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-bold transition-all shadow-lg shadow-accent/20">
                { m.dash_main_zeroconf_config() }
            </a>
        </div>
    {/if}
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
            <button 
                onclick={() => newObsStore.open()}
                class="cursor-pointer w-1/4 flex items-center gap-2 px-5 py-3 rounded-xl bg-accent hover:bg-accent-hover
                    text-white font-semibold transition-colors shadow-glow">
                <Plus size={18} />
                {m.dash_main_new_session()}
            </button>
            {#each recentSessions as session (session.id)}
                <SessionCard 
                    id={session.id}
                    name={session.name}
                    creation={session.creation}
                />
            {:else}
                <div class="text-center py-12 border-2 border-dashed border-border rounded-2xl">
                    <p class="text-copy-muted">{m.dash_observ_not_found()}</p>
                </div>
            {/each}
        </div>
    </div>
</div>

<!-- Modals -->
<Modal bind:open={telescopeModalOpen} title="Telescope configuration" size="md">
    <p class="text-copy-secondary text-sm">Telescope config coming soon.</p>
</Modal>
