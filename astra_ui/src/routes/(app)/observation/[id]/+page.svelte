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

<!-- src/routes/(app)/dashboard/observation/[id]/+page.svelte -->
<script lang="ts">
    import { onMount, untrack} from 'svelte'; 
    import { browser } from '$app/environment';
    import { fade } from 'svelte/transition';
    import * as m from '$lib/paraglide/messages.js';
    import SkyMap3D from '$lib/components/skyMap/SkyMap3D.svelte';
    import TimeController from '$lib/components/observation/TimeController.svelte';
    import { catalogStore } from '$lib/stores/skyCatalog.svelte';
    import { timeEngine } from '$lib/stores/timeEngine.svelte';
    import { themeState } from '$lib/themes/themes.svelte';
	import SideDock from '$lib/components/observation/SideDock.svelte';
	import SkyFinder from '$lib/components/observation/SkyFinder.svelte';
	import TargetDetailsPanel from '$lib/components/observation/TargetDetailsPanel.svelte';
	import Chat from '$lib/components/observationAssistant/Chat.svelte';
	import { activeObs } from '$lib/stores/activeObservation.svelte';
    import { deviceStore } from '$lib/stores/devices.svelte';

	import TelescopeController from '$lib/components/observation/TelescopeController.svelte';
	import { deviceAPI } from '$lib/api/devices';
	import { chatStore } from '$lib/stores/chat.svelte';
	import { selectionStore } from '$lib/stores/activeSelection.svelte';
	import { skyEngine } from '$lib/stores/skyEngine.svelte';
    import { executeFrontendAction, type ChatAction } from '$lib/utils/frontendActions';

    // So we can call fly whenever we want
    let skyMap = $state<ReturnType<typeof SkyMap3D>>();
    let telescopePos = $state<{alt: number, az: number} | null>(null);

    // Sky settings
    let showConstellations = $state(false);
    let showGround         = $state(true);
    let solidGround        = $state(true);
    let showAtmosphere     = $state(true);
    let showConstellationLabels = $state(true);
    let useLatinConstellations = $state(true);
    
    // Panels
    let chatOpen       = $state(false);
    let searchOpen     = $state(false);

    const effectiveShowAtmosphere = $derived(themeState.current === 'astronomical' ? false : showAtmosphere);

    // Sun altitude for UI contrast
    const isDaytime = $derived.by(() => {
        if (!effectiveShowAtmosphere) return false;
        const sunPos = skyEngine.positions.get('sun');
        return sunPos ? sunPos.alt > -6.0 : false; // End of twilight threshold
    });

    // Only dark themes
    $effect(() => {
        if (!browser) return;
        const current = themeState.current;
        const targetTheme = current === 'light' ? 'standard' : current;

        document.documentElement.setAttribute('data-theme', targetTheme);
        document.documentElement.style.colorScheme = 'dark';

        // Apply daytime UI contrast
        if (isDaytime) {
            document.documentElement.classList.add('daytime-ui');
        } else {
            document.documentElement.classList.remove('daytime-ui');
        }

        return () => {
            document.documentElement.setAttribute('data-theme', themeState.current);
            document.documentElement.style.colorScheme = '';
            document.documentElement.classList.remove('daytime-ui');
        };
    });

    // Sky color
    const simColors = $derived.by(() => {
        if (themeState.current === 'astronomical') {
            return {
                ground: 0x160404,//1f0505,         
                constellations: 0x991b1b, 
                constellationLabelColor: 0xff4444,
                cardinal: '#ff0000' //'#f87171'       
            };
        }
        return {
            ground: 0x02120a, //02170d, //0f172a         
            constellations: 0x30318e,//475569, 
            constellationLabelColor: 0x7879c5,
            cardinal: '#ff0000' //'#94a3b8'       
        };
    });

    // Cardinal translations
    const cardinalLabels = $derived({
        'N' : m.cardinal_north(),
        'NE': m.cardinal_northeast(),
        'E' : m.cardinal_east(),
        'SE': m.cardinal_southeast(),
        'S' : m.cardinal_south(),
        'SW': m.cardinal_southwest(),
        'W' : m.cardinal_west(),
        'NW': m.cardinal_northwest()
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
                console.error("Error trying to get telescope position:", e);
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


    $effect(() => {
        if (chatStore.pendingActions.length > 0) {
            untrack(() => {
                // Grab the oldest action off the queue
                const action = chatStore.consumeAction();
                if (action) {
                    console.log("[Observation Page] Consumed action from chatStore:", action);
                    executeFrontendAction(action, {skyMap, selectionStore});
                }
            });
        }
    });

    onMount(() => {
        posInterval = setInterval(pollTelescopePosition, 1000);
        return () => {
            chatStore.clearPendingActions();
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
    <div class="absolute inset-0 bg-black">
        {#if catalogStore.isLoaded}
            <div in:fade={{ duration: 400 }} class="w-full h-full">
                <SkyMap3D 
                    bind:this={skyMap} 
                    {showGround} 
                    {solidGround}
                    {showConstellations} 
                    {showConstellationLabels}
                    {useLatinConstellations}
                    showAtmosphere={effectiveShowAtmosphere}
                    groundColor={simColors.ground}
                    constellationColor={simColors.constellations}
                    constellationLabelColor={simColors.constellationLabelColor}
                    cardinalColor={simColors.cardinal}
                    {cardinalLabels}
                />
            </div>
        {/if}
    </div>

    <!-- Telescope control -->
    <div class="absolute top-4 left-4 md:top-6 md:left-5 z-30 pointer-events-auto scale-90 md:scale-100 origin-top-left transition-transform">
        <TelescopeController
            canCenter={telescopePos !== null} 
            onCenter={centerOnTelescope} 
        />
    </div>

    <!-- Options dock -->
    <div class="absolute left-2 md:left-4 top-1/2 -translate-y-1/2 z-20 pointer-events-auto scale-90 md:scale-100 origin-left transition-transform">
        <SideDock 
            bind:showConstellations 
            bind:showConstellationLabels
            bind:useLatinConstellations
            bind:showGround 
            bind:solidGround
            bind:showAtmosphere
            atmosphereLocked={themeState.current === 'astronomical'}
            bind:searchOpen 
            bind:chatOpen 
        />
    </div>

    <!-- Target info -->
    <div class="fixed inset-x-0 bottom-0 z-40 w-full 
                landscape:inset-0 landscape:h-[100dvh] landscape:bottom-auto landscape:z-50 landscape:scale-100
                md:landscape:absolute md:landscape:inset-auto md:landscape:top-6 md:landscape:right-6 md:landscape:bottom-auto md:landscape:z-10 md:landscape:w-auto
                lg:absolute lg:inset-auto lg:top-6 lg:right-6 lg:bottom-auto lg:h-auto lg:z-10 lg:w-auto
                pointer-events-none scale-90 lg:scale-100 origin-bottom landscape:origin-center lg:origin-top-right transition-all">
        {#if !chatOpen}
            <TargetDetailsPanel 
                onFlyTo={(alt, az) => skyMap?.flyTo(alt, az)} 
                onClear={() => skyMap?.clearSelection()}
            />
        {/if}
    </div>

    <!-- Time control -->
    <div class="absolute bottom-2 md:bottom-4 lg:bottom-6 left-1/2 -translate-x-1/2 z-10 flex justify-center w-[96%] md:w-max max-w-full pointer-events-none transition-all scale-90 lg:scale-100 origin-bottom">
        <TimeController />
    </div>

    <!-- AI chat -->
    <Chat bind:open={chatOpen} 
          onClear={() => skyMap?.clearSelection()}
    />

    <!-- SkyFinder object searcher -->
    <SkyFinder 
        bind:open={searchOpen} 
        onSelect={(id) => {
            const isConstellation = catalogStore.constellations.some(c => c.abbr === id);
            if (isConstellation) {
                skyMap?.flyToConstellation(id);
            } else {
                skyMap?.selectObject(id);
            }
        }} 
    />  

</div>