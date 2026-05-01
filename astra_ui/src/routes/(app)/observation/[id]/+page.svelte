<!-- src/routes/(app)/dashboard/observation/[id]/+page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import * as m from '$lib/paraglide/messages.js';
    import SkyMap3D from '$lib/components/skyMap/SkyMap3D.svelte';
    import TimeController from '$lib/components/observation/TimeController.svelte';
    import { catalogStore } from '$lib/stores/skyCatalog.svelte';
    import { timeEngine } from '$lib/stores/timeEngine.svelte';
    import { themeState } from '$lib/themes/themes.svelte';
	import SideDock from '$lib/components/observation/SideDock.svelte';
	import SkyFinder from '$lib/components/observation/SkyFinder.svelte';
	import TargetInfo from '$lib/components/observation/TargetInfo.svelte';
	import Chat from '$lib/components/observationAssistant/Chat.svelte';
	import { activeObs } from '$lib/stores/activeObservation.svelte';
    import { deviceStore } from '$lib/stores/devices.svelte';

	import TelescopeController from '$lib/components/observation/TelescopeController.svelte';
	import { deviceAPI } from '$lib/api/devices';

    // So we can call fly whenever we want
    let skyMap = $state<ReturnType<typeof SkyMap3D>>();
    let telescopePos = $state<{alt: number, az: number} | null>(null);

    // Sky settings
    let showConstellations = $state(true);
    let showGround         = $state(true);
    let showConstellationLabels = $state(true);
    let useLatinConstellations = $state(true);
    
    // Panels
    let chatOpen       = $state(false);
    let searchOpen     = $state(false);

    // Only dark themes
    $effect(() => {
        if (!browser) return;
        const current = themeState.current;
        const targetTheme = current === 'light' ? 'standard' : current;

        document.documentElement.setAttribute('data-theme', targetTheme);
        document.documentElement.style.colorScheme = 'dark';

        return () => {
            document.documentElement.setAttribute('data-theme', themeState.current);
            document.documentElement.style.colorScheme = '';
        };
    });

    // Sky color
    const simColors = $derived.by(() => {
        if (themeState.current === 'astronomical') {
            return {
                ground: 0x160404,//1f0505,         
                constellations: 0x991b1b, 
                constellationLabelColor: 0xff4444,
                cardinal: '#f87171'       
            };
        }
        return {
            ground: 0x02120a, //02170d, //0f172a         
            constellations: 0x30318e,//475569, 
            constellationLabelColor: 0x7879c5,
            cardinal: '#94a3b8'       
        };
    });

    // --- Real Time telescope ---
    let posInterval: ReturnType<typeof setInterval>;

    async function pollTelescopePosition() {
        const activeId = deviceStore.effectiveActiveId;
        const activeTelescope = deviceStore.activeComponents?.telescope;
        
        const isOnline = deviceStore.activeDetails?.is_online ?? deviceStore.activeBase?.is_online ?? false;

        if (activeId && activeTelescope && isOnline) {
            try {
                const pos = await deviceAPI.getTelescopePos(activeId, activeTelescope)
                if (pos && pos.horizontal) {
                    skyMap?.updateTelescopePosition(pos.horizontal.alt, pos.horizontal.az);
                    telescopePos = { alt: pos.horizontal.alt, az: pos.horizontal.az };
                    return;
                }
            } catch (e) {
                console.error("Error trying to ge telescope position:", e);
            }
        }
        // Else hide the telescope pointer
        telescopePos = null;
        skyMap?.updateTelescopePosition(null, null);
    }
    function centerOnTelescope() {
        if (telescopePos) {
            skyMap?.flyTo(telescopePos.alt, telescopePos.az);
        }
    }

    onMount(() => {
        posInterval = setInterval(pollTelescopePosition, 1000);
        return () => {
            if (!timeEngine.isLive) timeEngine.setLive(true);
            if (posInterval) clearInterval(posInterval);
        };
    });
</script>

<svelte:head>
    <title>{m.obs_title({obs_title: activeObs.current?.name || m.obs(), name: m.name().toUpperCase()})}</title>
    <meta name="description" content={m.obs_title({obs_title: activeObs.current?.name || m.obs(), name: m.name().toUpperCase()})}/>
</svelte:head>

<div class="absolute inset-0 z-0 bg-black overflow-hidden pointer-events-auto text-copy-primary">

    <!-- 3D SkyMap -->
    <div class="absolute inset-0">
        {#if catalogStore.isLoaded}
            <SkyMap3D 
                bind:this={skyMap} 
                {showGround} 
                {showConstellations} 
                {showConstellationLabels}
                {useLatinConstellations}
                groundColor={simColors.ground}
                constellationColor={simColors.constellations}
                constellationLabelColor={simColors.constellationLabelColor}
                cardinalColor={simColors.cardinal}
                
            />
        {:else}
            <div class="w-full h-full flex flex-col items-center justify-center gap-4 bg-black">
                <div class="w-12 h-12 border-4 border-accent/30 border-t-accent rounded-full animate-spin"></div>
            </div>
        {/if}
    </div>

    <!-- Telescope control -->
    <div class="absolute top-6 left-5 z-10 pointer-events-auto">
        <TelescopeController
            canCenter={telescopePos !== null} 
            onCenter={centerOnTelescope} 
        />
    </div>

    <!-- Options dock -->
    <div class="absolute left-4 top-1/2 -translate-y-1/2 z-20 pointer-events-auto">
        <SideDock 
            bind:showConstellations 
            bind:showConstellationLabels
            bind:useLatinConstellations
            bind:showGround 
            bind:searchOpen 
            bind:chatOpen 
        />
    </div>

    <!-- Target info -->
    <div class="absolute top-6 right-6 z-10 pointer-events-none">
        {#if !chatOpen}
            <TargetInfo 
                onFlyTo={(alt, az) => skyMap?.flyTo(alt, az)} 
                onClear={() => skyMap?.clearSelection()}
            />
        {/if}
    </div>

    <!-- Time control -->
    <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex justify-center w-full pointer-events-none">
        <TimeController />
    </div>

    <!-- AI chat -->
    <Chat bind:open={chatOpen} />

    <!-- SkyFinder object searcher -->
    <SkyFinder 
        bind:open={searchOpen} 
        onSelect={(id) => {
            // IS a constellation
            const isConstellation = catalogStore.constellations.some(c => c.abbr === id);

            if (isConstellation) {
                skyMap?.flyToConstellation(id);
            } else {
                skyMap?.selectObject(id);
            }
        }} 
    />  

</div>