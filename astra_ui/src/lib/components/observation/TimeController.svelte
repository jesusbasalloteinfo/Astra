<!-- src/lib/components/observation/TimeController.svelte -->
<script lang="ts">
    import { timeEngine } from '$lib/stores/timeEngine.svelte';
    import { locStore } from '$lib/stores/location.svelte';
    import { Play, Pause, FastForward, Clock } from 'lucide-svelte';
    import { fade } from 'svelte/transition';
    import { onMount } from 'svelte';
    import { getLocale } from '$lib/paraglide/runtime.js';
	import { m } from '$lib/paraglide/messages';

    const speeds = [
        { label: '-1h/s', v: -3600 },
        { label: '-10m/s', v: -600 },
        { label: '-1m/s', v: -60 },
        { label: m.obs_timecontrol_real(), v: 1 },
        { label: '1m/s', v: 60 },
        { label: '10m/s', v: 600 },
        { label: '1h/s', v: 3600 }
    ];

    const formatTime = (date: Date) => date.toLocaleTimeString(getLocale(), { hour12: false, timeZone: 'UTC'});
    const formatDate = (date: Date) => date.toLocaleDateString(getLocale(), { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' });

    const getLocalInputValue = (date: Date) => {
        const y = date.getUTCFullYear();
        const m = String(date.getUTCMonth() + 1).padStart(2, '0');
        const d = String(date.getUTCDate()).padStart(2, '0');
        const h = String(date.getUTCHours()).padStart(2, '0');
        const min = String(date.getUTCMinutes()).padStart(2, '0');
        
        return `${y}-${m}-${d}T${h}:${min}`;
    };

    const handleTimeChange = (e: Event) => {
        const value = (e.currentTarget as HTMLInputElement).value;
        if (!value) return;

        const localSelectedTime = new Date(value + 'Z').getTime(); 
        
        const offsetMs = (locStore.active?.timezone || 0) * 3600000;
        
        timeEngine.setTime(localSelectedTime - offsetMs);
    };

    onMount(() => {
        timeEngine.play()
        return () => {
            if (!timeEngine.isLive) timeEngine.setLive(true);
        };
    });
</script>

<div class="pointer-events-auto bg-surface backdrop-blur-xl border border-border rounded-3xl p-4 shadow-[0_8px_32px_rgba(0,0,0,0.3)] 
    flex flex-wrap md:flex-nowrap items-center justify-between gap-4 transition-all">
    
    
    <!-- Div 1: Clocks -->
    <div class="flex items-center gap-4">
        <div class="p-2.5 bg-accent/10 rounded-2xl text-accent border border-accent/20 shadow-inner">
            <Clock size={22} />
        </div>
        <div class="flex flex-col">
            <div class="flex items-baseline gap-2">
                <span class="text-xl font-mono font-bold text-copy-primary tabular-nums tracking-tight">
                    {formatTime(timeEngine.local)}
                </span>
                <span class="text-[9px] bg-panel/50 border border-border px-1.5 py-0.5 rounded-md text-copy-muted uppercase font-bold">
                    {locStore.active?.timezone ? `UTC${locStore.active.timezone > 0 ? '+' : ''}${locStore.active.timezone}` : 'SYS'}
                </span>
            </div>
            <div class="flex items-baseline gap-1.5 mt-0.5">
                <span class="text-[10px] font-mono text-accent">{formatDate(timeEngine.local)}</span>
                <span class="text-[10px] text-border">|</span>
                <span class="text-[9px] font-mono text-copy-muted" title="Universal Time">UTC: {formatTime(timeEngine.current)}</span>
            </div>
        </div>
    </div>

    <!-- Div 2: Jump to date -->
    <div class="flex flex-col gap-2 items-center border-x border-border/50 px-6">
        <div class="flex items-center justify-between w-full">
            <label for="time-travel" class="text-[9px] font-bold text-copy-muted uppercase tracking-widest">
                {m.obs_timecontrol_time_travel()}
            </label>
            <button 
                onclick={() => {
                    timeEngine.setLive(true);
                    timeEngine.setRate(1)
                }}
                class="text-[9px] font-bold uppercase transition-all {timeEngine.isLive ? 'text-copy-muted' : 'text-accent hover:text-accent-hover drop-shadow-[0_0_5px_var(--color-accent-glow)]'}"
            >
                {timeEngine.isLive ? m.obs_timecontrol_live() : m.obs_timecontrol_back()}
            </button>
        </div>
        
        <input 
            id="time-travel"
            type="datetime-local" 
            value={getLocalInputValue(timeEngine.local)} 
            onchange={handleTimeChange}
            class="bg-panel/40 border border-border rounded-xl px-4 py-2 text-xs font-mono text-copy-primary 
                focus:bg-panel/60 focus:border-accent/50 outline-none transition-all w-full color-scheme-dark shadow-inner"
        />
    </div>

    <!-- Div 3: Time speed and play -->
    <div class="flex items-center justify-between lg:justify-end gap-4 border-t lg:border-t-0 border-border/50 pt-4 lg:pt-0 w-full lg:w-auto shrink-0">
        
        <div class="relative flex flex-col items-end">
            <select 
                value={timeEngine.playbackRate}
                onchange={(e) => {
                    timeEngine.setRate(Number(e.currentTarget.value));
                }}
                class="bg-panel/40 border border-border rounded-xl px-2 py-2 text-[11px] font-bold text-copy-primary uppercase outline-none focus:border-accent/50 transition-colors w-24 cursor-pointer appearance-none text-center shadow-inner h-9.5"
            >
                {#each speeds as s}
                    <option value={s.v} class="bg-panel">{s.label}</option>
                {/each}
            </select>
            
            {#if Math.abs(timeEngine.playbackRate) > 1 && timeEngine.isPlaying}
                <div in:fade class="absolute top-full mt-1 right-1 flex items-center gap-1 text-accent animate-pulse drop-shadow-[0_0_5px_var(--color-accent-glow)] whitespace-nowrap">
                    <FastForward size={10} />
                    <span class="text-[8px] font-black uppercase tracking-tighter">{m.obs_timecontrol_warp()}</span>
                </div>
            {/if}
            
        </div>

        <button 
            onclick={() => timeEngine.isPlaying ? timeEngine.pause() : timeEngine.play()}
            class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 transition-all {!timeEngine.isPlaying ? 'bg-panel/40 border border-border text-copy-primary hover:bg-surface' : 'bg-accent text-white shadow-[0_0_20px_var(--color-accent-glow)]'}">
            {#if !timeEngine.isPlaying} 
                <Play size={22} fill="currentColor" class="ml-1" /> 
            {:else} 
                <Pause size={22} fill="currentColor" /> 
            {/if}
        </button>
    </div>
</div>