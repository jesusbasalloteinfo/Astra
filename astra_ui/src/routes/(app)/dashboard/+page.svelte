<!-- src/routes/(app)/dashboard/+page.svelte -->
<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { Plus, Globe, Sun, CloudSun, Moon, Sparkles } from 'lucide-svelte';
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
        if (hour >= 5 && hour < 13) return 'morning';
        if (hour >= 13 && hour < 17) return 'afternoon';
        if (hour >= 17 && hour < 20) return 'evening';
        return 'night';
    };

    let now = $state<Date | null>(browser ? new Date() : null);
    
    // Derived hour based on active location timezone or local time fallback
    let effectiveHour = $derived.by(() => {
        if (!now) return 12; // Neutral fallback
        const offset = locStore.active?.timezone;
        
        // If no location timezone is set, use the local browser hour
        if (offset === undefined || offset === null) return now.getHours();
        
        // Calculate the hour in the target timezone
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const targetDate = new Date(utc + (3600000 * offset));
        return targetDate.getHours();
    });

    let period = $derived(now ? getPeriod(effectiveHour) : 'night');
    let randomIndex = $state(0);

    // Format time for the localized clock
    let clockData = $derived.by(() => {
        if (!now) return { time: '--:--:--', offset: '' };
        const offset = locStore.active?.timezone;
        
        let targetDate: Date;
        let offsetStr = '';
        
        if (offset === undefined || offset === null) {
            targetDate = now;
            const localOffset = -now.getTimezoneOffset() / 60;
            offsetStr = `UTC${localOffset >= 0 ? '+' : ''}${localOffset}`;
        } else {
            const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
            targetDate = new Date(utc + (3600000 * offset));
            offsetStr = `UTC${offset >= 0 ? '+' : ''}${offset}`;
        }
        
        return {
            time: targetDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
            offset: offsetStr
        };
    });

    const getGreeting = (p: Period, name: string, idx: number) => {
        const key = `dash_main_greeting_${p}_${idx}` as any;
        const subKey = `dash_main_sub_morning_${p}_${idx}` as any;

        return {
            title: m[key] ? m[key]({ user: name }) : m[`dash_main_greeting_${p}_0` as any]({ user: name }),
            subtitle: m[subKey] ? m[subKey]() : m[`dash_main_sub_morning_${p}_0` as any]()
        };
    };

    const getPeriodIcon = (p: Period) => {
        switch (p) {
            case 'morning': return { icon: Sun, color: 'text-orange-400' };
            case 'afternoon': return { icon: CloudSun, color: 'text-orange-500' };
            case 'evening': return { icon: Moon, color: 'text-purple-400' };
            case 'night': return { icon: Sparkles, color: 'text-accent' };
        }
    };

    // Update time for greeting
    onMount(() => {
        now = new Date();
        randomIndex = Math.floor(Math.random() * 3);
        const interval = setInterval(() => { now = new Date(); }, 1000);
        return () => clearInterval(interval);
    });

    let greetings = $derived(getGreeting(period, authStore.user?.username || (authStore.isLoggingOut ? "" : "Explorer"), randomIndex));
    let periodIcon = $derived(getPeriodIcon(period));
    const recentSessions = $derived(obsStore.items.slice(0, 3));
</script>

<svelte:head>
    <title>{m.dash_title({name: m.name().toUpperCase()})}</title>
    <meta name="description" content={m.dash_title({name: m.name().toUpperCase()})} />
</svelte:head>

<div class="max-w-4xl mx-auto transition-opacity duration-300 {now ? 'opacity-100' : 'opacity-0'}">
    <!-- Welcome -->
    <div class="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
            <div class="p-3 bg-panel border border-border rounded-2xl shadow-sm shrink-0">
                <periodIcon.icon class="w-6 h-6 md:w-8 md:h-8 {periodIcon.color}" />
            </div>
            <div class="min-w-0">
                <h1 class="text-2xl md:text-3xl font-bold text-copy-primary leading-tight truncate">{greetings.title}</h1>
                <p class="text-sm text-copy-muted mt-0.5 truncate">{greetings.subtitle}</p>
                
                <!-- Localized Clock (Mobile Only) -->
                <div class="flex sm:hidden items-center gap-2 mt-2">
                    <div class="text-md font-mono font-bold text-copy-primary tracking-tighter">
                        {clockData.time}
                    </div>
                    <div class="px-1.5 py-0.5 bg-accent/10 border border-accent/20 rounded text-[10px] font-bold text-accent uppercase tracking-wider">
                        {clockData.offset}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Localized Clock (Desktop Only) -->
        <div class="hidden sm:flex flex-col items-end shrink-0">
            <div class="text-xl md:text-2xl font-mono font-bold text-copy-primary tracking-tighter">
                {clockData.time}
            </div>
            <div class="px-1.5 py-0.5 bg-accent/10 border border-accent/20 rounded text-[10px] font-bold text-accent uppercase tracking-wider">
                {clockData.offset}
            </div>
        </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
    <!-- Widgets row -->
    {#if locStore.active}
        <DeviceWidget/>
            <LocationWidget/>
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
                <SessionCard 
                    id={session.id} 
                    name={session.name} 
                    description={session.description}
                    creation={session.creation}
                    lastUsed={session.last_used} 
                />
            {:else}
                <div class="text-center py-10 md:py-12 border border-dashed border-border rounded-xl md:rounded-2xl bg-surface/50">
                    <p class="text-sm text-copy-muted">{m.dash_observ_not_found()}</p>
                </div>
            {/each}
        </div>
    </div>
</div>
