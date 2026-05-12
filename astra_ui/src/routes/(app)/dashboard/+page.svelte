<!-- src/routes/(app)/dashboard/+page.svelte -->
<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';
    import { Plus, Globe } from 'lucide-svelte';
    import SessionCard from '$lib/components/session/SessionCard.svelte';
    import LocationWidget from '$lib/components/location/LocationWidget.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
    import DeviceWidget from '$lib/components/devices/DeviceWidget.svelte';
	import { obsStore } from '$lib/stores/observations.svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { newObsStore } from '$lib/stores/newObservation.svelte';
	import { locStore } from '$lib/stores/location.svelte';

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
        const interval = setInterval(() => { now = new Date(); }, 60000); 
        return () => clearInterval(interval);
    });

    let greetings = $derived(getGreeting(period, authStore.user?.username || (authStore.isLoggingOut ? "" : "Explorer")));
    const recentSessions = $derived(obsStore.items.slice(0, 3));
</script>

<svelte:head>
    <title>{m.dash_title({name: m.name().toUpperCase()})}</title>
    <meta name="description" content={m.dash_title({name: m.name().toUpperCase()})} />
</svelte:head>

<div class="max-w-4xl mx-auto transition-opacity duration-300 {now ? 'opacity-100' : 'opacity-0'}">
    <!-- Welcome -->
    <div class="mb-6 md:mb-8">
        <h1 class="text-2xl md:text-3xl font-bold text-copy-primary">{greetings.title}</h1>
            <p class="text-sm text-copy-muted mt-1">{greetings.subtitle}</p>
        </div>
        
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
    <!-- Widgets row -->
    {#if locStore.active}
        <DeviceWidget/>
            <LocationWidget temperature={14} humidity={62} />
    {:else}
            <div class="col-span-1 md:col-span-2 p-6 md:p-12 landscape:p-6 bg-panel border border-dashed border-border rounded-2xl md:rounded-3xl text-center">
                <div class="w-12 h-12 md:w-16 md:h-16 bg-accent/10 text-accent rounded-full flex items-center justify-center mx-auto mb-4">
                    <Globe class="w-6 h-6 md:w-8 md:h-8" />
            </div>
                <h2 class="text-lg md:text-xl font-bold text-copy-primary">{ m.dash_main_zeroconf_welcome() }</h2>
                <p class="text-sm text-copy-muted max-w-md mx-auto mt-2 mb-6">
                { m.dash_main_zeroconf_info() }
            </p>
                <a href="/dashboard/location" class="inline-block px-6 py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-bold transition-all shadow-lg shadow-accent/20 active:scale-95">
                { m.dash_main_zeroconf_config() }
            </a>
        </div>
    {/if}
    </div>
    

    <!-- Recent sessions -->
    <div>
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-xs font-bold text-copy-muted uppercase tracking-widest">{m.dash_main_recent()}</h2>
            <a href="/dashboard/sessions" class="text-xs font-bold text-accent hover:text-accent-hover transition-colors">
                {m.dash_main_view_sessions()}
            </a>
        </div>
        <div class="flex flex-col gap-3">
            <button 
                onclick={() => newObsStore.open()}
                class="hidden md:flex cursor-pointer w-fit items-center gap-2 px-5 py-3 rounded-xl bg-accent hover:bg-accent-hover text-white font-bold transition-all active:scale-95 shadow-lg shadow-accent/20">
                <Plus size={18} />
                {m.dash_main_new_session()}
            </button>
            
            {#each recentSessions as session (session.id)}
                <SessionCard id={session.id} name={session.name} creation={session.creation} />
            {:else}
                <div class="text-center py-10 md:py-12 border border-dashed border-border rounded-xl md:rounded-2xl bg-surface/50">
                    <p class="text-sm text-copy-muted">{m.dash_observ_not_found()}</p>
                </div>
            {/each}
        </div>
    </div>
</div>
