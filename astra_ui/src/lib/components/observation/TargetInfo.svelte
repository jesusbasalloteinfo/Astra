<!-- src/lib/components/observation/TargetInfo.svelte -->
<script lang="ts">
    import { Target, X, Crosshair, LoaderCircle, Telescope } from 'lucide-svelte';
    import { fade } from 'svelte/transition';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { skyEngine } from '$lib/stores/skyEngine.svelte';
	import type { PlanetaryObjectDetails, SiderealObjectDetails } from '$lib/types/sideris';
	import { m } from '$lib/paraglide/messages';
	import { deviceStore } from '$lib/stores/devices.svelte';
	import { deviceAPI } from '$lib/api/devices';
	import { CoordinateTypes } from '$lib/types/devices';

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
        
        if (!isPlanet) {
            const sidereal = details as SiderealObjectDetails;
            type = sidereal.type;
            type = type.charAt(0).toUpperCase() + type.slice(1);
            dist = sidereal.distance_ly;
        } else {
            const planetary = details as PlanetaryObjectDetails;
            dist = planetary.dist;
        }
        console.log({
            id: id,
            name: details.name || id,
            type: type,
            alt: dynamicData.alt,
            az: dynamicData.az,
            ra: details.ra_j2000,
            dec: details.dec_j2000,
            magnitude: details.mag !== undefined && details.mag !== null ? details.mag : '—',
            distance: dist ? `${dist.toFixed(isPlanet ? 2 : 1)} ${distUnit}` : '—'
        })
        return {
            id: id,
            name: details.name || id,
            type: type,
            alt: dynamicData.alt,
            az: dynamicData.az,
            ra: details.ra_j2000,
            dec: details.dec_j2000,
            magnitude: details.mag !== undefined && details.mag !== null ? details.mag : '—',
            distance: dist ? `${dist.toFixed(isPlanet ? 2 : 1)} ${distUnit}` : '—'
        };
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
    <div transition:fade={{ duration: 200 }} class="w-72 bg-surface backdrop-blur-xl border border-border rounded-3xl p-5 shadow-[0_8px_32px_rgba(0,0,0,0.3)] pointer-events-auto">
        <div class="flex items-start justify-between mb-5">
            <div>
                <div class="flex items-center gap-2 mb-1.5 drop-shadow-[0_0_5px_var(--color-accent-glow)]">
                    <Target size={14} class="text-accent animate-pulse" />
                    <span class="text-[10px] font-bold text-accent uppercase tracking-widest">{m.obs_targetinfo_title()}</span>
                </div>
                {#if selectionStore.isLoadingDetails && !selectedInfo}
                    <div class="h-6 w-32 bg-panel rounded animate-pulse mb-1"></div>
                    <div class="h-4 w-20 bg-panel rounded animate-pulse"></div>
                {:else if selectedInfo}
                    <h2 class="text-xl font-bold text-copy-primary leading-tight">{selectedInfo.name}</h2>
                    <p class="text-xs text-copy-muted mt-1">{selectedInfo.type}</p>
                {/if}
            </div>

            <div class="flex items-start justify-between mb-5">
                <button onclick={onClear} class="cursor-pointer p-1 text-copy-muted hover:text-white rounded-full">
                    <X size={16}/>
                </button>
            </div>
        </div>

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
                    { label: 'Altitude',   value: `${selectedInfo.alt.toFixed(1)}°` },
                    { label: 'Azimuth',    value: `${selectedInfo.az.toFixed(1)}°`  },
                    { label: 'Magnitude',  value: selectedInfo.magnitude },
                    { label: 'Distance', value: selectedInfo.distance },
                ] as stat}
                    <div class="bg-panel/40 rounded-xl p-3 border border-border shadow-inner">
                        <p class="text-[9px] uppercase tracking-wider text-copy-muted mb-1">{stat.label}</p>
                        <p class="text-sm font-semibold text-copy-primary font-mono tabular-nums">{stat.value}</p>
                    </div>
                {/each}
            {/if}
        </div>
        
        <div class="mt-5 flex flex-col gap-2">
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
                        Sending...
                    {:else}
                        <Telescope size={16} />
                        Slew & Track
                    {/if}
                </button>
            {/if}
        </div>
    </div>
{/if}
