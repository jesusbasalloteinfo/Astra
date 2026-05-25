<script lang="ts">
    import { locStore } from '$lib/stores/location.svelte';
    import { MapPin, Navigation, Plus, Trash2, X, Map as MapIcon, Globe, ChevronRight } from 'lucide-svelte';
    import { fade, slide } from 'svelte/transition';
    import type {UserLocation, LocationCreate} from '$lib/types/user'
    import * as m from '$lib/paraglide/messages.js';
	import LocationCard from './LocationCard.svelte';

    const getLocalTimezone = () => -(new Date().getTimezoneOffset() / 60);

    let newLoc = $state<LocationCreate>({ 
        label: '', 
        lat: 0, 
        lng: 0, 
        elevation: 0,
        timezone: getLocalTimezone(),
        is_default: false 
    });

    // Validación reactiva
    const isValid = $derived(
        newLoc.label.trim() !== '' &&
        newLoc.lat >= -90 && newLoc.lat <= 90 &&
        newLoc.lng >= -180 && newLoc.lng <= 180 &&
        newLoc.elevation >= -1000 && newLoc.elevation <= 10000 &&
        newLoc.timezone >= -12 && newLoc.timezone <= 14
    );

    async function handleGPS() {
        try {
            const coords = await locStore.detectGPS();
            newLoc.lat = coords.lat ?? 0;
            newLoc.lng = coords.lng ?? 0;
            newLoc.elevation = coords.elevation ?? 0;
            newLoc.timezone = coords.timezone ?? getLocalTimezone();
        } catch (e) {
            console.error("GPS Error", e);
        }
    }

    async function save() {
        await locStore.addLocation(newLoc);
        locStore.hideForm();
        newLoc = { label: '', lat: 0, lng: 0, elevation: 0, timezone: getLocalTimezone(), is_default: false };
    }
</script>

<div class="space-y-4">
    <div class="flex items-center justify-between px-1">
        <h3 class="text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em] flex items-center gap-2">
            <Globe size={12} class="text-accent" />
            {m.dash_location_subtitle()}
        </h3>
    </div>
    
    <div class="flex flex-col gap-2.5">
        {#each locStore.all as loc (loc.id)}
            <LocationCard 
                id={loc.id}
                label={loc.label}
                lat={loc.lat}
                lng={loc.lng}
                tz={loc.timezone}
                elevation={loc.elevation} 
            />
        {:else}
            <div class="py-10 text-center border-2 border-dashed border-border rounded-2xl bg-panel/20">
                <p class="text-xs text-copy-muted italic">{m.dash_location_not_found()}</p>
            </div>
        {/each}
    </div>

    <!-- New location -->
    <div class="pt-2">
        {#if !locStore.isAdding}
            <button 
                onclick={() => locStore.isAdding = true}
                class="cursor-pointer w-full flex items-center justify-center gap-2 p-3 rounded-xl border border-dashed border-border 
                       hover:bg-accent/5 hover:border-accent/50 hover:text-accent transition-all text-[11px] font-bold uppercase tracking-widest text-copy-muted">
                <Plus size={14} />
                {m.dash_location_new_location()}
            </button>
        {:else}
            <div in:slide={{ duration: 200 }} class="p-5 rounded-2xl bg-panel border border-accent/20 space-y-4 shadow-2xl">
                <div class="flex items-center justify-between">
                    <span class="text-[10px] font-black uppercase tracking-widest text-accent">{m.dash_location_new_subtitle()}</span>
                    <button onclick={() => locStore.isAdding = false} class="cursor-pointer text-copy-muted hover:text-copy-primary transition-colors">
                        <X size={16} />
                    </button>
                </div>

                <div class="space-y-4">
                    <span class="text-[9px] font-bold text-copy-muted ml-1 uppercase">{m.dash_location_new_label()}</span>
                    <input 
                        bind:value={newLoc.label} 
                        placeholder={m.dash_location_new_label_placeholder()}
                        class="w-full bg-secondary/50 border border-border rounded-xl px-4 py-2.5 text-sm text-copy-primary focus:border-accent outline-none transition-colors"
                    />
                    
                    <div class="grid grid-cols-4 gap-3">
                        <div class="space-y-1">
                            <span class="text-[9px] font-bold text-copy-muted ml-1 uppercase">{m.dash_location_new_lat()}</span>
                            <input 
                                type="number" 
                                min="-90" 
                                max="90"
                                bind:value={newLoc.lat} 
                                class="w-full bg-secondary/50 border border-border rounded-xl px-4 py-2 text-sm font-mono text-copy-primary outline-none focus:border-accent/50" />
                        </div>
                        <div class="space-y-1">
                            <span class="text-[9px] font-bold text-copy-muted ml-1 uppercase">{m.dash_location_new_lng()}</span>
                            <input 
                                type="number" 
                                min="-180" 
                                max="180"
                                bind:value={newLoc.lng} 
                                class="w-full bg-secondary/50 border border-border rounded-xl px-4 py-2 text-sm font-mono text-copy-primary outline-none focus:border-accent/50" />
                        </div>
                        <div class="space-y-1">
                            <span class="text-[9px] font-bold text-copy-muted ml-1 uppercase">{m.dash_location_new_elev()}</span>
                            <input 
                                type="number"
                                min="-1000" 
                                max="10000"
                                bind:value={newLoc.elevation} 
                                class="w-full bg-secondary/50 border border-border rounded-xl px-4 py-2 text-sm font-mono text-copy-primary outline-none focus:border-accent/50" />
                        </div>
                        <div class="space-y-1">
                            <span class="text-[9px] font-bold text-copy-muted ml-1 uppercase">{m.dash_location_new_tz()}</span>
                            <input 
                                type="number" 
                                step="0.5" 
                                min="-12" 
                                max="14" 
                                bind:value={newLoc.timezone} 
                                class="w-full bg-secondary/50 border border-border rounded-xl px-4 py-2 text-sm font-mono text-copy-primary outline-none focus:border-accent/50" 
                            />
                        </div>
                    </div>

                    <button 
                        onclick={handleGPS}
                        disabled={locStore.isDetecting}
                        class="w-full flex items-center justify-center cursor-pointer gap-2 py-2.5 text-[10px] font-bold uppercase tracking-widest bg-secondary/30 hover:bg-secondary/60 border border-border rounded-xl transition-all">
                        <Navigation size={14} class={locStore.isDetecting ? 'animate-spin text-accent' : ''} />
                        {locStore.isDetecting ? m.dash_location_new_gps_detect() : m.dash_location_new_gps()}
                    </button>
                    <label class="flex items-center gap-3 cursor-pointer p-2 group">
                        <div class="relative flex items-center">
                            <input 
                                type="checkbox" 
                                bind:checked={newLoc.is_default}
                                class="peer sr-only"
                            />
                            <div class="w-8 h-4 bg-secondary border border-border rounded-full peer-checked:bg-accent/30 transition-colors"></div>
                            <div class="absolute left-1 w-2 h-2 bg-copy-muted rounded-full transition-all peer-checked:left-5 peer-checked:bg-accent"></div>
                        </div>
                        <span class="text-[10px] font-bold text-copy-muted uppercase tracking-widest group-hover:text-copy-primary transition-colors">
                            {m.dash_location_new_default()}
                        </span>
                    </label>

                    <button 
                        onclick={save}
                        disabled={!isValid || locStore.isSyncing}
                        class="w-full cursor-pointer py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg shadow-accent/20 disabled:opacity-30 transition-all active:scale-[0.98]">
                        {locStore.isSyncing ? m.dash_location_action_saving() : m.dash_location_action_add()}
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div>
