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

<!-- src/lib/components/observation/TargetDetailsPanel.svelte -->
<script lang="ts">
    import { fade } from 'svelte/transition';
    import { Target, X, Crosshair, LoaderCircle, Telescope, Sunrise, Sunset, Navigation, Info, Lightbulb, Eye, Image, ExternalLink } from 'lucide-svelte';
    import { fly } from 'svelte/transition';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { skyEngine } from '$lib/stores/skyEngine.svelte';
    import type { PlanetaryObjectDetails, SiderealObjectDetails } from '$lib/types/sideris';
    import { m } from '$lib/paraglide/messages';
    import { deviceStore } from '$lib/stores/devices.svelte';
    import { deviceAPI } from '$lib/api/devices';
    import { CoordinateTypes } from '$lib/types/devices';
    import { getLocale } from '$lib/paraglide/runtime';
    import { getImageUrl, buildDynamicStats, getWikipediaUrl } from '$lib/components/observation/targetDetailsPanelComponents/targetDetailsHelper';
	import MoonInfoCard from './targetDetailsPanelComponents/MoonInfoCard.svelte';
	import RiseSetCard from './targetDetailsPanelComponents/RiseSetCard.svelte';
	import InfoBlockCard from './targetDetailsPanelComponents/InfoBlockCard.svelte';
	import PlanetInfoCard from './targetDetailsPanelComponents/PlanetInfoCard.svelte';
	import { translateObjectType } from '$lib/utils/i18n';
    import { onMount } from 'svelte';

    let { onFlyTo, onClear } = $props<{ 
        onFlyTo: (alt: number, az: number) => void; 
        onClear: () => void; 
    }>();

    // -- State & Derived --
    const isTelescopeReady = $derived(
        deviceStore.activeDetails?.is_online && 
        deviceStore.effectiveActiveId && 
        deviceStore.activeComponents?.telescope
    );
    let isSlewing = $state(false);
    let imageLoadError = $state(false);
    let imageLoaded = $state(false);

    // -- Responsive & Gesture State --
    let isPortrait = $state(false);
    let isMobileLandscape = $state(false);
    let viewMode = $state<'collapsed' | 'expanded'>('collapsed');
    let dragY = $state(0);
    let isDragging = $state(false);
    let startY = 0;

    function formatTime(isoString: string | null | undefined) {
        if (!isoString) return '—';
        return new Date(isoString).toLocaleTimeString(getLocale(), { hour: '2-digit', minute: '2-digit' });
    }

    const selectedInfo = $derived.by(() => {
        const id = selectionStore.targetId;
        const details = selectionStore.targetDetails;
        const dynamicData = skyEngine.positions.get(id || '');
        if (!id || !details || !dynamicData) return null;
        const isPlanet = selectionStore.targetType === 'planetary';
        const imageUrl = getImageUrl(details, isPlanet);
        const { stats, ephemeris } = buildDynamicStats(details, dynamicData, isPlanet);
        const wikipediaUrl = getWikipediaUrl(details.wikipedia_qid);

        return {
            id,
            name: details.name || id,
            category: details.category,
            imageUrl,
            wikipediaUrl,
            stats, 
            alt: dynamicData.alt,
            az: dynamicData.az,
            ra: details.ra_j2000,
            dec: details.dec_j2000,
            rise: formatTime(ephemeris.rise),
            set: formatTime(ephemeris.set),
            transit: formatTime(ephemeris.transit),
            description: details.description,
            funFact: details.fun_fact,
            visualTip: details.visual_tip,
            extraDetails: isPlanet ? (details as PlanetaryObjectDetails).extra_details : null 
        };
    });
    
    $effect(() => {
        selectionStore.targetId;
        imageLoadError = false;
        imageLoaded = false;
        isSlewing = false;
        viewMode = 'collapsed'; // Reset on target change
    });

    onMount(() => {
        const updateMedia = () => {
            isPortrait = window.matchMedia("(orientation: portrait)").matches;
            isMobileLandscape = window.matchMedia("(orientation: landscape) and (max-width: 1023px)").matches;
        };
        updateMedia();
        window.addEventListener("resize", updateMedia);
        return () => window.removeEventListener("resize", updateMedia);
    });

    /**
     * Handles the start of a pointer gesture for swiping the panel
     * @param {PointerEvent} e - The pointer down event
     */
    function handlePointerDown(e: PointerEvent) {
        if (!isPortrait) return; // Only gestures on portrait
        isDragging = true;
        startY = e.clientY;
        (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    }

    /**
     * Handles pointer movement during a swipe gesture
     * @param {PointerEvent} e - The pointer move event
     */
    function handlePointerMove(e: PointerEvent) {
        if (!isDragging) return;
        dragY = e.clientY - startY;
    }

    /**
     * Handles the end of a pointer gesture and determines swipe actions
     */
    function handlePointerUp() {
        if (!isDragging) return;
        isDragging = false;

        if (dragY > 100) { // Swiped DOWN
            if (viewMode === 'expanded') viewMode = 'collapsed';
            else onClear();
        } else if (dragY < -100) { // Swiped UP
            if (viewMode === 'collapsed') viewMode = 'expanded';
        }
        dragY = 0;
    }

    /**
     * Sends a command to the active telescope to slew to and track the selected target
     */
    async function handleSlewAndTrack() {
        if (!isTelescopeReady || !selectedInfo) return;
        const deviceId = deviceStore.effectiveActiveId!;
        const telescopeId = deviceStore.activeComponents!.telescope!;
        isSlewing = true;
        try {
            await deviceAPI.slewTelescope(deviceId, telescopeId, {
                coord: [selectedInfo.alt, selectedInfo.az],
                input_type: CoordinateTypes.HORIZONTAL,
                mode: "TRACK" 
            });
        } catch (error) {
            console.error("Error sending slew to telescope:", error);
        } finally {
            isSlewing = false;
        }
    }
</script>

{#if selectionStore.targetId}
    <div 
        transition:fly={isPortrait ? { y: 200, duration: 300 } : (isMobileLandscape ? { scale: 0.9, duration: 300 } : { x: 50, duration: 300 })} 
        class="flex flex-col bg-surface backdrop-blur-xl border border-border transition-all duration-300 pointer-events-auto overflow-hidden
               {isPortrait ? (viewMode === 'expanded' ? 'h-[90dvh]' : 'h-[55dvh]') : 'h-full landscape:h-full md:landscape:h-auto'}
               {isPortrait ? 'w-full rounded-t-3xl rounded-b-none' : 'landscape:w-full md:landscape:w-100 lg:w-100 rounded-3xl md:landscape:rounded-3xl lg:rounded-3xl'}
               {isPortrait ? 'shadow-[0_-8px_32px_rgba(0,0,0,0.3)]' : 'shadow-[0_8px_32px_rgba(0,0,0,0.3)]'}
               {isPortrait ? '' : 'landscape:max-h-[80vh] md:landscape:max-h-[70vh] 2xl:landscape:max-h-[92vh]'}
               {!isPortrait && !isMobileLandscape ? 'border-border/60' : ''}"
        style="transform: translateY({isDragging ? dragY : 0}px)"
    >
        <!-- Drag Handle / Header Area for Gestures -->
        <div 
            onpointerdown={handlePointerDown}
            onpointermove={handlePointerMove}
            onpointerup={handlePointerUp}
            onpointercancel={handlePointerUp}
            class="shrink-0 touch-none select-none"
        >
            <!-- Visual Handle -->
            <div class="w-full flex justify-center pt-3 pb-1 landscape:hidden shrink-0">
                <div class="w-12 h-1.5 bg-border/40 rounded-full"></div>
            </div>

            <!-- Header Content -->
            <div class="p-5 pb-4 border-b border-border/50">
                <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                        <div class="flex items-center gap-2 mb-1.5 drop-shadow-[0_0_5px_var(--color-accent-glow)]">
                            <Target size={14} class="text-accent animate-pulse" />
                            <span class="text-[10px] font-bold text-accent uppercase tracking-widest">{m.obs_targetinfo_title()}</span>
                        </div>
                        {#if selectionStore.isLoadingDetails && !selectedInfo}
                            <div class="h-6 w-32 bg-panel rounded animate-pulse mb-1"></div>
                            <div class="h-4 w-20 bg-panel rounded animate-pulse"></div>
                        {:else if selectedInfo}
                            <h2 class="text-xl font-bold text-copy-primary leading-tight truncate" title={selectedInfo.name}>{selectedInfo.name}</h2>
                            <p class="text-xs text-copy-muted mt-1 truncate">{translateObjectType(selectedInfo.category)}</p>
                        {/if}
                    </div>

                    <button onclick={onClear} class="cursor-pointer p-1.5 text-copy-muted hover:text-white rounded-full hover:bg-panel/50 transition-colors shrink-0">
                        <X size={18}/>
                    </button>
                </div>
            </div>
        </div>

        <!-- Content -->
        <div class="p-4 landscape:p-5 overflow-y-auto custom-scrollbar flex-1 space-y-5">
            
            <!-- --- Image --- -->
            {#if selectedInfo && selectedInfo.imageUrl && !imageLoadError}
                <div class="aspect-16/10 w-full rounded-2xl border border-border/50 bg-panel/30 overflow-hidden relative shadow-inner group shrink-0">
                    {#if !imageLoaded}
                        <div class="absolute inset-0 flex flex-col items-center justify-center" out:fade={{ duration: 300 }}>
                            <Image size={28} class="text-copy-muted/40 animate-pulse" />
                        </div>
                    {/if}

                    <img 
                        src={selectedInfo.imageUrl} 
                        alt={selectedInfo.name}
                        class="w-full h-full object-cover rounded-2xl transition-all duration-700 group-hover:scale-105 {imageLoaded ? 'opacity-100' : 'opacity-0'}"
                        onload={() => imageLoaded = true}
                        onerror={() => imageLoadError = true}
                    />
                </div>
            {/if}

            <!-- Primary Stats Grid -->
            <div class="grid grid-cols-2 gap-3">
                {#if selectionStore.isLoadingDetails && !selectedInfo}
                    {#each Array(4) as _}
                        <div class="bg-panel/40 rounded-xl p-3 border border-border shadow-inner animate-pulse">
                            <div class="h-2 w-12 bg-panel rounded mb-2"></div>
                            <div class="h-4 w-16 bg-panel rounded"></div>
                        </div>
                    {/each}
                {:else if selectedInfo}
                    {#each selectedInfo.stats as stat}
                        <div class="rounded-xl p-3 border shadow-inner transition-colors bg-panel/40 hover:bg-panel/60 border-transparent hover:border-border">
                            <p class="text-[9px] uppercase tracking-wider text-copy-muted mb-1">{stat.label}</p>
                            <p class="text-sm font-semibold text-copy-primary font-mono tabular-nums">{stat.value}</p>
                        </div>
                    {/each}
                {/if}
            </div>
            
            <!-- Special cards -->
            {#if selectedInfo?.extraDetails}
                {#if selectedInfo.extraDetails.category === 'moon'}
                    <MoonInfoCard 
                        age={selectedInfo.extraDetails.age} 
                        illuminationPct={selectedInfo.extraDetails.illumination_pct} 
                        nextNewMoon={selectedInfo.extraDetails.next_new_moon}
                        nextFullMoon={selectedInfo.extraDetails.next_full_moon}
                    />
                {/if}
                {#if selectedInfo.extraDetails.category === 'planet'}
                    <PlanetInfoCard 
                        id={selectedInfo.id}
                        illuminationPct={selectedInfo.extraDetails.illumination_pct}
                        elongationDeg={selectedInfo.extraDetails.elongation_deg}
                    />
                {/if}
            {/if}
            

            <!-- --- Rise-Set --- -->
            {#if selectedInfo}
                <RiseSetCard 
                    rise={selectedInfo.rise} 
                    transit={selectedInfo.transit} 
                    set={selectedInfo.set} 
                />

                <!-- Object Description -->
                {#if selectedInfo.description || selectedInfo.funFact || selectedInfo.visualTip || selectedInfo.wikipediaUrl}
                    <div class="space-y-4 pt-2">
                        
                        <!-- Wikipedia link  button -->
                        {#snippet wikiLink()}
                            <a 
                                href={selectedInfo.wikipediaUrl} 
                                target="_blank" 
                                rel="noopener noreferrer" 
                                class="flex items-center gap-1 text-[9px] font-bold text-accent hover:text-accent-hover uppercase tracking-wider transition-colors"
                            >
                                Wikipedia <ExternalLink size={10} />
                            </a>
                        {/snippet}

                        <InfoBlockCard 
                            title={m.obs_targetinfo_description()} 
                            text={selectedInfo.description} 
                            icon={Info} 
                            headerAction={selectedInfo.wikipediaUrl ? wikiLink : undefined} 
                        />

                        <InfoBlockCard 
                            title={m.obs_targetinfo_fun_fact()} 
                            text={selectedInfo.funFact} 
                            icon={Lightbulb} 
                            variant="funFact" 
                        />

                        <InfoBlockCard 
                            title={m.obs_targetinfo_visual_tip()} 
                            text={selectedInfo.visualTip} 
                            icon={Eye} 
                            variant="visualTip" 
                        />
                        
                    </div>
                {/if}
            {/if}
        </div>

        <!-- Footer / Actions -->
        <div class="p-5 border-t border-border/50 shrink-0 flex flex-col gap-2 bg-surface/50">
            <button 
                onclick={() => selectedInfo && onFlyTo(selectedInfo.alt, selectedInfo.az)} 
                disabled={!selectedInfo}
                class="cursor-pointer w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-panel/50 border border-border hover:border-accent/50 hover:bg-surface text-copy-primary text-xs font-bold transition-all shadow-inner group disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Crosshair size={16} class="group-hover:rotate-90 transition-transform text-accent" />
                {m.obs_targetinfo_center()}
            </button>
            
            {#if isTelescopeReady}
                <button 
                    onclick={handleSlewAndTrack} 
                    disabled={isSlewing || !selectedInfo}
                    class="cursor-pointer w-full flex items-center justify-center gap-2 py-2.5 rounded-xl transition-all shadow-[0_0_15px_rgba(0,0,0,0.1)] text-xs font-bold
                    {isSlewing ? 'bg-accent/50 text-white cursor-not-allowed' : 'bg-accent hover:bg-accent-hover text-white hover:shadow-[0_0_20px_var(--color-accent-glow)]'}
                    disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {#if isSlewing}
                        <LoaderCircle size={16} class="animate-spin" />
                        {m.obs_targetinfo_slewing()}
                    {:else}
                        <Telescope size={16} />
                        {m.obs_targetinfo_slew()}
                    {/if}
                </button>
            {/if}
        </div>
    </div>
{/if}

<style>
    /* 
     * Scrollbar for Gecko
     */
    .custom-scrollbar {
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
    }

    /* 
     * Scrollbar for Blink/Webkit
     */
    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
</style>