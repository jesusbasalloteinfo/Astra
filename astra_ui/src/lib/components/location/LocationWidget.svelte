<script lang="ts">
	import { m } from '$lib/paraglide/messages';
    import { locStore } from '$lib/stores/location.svelte';
    import { MapPin, Thermometer, Droplets, Settings, Navigation } from 'lucide-svelte';
    import { fade } from 'svelte/transition';

    let {
        temperature = 12, 
        humidity = 65,
    } = $props();

    const active = $derived(locStore.active);
</script>

<div class="bg-panel border border-border rounded-2xl p-5 shadow-sm hover:border-accent/20 transition-all duration-300 group">
    <!-- Header -->
    <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-2">
            <div class="p-1.5 bg-accent/10 rounded-lg text-accent">
                <MapPin size={14} />
            </div>
            <span class="text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em]">{m.dash_main_locationwidget_title()}</span>
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
            <h3 class="text-lg font-bold text-copy-primary truncate mb-1">
                {active.label}
            </h3>

            <div class="flex items-center gap-3 text-[10px] font-mono text-copy-muted mb-6 opacity-70">
                <div class="flex items-center gap-1">
                    <Navigation size={10} class="text-accent/60 rotate-45" />
                    <span>{active.lat.toFixed(4)}°N</span>
                </div>
                <span class="opacity-30">•</span>
                <span>{active.lng.toFixed(4)}°E</span>
                <span class="opacity-30">•</span>
                <span>{active.elevation}m</span>
            </div>

            <div class="grid grid-cols-2 gap-4 pt-4 border-t border-border/40">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-secondary/50 flex items-center justify-center text-copy-muted group-hover:text-accent transition-colors">
                        <Thermometer size={15} />
                    </div>
                    <div>
                        <p class="text-[9px] uppercase font-black text-copy-muted leading-none mb-1">{m.dash_main_locationwidget_temp()}</p>
                        <p class="text-sm font-mono text-copy-primary leading-none">{temperature}°C</p>
                    </div>
                </div>

                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-secondary/50 flex items-center justify-center text-copy-muted group-hover:text-accent transition-colors">
                        <Droplets size={15} />
                    </div>
                    <div>
                        <p class="text-[9px] uppercase font-black text-copy-muted leading-none mb-1">{m.dash_main_locationwidget_humidity()}</p>
                        <p class="text-sm font-mono text-copy-primary leading-none">{humidity}%</p>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="py-6 text-center border-2 border-dashed border-border/50 rounded-xl bg-secondary/20">
            <p class="text-xs text-copy-muted italic mb-4">{m.dash_main_locationwidget_no_location()}</p>
            <a
                href="/dashboard/settings/location"
                class="inline-block px-4 py-2 bg-accent/10 hover:bg-accent/20 text-accent text-[10px] font-bold uppercase tracking-widest rounded-lg transition-all"
            >
                {m.dash_main_locationwidget_gps()}
            </a>
        </div>
    {/if}
</div>