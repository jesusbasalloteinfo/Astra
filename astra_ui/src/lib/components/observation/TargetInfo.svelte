<!-- src/lib/components/simulator/TargetInfo.svelte -->
<script lang="ts">
    import { Target, X, Crosshair } from 'lucide-svelte';
    import { fade } from 'svelte/transition';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { catalogStore } from '$lib/stores/skyCatalog.svelte';
    import { skyEngine } from '$lib/stores/skyEngine.svelte';
	import type { PlanetaryObjectMetadata, SiderealObjectMetadata } from '$lib/types/sideris';
	import { m } from '$lib/paraglide/messages';

    let { onFlyTo } = $props<{ onFlyTo: (alt: number, az: number) => void }>();

    const selectedInfo = $derived.by(() => {
        const id = selectionStore.targetId;
        if (!id) return null;

        const isPlanet = !!catalogStore.planetaryData[id];
        const staticData:SiderealObjectMetadata|PlanetaryObjectMetadata = isPlanet ? catalogStore.planetaryData[id] : catalogStore.siderealData[id];
        const dynamicData = skyEngine.positions.get(id);

        if (!staticData || !dynamicData) return null;
        let type = "Planetary";
        let dist = null;
        let distUnit= isPlanet? "AU" :  "LY"
        if (!isPlanet) {
            type = (staticData as SiderealObjectMetadata).type;
            type= type.charAt(0).toUpperCase() + type.slice(1)
            dist = (staticData as SiderealObjectMetadata).distance_ly
        }
        else{
            dist=staticData.dist
        }

        return {
            name: staticData.name || id,
            type: type,
            alt: dynamicData.alt,
            az: dynamicData.az,
            magnitude: staticData.mag !== undefined ? staticData.mag : (staticData.vmag ?? '—'),
            distance: dist ? `${dist} ${distUnit}` : '—'
        };
    });
</script>

{#if selectedInfo}
    <div transition:fade={{ duration: 200 }} class="w-72 bg-surface backdrop-blur-xl border border-border rounded-3xl p-5 shadow-[0_8px_32px_rgba(0,0,0,0.3)] pointer-events-auto">
        <div class="flex items-start justify-between mb-5">
            <div>
                <div class="flex items-center gap-2 mb-1.5 drop-shadow-[0_0_5px_var(--color-accent-glow)]">
                    <Target size={14} class="text-accent animate-pulse" />
                    <span class="text-[10px] font-bold text-accent uppercase tracking-widest">{m.obs_targetinfo_title()}</span>
                </div>
                <h2 class="text-xl font-bold text-copy-primary leading-tight">{selectedInfo.name}</h2>
                <p class="text-xs text-copy-muted mt-1">{selectedInfo.type}</p>
            </div>
            <button onclick={() => selectionStore.clear()} class="cursor-pointer p-1 text-copy-muted hover:text-white rounded-full"><X size={16}/></button>
        </div>

        <div class="grid grid-cols-2 gap-3">
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
        </div>

        <button onclick={() => onFlyTo(selectedInfo.alt, selectedInfo.az)} class="cursor-pointer w-full mt-5 flex items-center justify-center gap-2 py-3 rounded-xl bg-panel/50 border border-border hover:border-accent/50 hover:bg-surface text-copy-primary text-xs font-bold transition-all shadow-inner group">
            <Crosshair size={16} class="group-hover:rotate-90 transition-transform text-accent" />
            {m.obs_targetinfo_center()}
        </button>
    </div>
{/if}