<script lang="ts">
	import { m } from '$lib/paraglide/messages';
    import { formatNumber } from '$lib/utils/i18n';
    import { Eclipse, Orbit } from 'lucide-svelte';

    let {
        id, 
        illuminationPct = 0,
        elongationDeg = 0
    } = $props<{
        id: string;
        illuminationPct: number;
        elongationDeg: number;
    }>();

    // 1. Determine the limit for an object
    let safeId = $derived(id.toLowerCase());
    let isInferior = $derived(['mercury', 'venus'].includes(safeId));
    
    let maxElongation = $derived.by(() => {
        if (safeId === 'mercury') return 28;
        if (safeId === 'venus') return 48;
        return 180; // For the rest
    });

    let elongationProgress = $derived(Math.min(100, (elongationDeg / maxElongation) * 100));
    
    let elongationLabel = $derived.by(() => {
        if (elongationDeg < 10) return m.obs_targetinfo_planetary_conjunction(); 

        if (isInferior) {
            // Mercury/Venus
            if (elongationDeg >= maxElongation - 4) return m.obs_targetinfo_planetary_max_elong();
        } else {
            if (elongationDeg > 170) return m.obs_targetinfo_planetary_opposition(); 
        }
        
        return '';
    });
</script>

<div class="bg-panel/30 rounded-xl p-4 border border-border shadow-inner flex flex-col gap-3 group transition-colors hover:bg-panel/40">
    <h4 class="text-[10px] uppercase tracking-wider text-copy-muted">{m.obs_targetinfo_planetary_title()}</h4>

    <div class="grid grid-cols-2 gap-4 mt-1">
        
        <!-- ILLUMINATION -->
        <div class="flex items-start gap-2">
            <div class="mt-0.5 text-accent opacity-80 group-hover:scale-110 transition-transform">
                <Eclipse size={14} />
            </div>
            <div class="flex flex-col">
                <span class="text-[8px] font-bold uppercase text-copy-muted mb-0.5">{m.obs_targetinfo_planetary_ilum()}</span>
                <span class="text-sm font-bold text-white tabular-nums">{formatNumber(illuminationPct, 1)}%</span>
            </div>
        </div>

        <!-- ELONGATION -->
        <div class="flex items-start gap-2">
            <div class="mt-0.5 text-accent opacity-80 group-hover:rotate-45 transition-transform duration-700">
                <Orbit size={14} />
            </div>
            <div class="flex flex-col w-full">
                <div class="flex justify-between items-baseline mb-0.5">
                    <span class="text-[8px] font-bold uppercase text-copy-muted">{m.obs_targetinfo_planetary_elong()}</span>
                    {#if elongationLabel}
                        <span class="text-[7px] font-bold text-accent uppercase tracking-widest">{elongationLabel}</span>
                    {/if}
                </div>
                
                <span class="text-sm font-bold text-white tabular-nums">{formatNumber(elongationDeg, 1)}°</span>

                <div class="w-full h-1 bg-black/40 rounded-full mt-2 overflow-hidden shadow-inner relative" title="Max: {maxElongation}°">
                    <!-- Best moment indicator -->
                    <!-- <div class="absolute right-0 top-0 bottom-0 w-0.5 bg-white/20 z-10"></div> -->
                    
                    <div 
                        class="h-full rounded-full transition-all duration-1000 {elongationProgress > 90 ? 'bg-accent shadow-[0_0_8px_var(--color-accent-glow)]' : 'bg-copy-muted/50'}"
                        style="width: {elongationProgress}%"
                    ></div>
                </div>
            </div>
        </div>
        
    </div>
</div>