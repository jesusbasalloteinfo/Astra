<!-- src/lib/components/skyMap/SkyMap3D.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { SkyMap3DEngine } from './core/SkyMap3DEngine';

    let {
        showGround = true,
        groundColor = 0x0f172a,
        solidGround = true,
        starOpacity = 0.8,
        cardinalColor = '#94a3b8',
        cardinalLabels = null,
        showConstellations = false,
        constellationColor = 0x475569,
        constellationLabelColor=0x7879c5,
        constellationOpacity = 0.4,
        showConstellationLabels = true,
        useLatinConstellations = true,
        showAtmosphere = true 
    } = $props();

    let container: HTMLDivElement;
    let engine: SkyMap3DEngine;

    // Props reactivity
    $effect(() => {
        const currentProps = { 
            showGround, 
            groundColor, 
            solidGround,
            cardinalColor,
            cardinalLabels,
            showConstellations, 
            constellationColor,
            constellationLabelColor,
            constellationOpacity,
            showConstellationLabels,
            useLatinConstellations,
            showAtmosphere  
        };

        if (engine) {
            engine.updateProps(currentProps);
        }
    });

    onMount(() => {
        // Startup
        engine = new SkyMap3DEngine(container, {
            showGround,
            groundColor, 
            solidGround, 
            cardinalColor, 
            cardinalLabels,
            starOpacity, 
            showConstellations,
            constellationColor, 
            constellationLabelColor, 
            constellationOpacity, 
            showConstellationLabels, 
            useLatinConstellations,
            showAtmosphere
        });

        // Shutdown
        return () => engine.dispose();
    });

    export const flyTo = (alt: number, az: number) => {
        if (engine) engine.flyTo(alt, az);
    };

    export const flyToConstellation = (abbr: string) => {
        if (engine) engine.flyToConstellation(abbr);
    };
    
    export const selectObject = (id: string) => {
        if (engine) engine.selectObject(id);
    };

    export const clearSelection = () => {
        if (engine) engine.clearSelection();
    };

    export const updateTelescopePosition = (alt: number | null, az: number | null) => {
        if (engine) engine.setTelescopePosition(alt, az);
    };
</script>

<div class="w-full h-full relative group">
    <div bind:this={container} class="w-full h-full bg-transparent overflow-hidden"></div>
</div>