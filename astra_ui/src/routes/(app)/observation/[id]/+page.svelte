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
	import TelescopePill from '$lib/components/observation/TelescopePill.svelte';
	import SideDock from '$lib/components/observation/SideDock.svelte';
	import SkyFinder from '$lib/components/observation/SkyFinder.svelte';
	import TargetInfo from '$lib/components/observation/TargetInfo.svelte';
	import Chat from '$lib/components/observationAssistant/Chat.svelte';
	import { activeObs } from '$lib/stores/activeObservation.svelte';

    // So we can call fly whenever we want
    let skyMap = $state<ReturnType<typeof SkyMap3D>>();

    // Sky settings
    let showConstellations = $state(true);
    let showGround         = $state(true);
    
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
                cardinal: '#f87171'       
            };
        }
        return {
            ground: 0x02120a, //02170d, //0f172a         
            constellations: 0x30318e,//475569, 
            cardinal: '#94a3b8'       
        };
    });

    onMount(() => {
        return () => {
            if (!timeEngine.isLive) timeEngine.setLive(true);
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
                groundColor={simColors.ground}
                constellationColor={simColors.constellations}
                cardinalColor={simColors.cardinal}
            />
        {:else}
            <div class="w-full h-full flex flex-col items-center justify-center gap-4 bg-black">
                <div class="w-12 h-12 border-4 border-accent/30 border-t-accent rounded-full animate-spin"></div>
            </div>
        {/if}
    </div>

    <!-- Telescope status -->
    <div class="absolute top-6 left-5 z-10 pointer-events-auto">
        <TelescopePill/>
    </div>

    <!-- Options dock -->
    <div class="absolute left-4 top-1/2 -translate-y-1/2 z-20 pointer-events-auto">
        <SideDock 
            bind:showConstellations 
            bind:showGround 
            bind:searchOpen 
            bind:chatOpen 
        />
    </div>

    <!-- Target info -->
    <div class="absolute top-6 right-6 z-10 pointer-events-none">
        {#if !chatOpen}
            <TargetInfo onFlyTo={(alt, az) => skyMap?.flyTo(alt, az)} />
        {/if}
    </div>

    <!-- Time control -->
    <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex justify-center w-full pointer-events-none">
        <TimeController />
    </div>

    <!-- AI chat -->
    <Chat bind:open={chatOpen} />

    <!-- SkyFinder object searcher -->
    <SkyFinder bind:open={searchOpen} onSelect={(id) => skyMap?.selectObject(id)} />

</div>