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
        constellationOpacity = 0.4
    } = $props();

    let container: HTMLDivElement;
    let engine: SkyMap3DEngine;

    // Props reactivity
    $effect(() => {
        if (engine) {
            engine.updateProps({ showGround, groundColor, showConstellations, constellationColor });
        }
    });

    onMount(() => {
        // Startup
        engine = new SkyMap3DEngine(container, {
            groundColor, cardinalColor, starOpacity, constellationColor, constellationOpacity
        });

        // Shutdown
        return () => engine.dispose();
    });
</script>

<div class="w-full h-full relative group">
    <div bind:this={container} class="w-full h-full bg-transparent rounded-3xl overflow-hidden cursor-move"></div>
    <div class="absolute top-4 left-4 px-3 py-1.5 bg-slate-900/80 backdrop-blur border border-slate-700 rounded-lg text-[10px] font-mono text-slate-300 uppercase pointer-events-none z-10 flex flex-col gap-1">
        <span class="text-yellow-400 font-bold">Sky 3D Engine</span>
        <span class="text-slate-400">Scroll: Zoom | Drag: Move</span>
    </div>
</div>