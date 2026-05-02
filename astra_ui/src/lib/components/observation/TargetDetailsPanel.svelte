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
	import { endpoints, siderisEndpoints } from '$lib/api/endpoints';
    import { getLocale } from '$lib/paraglide/runtime';

    let { onFlyTo, onClear } = $props<{ 
        onFlyTo: (alt: number, az: number) => void;
        onClear: () => void; 
    }>();

    const isTelescopeReady = $derived(
        deviceStore.activeDetails?.is_online && 
        deviceStore.effectiveActiveId && 
        deviceStore.activeComponents?.telescope
    );
    let isSlewing = $state(false);

    let imageLoadError = $state(false);

    function formatTime(isoString: string | null | undefined) {
        if (!isoString) return '—';
        return new Date(isoString).toLocaleTimeString(getLocale(), { hour: '2-digit', minute: '2-digit' });
    }

    const selectedInfo = $derived.by(() => {
        const id = selectionStore.targetId;
        const details = selectionStore.targetDetails;
        if (!id || !details) return null;

        const dynamicData = skyEngine.positions.get(id);
        if (!dynamicData) return null;

        const isPlanet = selectionStore.targetType === 'planetary';
        let type = "Planetary";
        let dist = null;
        let distUnit = isPlanet ? "AU" : "LY";
        
        let rise = null;
        let set = null;
        let transit = null;

        let imageUrl = null;
        if (isPlanet) {
            // Planetary image from static images
            const planetaryDetails = details as PlanetaryObjectDetails;
            
            if (planetaryDetails.image_url) {                
                imageUrl = `${endpoints.apiBase}${siderisEndpoints.base}${planetaryDetails.image_url}`;
            }
            
        } else {
            // Aladin HIPS image, generated on the go
            
            // Convert from hour format to 0..360
            let ra = details.ra_j2000 * 15;             
            const dec = details.dec_j2000;
            
            // FOV
            // Object size or 30 as default (size of the Moon)
            const sizeArcmin = (details as SiderealObjectDetails).size_arcmin || 30;
            
            // Convert to degrees and add a 1.5 spacing
            let fov = (sizeArcmin / 60) * 1.5; 
            
            // Security FOV limits
            if (fov < 0.1) fov = 0.1; // Max zoom
            if (fov > 10) fov = 10;   // Min zoom
            
            imageUrl = `https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FDSS2%2Fcolor&width=600&height=375&fov=${fov}&projection=TAN&coordsys=icrs&ra=${ra}&dec=${dec}&format=png`;
        }
        if (!isPlanet) {
            const sidereal = details as SiderealObjectDetails;
            type = sidereal.type;
            type = type.charAt(0).toUpperCase() + type.slice(1);
            dist = sidereal.distance_ly;
            rise = sidereal.next_rise;
            set = sidereal.next_set;
            transit = sidereal.next_transit;
        } else {
            const planetary = details as PlanetaryObjectDetails;
            dist = planetary.dist;
            rise = planetary.rise_set_transit?.next_rise;
            set = planetary.rise_set_transit?.next_set;
            transit = planetary.rise_set_transit?.next_transit;
        }

        let wikipediaUrl = null;
        if (details.wikipedia_qid) {
            const lang = getLocale();
            wikipediaUrl = `https://www.wikidata.org/wiki/Special:GoToLinkedPage/${lang}wiki/${details.wikipedia_qid}`;
        }
        return {
            id: id,
            name: details.name || id,
            type: type,
            imageUrl: imageUrl,
            wikipediaUrl: wikipediaUrl, 
            alt: dynamicData.alt,
            az: dynamicData.az,
            ra: details.ra_j2000,
            dec: details.dec_j2000,
            magnitude: details.mag !== undefined && details.mag !== null ? details.mag : '—',
            distance: dist ? `${dist.toFixed(isPlanet ? 2 : 1)} ${distUnit}` : '—',
            rise: formatTime(rise),
            set: formatTime(set),
            transit: formatTime(transit),
            description: details.description,
            funFact: details.fun_fact,
            visualTip: details.visual_tip
        };
    });

    // Reset error when changing target
    $effect(() => {
        selectionStore.targetId;
        imageLoadError = false;
    });

    async function handleSlewAndTrack() {
        if (!isTelescopeReady || !selectedInfo) return;
        
        const deviceId = deviceStore.effectiveActiveId!;
        const telescopeId = deviceStore.activeComponents!.telescope!;

        isSlewing = true;
        try {
            await deviceAPI.slewTelescope(deviceId, telescopeId, {
                coord: [selectedInfo.ra, selectedInfo.dec],
                input_type: CoordinateTypes.EQUATORIAL_J2000,
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
        transition:fly={{ x: 50, duration: 300 }} 
        class="w-100 max-h-[85vh] flex flex-col bg-surface backdrop-blur-xl border border-border rounded-3xl shadow-[0_8px_32px_rgba(0,0,0,0.3)] pointer-events-auto"
    >
        <!-- Header -->
        <div class="p-5 pb-4 border-b border-border/50 shrink-0">
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
                        <p class="text-xs text-copy-muted mt-1 truncate">{selectedInfo.type}</p>
                    {/if}
                </div>

                <button onclick={onClear} class="cursor-pointer p-1.5 text-copy-muted hover:text-white rounded-full hover:bg-panel/50 transition-colors shrink-0">
                    <X size={18}/>
                </button>
            </div>
        </div>

        <!-- Content -->
        <div class="p-5 overflow-y-auto custom-scrollbar flex-1 space-y-5">
            
            <!-- --- Image --- -->
            {#if selectedInfo && selectedInfo.imageUrl && !imageLoadError}
                <div class="aspect-16/10 w-full rounded-2xl border border-border/50 bg-panel/30 overflow-hidden relative shadow-inner group">
                        <img 
                            src={selectedInfo.imageUrl} 
                            alt={selectedInfo.name}
                            class="w-full h-full object-cover rounded-2xl transition-transform duration-700 group-hover:scale-105"
                            in:fade={{ duration: 400 }}
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
                    {#each [
                        { label: m.obs_targetinfo_alt() , value: `${selectedInfo.alt.toFixed(1)}°` },
                        { label: m.obs_targetinfo_az()  , value: `${selectedInfo.az.toFixed(1)}°`  },
                        { label: m.obs_targetinfo_mag() , value: selectedInfo.magnitude },
                        { label: m.obs_targetinfo_dist(), value: selectedInfo.distance },
                    ] as stat}
                        <div class="bg-panel/40 rounded-xl p-3 border shadow-inner transition-colors hover:bg-panel/60 border-transparent hover:border-border">
                            <p class="text-[9px] uppercase tracking-wider text-copy-muted mb-1">{stat.label}</p>
                            <p class="text-sm font-semibold text-copy-primary font-mono tabular-nums">{stat.value}</p>
                        </div>
                    {/each}
                {/if}
            </div>

            <!-- --- Rise-Set --- -->
            {#if selectedInfo}
                <div class="bg-panel/20 rounded-xl p-3 border border-border/50">
                    <h3 class="text-[10px] font-bold text-copy-muted uppercase tracking-widest mb-3">{m.obs_targetinfo_riseset_title()}</h3>
                    
                    <div class="grid grid-cols-3 items-center divide-x divide-border/50 text-copy-primary">
                        
                        <div class="flex flex-col items-center gap-1">
                            <Sunrise size={16} class="text-orange-400/80" />
                            <div class="flex flex-col items-center">
                                <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5">{m.obs_targetinfo_riseset_rise()}</span>
                                <span class="text-xs font-mono font-medium">{selectedInfo.rise}</span>
                            </div>
                        </div>
                        
                        <div class="flex flex-col items-center gap-1 pl-1">
                            <Navigation size={16} class="text-blue-400/80" />
                            <div class="flex flex-col items-center">
                                <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5">{m.obs_targetinfo_riseset_transit()}</span>
                                <span class="text-xs font-mono font-medium">{selectedInfo.transit}</span>
                            </div>
                        </div>
                        
                        <div class="flex flex-col items-center gap-1 pl-1">
                            <Sunset size={16} class="text-purple-400/80" />
                            <div class="flex flex-col items-center">
                                <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5">{m.obs_targetinfo_riseset_set()}</span>
                                <span class="text-xs font-mono font-medium">{selectedInfo.set}</span>
                            </div>
                        </div>
                        
                    </div>
                </div>

                <!-- Object Description -->
                {#if selectedInfo.description || selectedInfo.funFact || selectedInfo.visualTip}
                    <div class="space-y-4 pt-2">
                        {#if selectedInfo.description}
                            <div class="space-y-2">
                                <div class="flex items-center justify-between mb-1.5">
                                    <div class="flex items-center gap-1.5 text-copy-muted">
                                        <Info size={14} />
                                        <h3 class="text-[10px] font-bold uppercase tracking-widest">{m.obs_targetinfo_description()}</h3>
                                    </div>
                                    
                                    {#if selectedInfo.wikipediaUrl}
                                        <a 
                                            href={selectedInfo.wikipediaUrl} 
                                            target="_blank" 
                                            rel="noopener noreferrer" 
                                            class="flex items-center gap-1 text-[9px] font-bold text-accent hover:text-accent-hover uppercase tracking-wider transition-colors"
                                        >
                                            Wikipedia <ExternalLink size={10} />
                                        </a>
                                    {/if}
                                </div>
                                <div class="relative overflow-hidden bg-panel/30 p-4 rounded-xl border border-border shadow-inner group transition-colors hover:bg-panel/50">
                                    <div class="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-700 text-copy-muted">
                                        <Info size={64} strokeWidth={1} />
                                    </div>
                                    <p class="relative text-sm text-copy-primary/90 leading-relaxed whitespace-pre-wrap">
                                        {selectedInfo.description}
                                    </p>
                                </div>
                            </div>
                        {/if}
                        
                        {#if selectedInfo.funFact}
                            <div class="space-y-2">
                                <div class="flex items-center gap-1.5 text-copy-muted">
                                    <Lightbulb size={14} class="text-yellow-500/70" />
                                    <h3 class="text-[10px] font-bold uppercase tracking-widest">{m.obs_targetinfo_fun_fact()}</h3>
                                </div>
                                <div class="relative overflow-hidden bg-yellow-500/5 p-4 rounded-xl border border-yellow-500/10 shadow-inner group">
                                    <div class="absolute -right-4 -bottom-4 opacity-[0.07] group-hover:scale-110 transition-transform duration-700 text-yellow-500">
                                        <Lightbulb size={64} strokeWidth={1} />
                                    </div>
                                    <p class="relative text-sm text-copy-primary/90 leading-relaxed">
                                        {selectedInfo.funFact}
                                    </p>
                                </div>
                            </div>
                        {/if}

                        {#if selectedInfo.visualTip}
                            <div class="space-y-2">
                                <div class="flex items-center gap-1.5 text-copy-muted">
                                    <Eye size={14} class="text-blue-400/70" />
                                    <h3 class="text-[10px] font-bold uppercase tracking-widest">{m.obs_targetinfo_visual_tip()}</h3>
                                </div>
                                <div class="relative overflow-hidden bg-blue-400/5 p-4 rounded-xl border border-blue-400/10 shadow-inner group">
                                    <div class="absolute -right-4 -bottom-4 opacity-[0.07] group-hover:scale-110 transition-transform duration-700 text-blue-400">
                                        <Eye size={64} strokeWidth={1} />
                                    </div>
                                    <p class="relative text-sm text-copy-primary/90 leading-relaxed">
                                        {selectedInfo.visualTip}
                                    </p>
                                </div>
                            </div>
                        {/if}
                    </div>
                {/if}
            {/if}
        </div>

        <!-- Footer / Actions -->
        <div class="p-5 border-t border-border/50 shrink-0 flex flex-col gap-2">
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