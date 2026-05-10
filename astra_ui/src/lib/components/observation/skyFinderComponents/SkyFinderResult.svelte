<!-- src/lib/components/observation/skyFinderComponents/SkyFinderResult.svelte -->
<script lang="ts">
    import { Globe, Star, ChevronRight } from 'lucide-svelte';
    import { translateObjectType } from '$lib/utils/i18n';
    import { m } from '$lib/paraglide/messages';

    let { 
        result, 
        isSelected = false, 
        onclick, 
        onHover 
    } = $props<{
        result: any;
        isSelected?: boolean;
        onclick: () => void;
        onHover: () => void;
    }>();
</script>

<button 
    {onclick}
    onmouseover={onHover}
    onfocus={onHover}
    class="w-full flex items-center justify-between p-3 rounded-xl transition-all cursor-pointer border border-transparent
        {isSelected ? 'bg-accent/20 border-accent/50 shadow-inner' : 'hover:bg-panel/50'}"
>
    <div class="flex items-center gap-4">
        <div class="p-2 rounded-lg {isSelected ? 'bg-accent text-white shadow-[0_0_10px_var(--color-accent-glow)]' : 'bg-surface text-copy-muted'}">
            {#if result.type === 'planetary' || result.type === "moon"}
                <Globe size={16} />
            {:else}
                <Star size={16} />
            {/if}
        </div>
        <div class="text-left">
            <h4 class="text-sm font-bold {isSelected ? 'text-accent' : 'text-copy-primary'}">{result.name}</h4>
            <p class="text-[10px] text-copy-muted uppercase tracking-widest">{translateObjectType(result.category)} · Mag: {result.mag ?? 'N/A'}</p>
        </div>
    </div>
    <div class="flex items-center gap-2 text-copy-muted {isSelected ? 'opacity-100' : 'opacity-0'} transition-opacity">
        <span class="text-[9px] font-bold uppercase tracking-widest">{m.obs_skyfinder_select()}</span>
        <ChevronRight size={16} />
    </div>
</button>