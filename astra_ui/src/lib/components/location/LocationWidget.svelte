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

<!-- src/lib/components/location/LocationWidget.svelte -->
<script lang="ts">
	import { m } from '$lib/paraglide/messages';
    import { locStore } from '$lib/stores/location.svelte';
    import { MapPin, Thermometer, Droplets, Settings, Navigation } from 'lucide-svelte';
    import { fade } from 'svelte/transition';

    let {
        /** Current temperature to display */
        temperature = 12, 
        /** Current humidity percentage to display */
        humidity = 65,
    } = $props();

    /** The currently active location from the location store */
    const active = $derived(locStore.active);
</script>

<div class="bg-panel border border-border rounded-2xl p-4 md:p-5 shadow-sm hover:border-accent/20 transition-all duration-300 group">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 md:mb-5">
        <div class="flex items-center gap-2">
            <div class="p-1 bg-accent/10 rounded-lg text-accent">
                <MapPin size={12} class="md:hidden" />
                <MapPin size={14} class="hidden md:block" />
            </div>
            <span class="text-[9px] md:text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em]">{m.dash_main_locationwidget_title()}</span>
        </div>
        <a
            href="/dashboard/location"
            class="text-copy-muted hover:text-copy-primary transition-colors p-1.5 rounded-lg hover:bg-surface"
            title={m.dash_main_locationwidget_config()}
        >
            <Settings size={14} />
        </a>
    </div>

    {#if active}
        <div in:fade>
            <h3 class="text-base md:text-lg font-bold text-copy-primary truncate mb-0.5 md:mb-1">
                {active.label}
            </h3>

            <div class="flex items-center gap-2 md:gap-3 text-[9px] md:text-[10px] font-mono text-copy-muted mb-4 md:mb-6 opacity-70">
                <div class="flex items-center gap-1">
                    <Navigation size={9} class="text-accent/60 rotate-45 md:w-2.5" />
                    <span>{active.lat.toFixed(3)}°N</span>
                </div>
                <span class="opacity-30">•</span>
                <span>{active.lng.toFixed(3)}°E</span>
                <span class="opacity-30">•</span>
                <span>{active.elevation}m</span>
            </div>

            <!-- <div class="grid grid-cols-2 gap-4 pt-3 md:pt-4 border-t border-border/40">
                <div class="flex items-center gap-2 md:gap-3">
                    <div class="w-7 h-7 md:w-8 md:h-8 rounded-full bg-secondary/50 flex items-center justify-center text-copy-muted group-hover:text-accent transition-colors">
                        <Thermometer size={14} class="md:w-3.75" />
                    </div>
                    <div>
                        <p class="text-[8px] md:text-[9px] uppercase font-black text-copy-muted leading-none mb-1">{m.dash_main_locationwidget_temp()}</p>
                        <p class="text-xs md:text-sm font-mono text-copy-primary leading-none">{temperature}°C</p>
                    </div>
                </div>

                <div class="flex items-center gap-2 md:gap-3">
                    <div class="w-7 h-7 md:w-8 md:h-8 rounded-full bg-secondary/50 flex items-center justify-center text-copy-muted group-hover:text-accent transition-colors">
                        <Droplets size={14} class="md:w-3.75" />
                    </div>
                    <div>
                        <p class="text-[8px] md:text-[9px] uppercase font-black text-copy-muted leading-none mb-1">{m.dash_main_locationwidget_humidity()}</p>
                        <p class="text-xs md:text-sm font-mono text-copy-primary leading-none">{humidity}%</p>
                    </div>
                </div>
            </div> -->
        </div>
    {:else}
        <div class="py-4 md:py-6 text-center border-2 border-dashed border-border/50 rounded-xl bg-secondary/20">
            <p class="text-[11px] md:text-xs text-copy-muted italic mb-3 md:mb-4">{m.dash_main_locationwidget_no_location()}</p>
            <a
                href="/dashboard/settings/location"
                class="inline-block px-4 py-2 bg-accent/10 hover:bg-accent/20 text-accent text-[9px] md:text-[10px] font-bold uppercase tracking-widest rounded-lg transition-all"
            >
                {m.dash_main_locationwidget_gps()}
            </a>
        </div>
    {/if}
</div>