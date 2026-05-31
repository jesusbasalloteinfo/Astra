<!-- src/lib/components/location/LocationCard.svelte -->
<script lang="ts">
    import { locStore } from '$lib/stores/location.svelte';
    import { MapPin, Home, Plus, Trash2, X, Map as MapIcon, Globe, ChevronRight, House } from 'lucide-svelte';
    import { fade, slide } from 'svelte/transition';
    import type {UserLocation, LocationCreate} from '$lib/types/user'
    import * as m from '$lib/paraglide/messages.js';
	import Modal from '../ui/Modal.svelte';

    let { 
        /** Unique identifier for the location */
        id, 
        /** Display label for the location */
        label, 
        /** Latitude in decimal degrees */
        lat, 
        /** Longitude in decimal degrees */
        lng, 
        /** Timezone offset from UTC */
        tz, 
        /** Elevation above sea level in meters */
        elevation 
    } = $props();

    /** Whether the deletion confirmation modal is visible */
    let showDeleteModal = $state(false);

    /**
     * Attempts to delete the location after confirmation
     */
    async function handleDelete() {
        locStore.deleteLocation(id);
        showDeleteModal = false;
    }
    
    /** Formatted timezone string (e.g., "+1" or "-5") */
    const formattedTZ = $derived(tz >= 0 ? `+${tz}` : `${tz}`);
</script>


<div class="group relative flex items-center">
    <button 
        onclick={() => locStore.select(id)}
        class="flex flex-1 items-center gap-4 p-4 bg-panel border border-border rounded-xl
                hover:bg-surface transition-all cursor-pointer pr-14 text-left
                {locStore.effectiveActiveId === id ? 'border-accent/40 bg-accent/5' : ''}">
        
        <div class="p-2.5 rounded-xl transition-all duration-300
            {locStore.effectiveActiveId === id 
                ? 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]' 
                : 'bg-secondary/50 text-copy-muted group-hover:text-copy-primary'}">
            <MapPin size={18} />
        </div>

        <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-copy-primary truncate">{label}</span>
                {#if locStore.all.find(l => l.id === id)?.is_default}
                    <div title="Default Location" class="text-accent">
                        <House size={10} fill="currentColor" class="opacity-80" />
                    </div>
                {/if}
                {#if locStore.effectiveActiveId === id}
                    <span class="text-[9px] font-bold text-accent uppercase tracking-tighter bg-accent/10 px-1.5 py-0.5 rounded">
                        {m.dash_location_selected()}
                    </span>
                {/if}
            </div>
            <div class="flex items-center gap-3 text-[11px] font-mono text-copy-muted mt-1 opacity-80">
                <span>{lat.toFixed(4)}°, {lng.toFixed(4)}°</span>
                <span class="opacity-30">•</span>
                <span>{elevation}m</span>
                <span>UTC{formattedTZ}</span>
            </div>
        </div>
    </button>

    <div class="absolute right-3 transition-all
                opacity-0 group-hover:opacity-100 translate-x-2 group-hover:translate-x-0
                [@media(hover:none)]:opacity-100 [@media(hover:none)]:translate-x-0">
        <button 
            // onclick={(e) => { e.stopPropagation(); locStore.deleteLocation(id); }}
            onclick={() => showDeleteModal = true}
            class="cursor-pointer p-2 rounded-lg bg-panel border border-border text-copy-muted hover:text-danger hover:border-danger/30 transition-all shadow-sm">
            <Trash2 size={14} />
        </button>
    </div>
</div>
<!-- Delete Modal -->
<Modal bind:open={showDeleteModal} title={m.dash_location_del_title()} size="sm">
    <p class="text-sm text-copy-muted mb-6">
        {m.dash_location_del_title_prefix()}
        <span class="text-copy-primary font-medium">"{label}"</span>
        {m.dash_location_del_title_suffix()}
    </p>
    <div class="flex justify-end gap-3">
        <button onclick={() => showDeleteModal = false} class="cursor-pointer px-4 py-2 text-sm font-medium text-copy-muted hover:text-copy-primary">
            {m.dash_location_action_cancel()}
        </button>
        <button onclick={handleDelete} class="cursor-pointer px-4 py-2 bg-danger-surface hover:opacity-90 text-danger text-sm font-bold rounded-xl transition-all shadow-lg shadow-danger-surface/20">
            {m.dash_location_action_delete()}
        </button>
    </div>
</Modal>
