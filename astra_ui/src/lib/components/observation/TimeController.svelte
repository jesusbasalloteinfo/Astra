<!--
  ASTRA - Automated Smart Telescope Remote Assistant
  Copyright (C) 2026 Jesus Basallote
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
  
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<!-- src/lib/components/observation/TimeController.svelte -->
<script lang="ts">
    import { timeEngine } from '$lib/stores/timeEngine.svelte';
    import { locStore } from '$lib/stores/location.svelte';
    import { Play, Pause, FastForward, Clock } from 'lucide-svelte';
    import { fade } from 'svelte/transition';
    import { onMount } from 'svelte';
    import { getLocale } from '$lib/paraglide/runtime.js';
	import { m } from '$lib/paraglide/messages';

    /** Available playback speed options */
    const speeds = [
        { label: '-1h/s', v: -3600 },
        { label: '-10m/s', v: -600 },
        { label: '-1m/s', v: -60 },
        { label: m.obs_timecontrol_real(), v: 1 },
        { label: '1m/s', v: 60 },
        { label: '10m/s', v: 600 },
        { label: '1h/s', v: 3600 }
    ];

    /**
     * Formats a date object into a localized time string
     * @param {Date} date - The date to format
     * @returns {string} Formatted time string
     */
    const formatTime = (date: Date) => date.toLocaleTimeString(getLocale(), { hour12: false, timeZone: 'UTC'});
    /**
     * Formats a date object into a localized date string
     * @param {Date} date - The date to format
     * @returns {string} Formatted date string
     */
    const formatDate = (date: Date) => date.toLocaleDateString(getLocale(), { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' });

    /**
     * Formats a date into a string suitable for a datetime-local input
     * @param {Date} date - The date to format
     * @returns {string} Formatted input value string
     */
    const getLocalInputValue = (date: Date) => {
        const y = date.getUTCFullYear();
        const m = String(date.getUTCMonth() + 1).padStart(2, '0');
        const d = String(date.getUTCDate()).padStart(2, '0');
        const h = String(date.getUTCHours()).padStart(2, '0');
        const min = String(date.getUTCMinutes()).padStart(2, '0');
        
        return `${y}-${m}-${d}T${h}:${min}`;
    };

    /**
     * Handles manual time selection from the datetime-local input
     * @param {Event} e - The input change event
     */
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

<!-- 
    Responsiveness Strategy:
    - Mobile & Tablet Portrait: 2-column grid, compact max-width.
    - Landscape (Any device) & PC: Horizontal flex bar.
-->
<div class="pointer-events-auto bg-surface backdrop-blur-xl border border-border rounded-2xl lg:rounded-3xl p-3 lg:p-4 shadow-[0_8px_32px_rgba(0,0,0,0.3)] 
    grid grid-cols-2 landscape:flex landscape:flex-row lg:flex lg:flex-row items-center justify-center 
    gap-x-3 gap-y-4 landscape:gap-3 lg:gap-4 transition-all 
    w-full max-w-md landscape:max-w-none lg:max-w-none landscape:w-max lg:w-max mx-auto">
    
    <!-- Section 1: Clock & Date -->
    <div class="flex items-center justify-start gap-3 lg:gap-4 w-full landscape:w-auto lg:w-auto order-1">
        <div class="flex items-center gap-2 lg:gap-3">
            <div class="p-1.5 lg:p-2.5 bg-accent/10 rounded-xl lg:rounded-2xl text-accent border border-accent/20 shadow-inner shrink-0">
                <Clock size={16} class="lg:w-5.5 lg:h-5.5" />
            </div>
            <div class="flex flex-col">
                <div class="flex items-baseline gap-2">
                    <span class="text-base lg:text-xl font-mono font-bold text-copy-primary tabular-nums tracking-tight">
                        {formatTime(timeEngine.local)}
                    </span>
                    <span class="text-[9px] bg-panel/50 border border-border px-1.5 py-0.5 rounded-md text-copy-muted uppercase font-bold inline-block">
                        {locStore.active?.timezone ? `UTC${locStore.active.timezone > 0 ? '+' : ''}${locStore.active.timezone}` : 'SYS'}
                    </span>
                </div>
                <div class="flex items-baseline justify-start gap-1.5 mt-0.5">
                    <span class="text-[9px] lg:text-[10px] font-mono text-accent">{formatDate(timeEngine.local)}</span>
                    <span class="text-[9px] text-border hidden lg:inline">|</span>
                    <span class="text-[9px] font-mono text-copy-muted hidden lg:inline" title="Universal Time">UTC: {formatTime(timeEngine.current)}</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Section 2: Playback (Top-Right on Portrait, Far-Right on Landscape/PC) -->
    <div class="flex items-center justify-end gap-2 lg:gap-4 w-full landscape:w-auto lg:w-auto shrink-0 order-2 landscape:order-3 lg:order-3">
        <div class="relative flex flex-col items-center lg:items-end">
            <select 
                value={timeEngine.playbackRate}
                onchange={(e) => timeEngine.setRate(Number(e.currentTarget.value))}
                class="bg-panel/40 border border-border rounded-xl px-2 py-1 lg:py-2 text-[10px] lg:text-[11px] font-bold text-copy-primary uppercase outline-none focus:border-accent/50 transition-colors w-28 md:w-20 lg:w-24 cursor-pointer appearance-none text-center shadow-inner h-9 lg:h-10.5"
            >
                {#each speeds as s}
                    <option value={s.v} class="bg-panel">{s.label}</option>
                {/each}
            </select>
            
            {#if Math.abs(timeEngine.playbackRate) > 1 && timeEngine.isPlaying}
                <div in:fade class="absolute top-full mt-0.5 left-1/2 -translate-x-1/2 landscape:translate-x-0 lg:translate-x-0 landscape:left-auto landscape:right-1 lg:left-auto lg:right-1 flex items-center gap-1 text-accent animate-pulse drop-shadow-[0_0_5px_var(--color-accent-glow)] whitespace-nowrap">
                    <FastForward size={9} />
                    <span class="text-[8px] font-black uppercase tracking-tighter">{m.obs_timecontrol_warp()}</span>
                </div>
            {/if}
        </div>

        <button 
            onclick={() => timeEngine.isPlaying ? timeEngine.pause() : timeEngine.play()}
            class="w-9 h-9 lg:w-12 lg:h-12 rounded-xl lg:rounded-2xl cursor-pointer flex items-center justify-center shrink-0 transition-all {!timeEngine.isPlaying ? 'bg-panel/40 border border-border text-copy-primary hover:bg-surface' : 'bg-accent text-white shadow-[0_0_20px_var(--color-accent-glow)]'}">
            {#if !timeEngine.isPlaying} 
                <Play size={18} fill="currentColor" class="ml-1 lg:w-5.5 lg:h-5.5" /> 
            {:else} 
                <Pause size={18} fill="currentColor" class="lg:w-5.5 lg:h-5.5" /> 
            {/if}
        </button>
    </div>

    <!-- Section 3: Time Travel (Bottom on Portrait, Middle on Landscape/PC) -->
    <div class="flex flex-col gap-1.5 lg:gap-2 items-center border-t landscape:border-t-0 lg:border-t-0 landscape:border-x lg:border-x border-border/50 pt-3 landscape:pt-0 lg:pt-0 px-1 lg:px-6 w-full landscape:w-auto lg:w-auto col-span-2 landscape:col-span-1 lg:col-span-1 order-3 landscape:order-2 lg:order-2">
        <div class="flex items-center justify-between gap-6 lg:gap-0 w-full">
            <label for="time-travel" class="text-[8px] lg:text-[9px] font-bold text-copy-muted uppercase tracking-widest">
                {m.obs_timecontrol_time_travel()}
            </label>
            <button 
                onclick={() => timeEngine.setLive(true)}
                class="text-[8px] lg:text-[9px] font-bold uppercase transition-all {timeEngine.isLive ? 'text-copy-muted' : 'text-accent hover:text-accent-hover drop-shadow-[0_0_5px_var(--color-accent-glow)]'}"
            >
                {timeEngine.isLive ? m.obs_timecontrol_live() : m.obs_timecontrol_back()}
            </button>
        </div>
        
        <input 
            id="time-travel"
            type="datetime-local" 
            value={getLocalInputValue(timeEngine.local)} 
            onchange={handleTimeChange}
            onclick={(e) => (e.currentTarget as any).showPicker?.()}
            class="bg-panel/40 border border-border rounded-xl px-2.5 lg:px-4 py-2 text-[11px] lg:text-xs font-mono text-copy-primary text-center landscape:text-left lg:text-left
                focus:bg-panel/60 focus:border-accent/50 outline-none transition-all w-full lg:min-w-50 color-scheme-dark shadow-inner cursor-pointer"
        />
    </div>
</div>