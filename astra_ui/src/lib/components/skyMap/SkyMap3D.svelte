<!-- src/lib/components/skyMap/SkyMap3D.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { SkyMap3DEngine } from './core/SkyMap3DEngine';

    let {
        showGround = true,
        groundColor = 0x0f172a,
        starOpacity = 0.8,
        cardinalColor = '#94a3b8',
        showConstellations = true,
        constellationColor = 0x475569,
        constellationLabelColor=0x7879c5,
        constellationOpacity = 0.4,
        showConstellationLabels = true,
        useLatinConstellations = true 
    } = $props();

    let container: HTMLDivElement;
    let engine: SkyMap3DEngine;

    // Props reactivity
    $effect(() => {
        const currentProps = { 
            showGround, 
            groundColor, 
            showConstellations, 
            constellationColor,
            constellationLabelColor,
            constellationOpacity,
            showConstellationLabels,
            useLatinConstellations  
        };

        if (engine) {
            engine.updateProps(currentProps);
        }
    });

    onMount(() => {
        // Startup
        engine = new SkyMap3DEngine(container, {
            groundColor, cardinalColor, starOpacity, constellationColor, constellationLabelColor, constellationOpacity, showConstellationLabels, useLatinConstellations
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
</script>

<div class="w-full h-full relative group">
    <div bind:this={container} class="w-full h-full bg-transparent rounded-3xl overflow-hidden"></div>
</div>