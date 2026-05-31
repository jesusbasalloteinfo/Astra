<!-- src/lib/components/observation/skyFinderComponents/SkyFinderResult.svelte -->
<script lang="ts">
    import { Sun, ChevronRight } from 'lucide-svelte';
    import Icon from '@iconify/svelte';
    import NebulaIcon from './NebulaIcon.svelte';
    import { translateObjectType } from '$lib/utils/i18n';
    import { m } from '$lib/paraglide/messages';

    /**
     * Component props
     * @type {{ result: any, isSelected?: boolean, onclick: () => void, onHover: () => void }}
     * @property {any} result - The search result object containing object details
     * @property {boolean} [isSelected=false] - Whether this result is currently selected/highlighted
     * @property {() => void} onclick - Function called when the result is clicked
     * @property {() => void} onHover - Function called when the result is hovered
     */
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

    /** Mapping of object categories to Iconify icon names */
    const iconMap = {
        'planetary': 'tabler:planet',
        'moon': 'tabler:moon',
        'galaxy': 'hugeicons:galaxy',
        'nebula': 'lucide:sparkles',
        'constellation': 'hugeicons:constellation',
        'star': 'tabler:star'
    };

    /**
     * Returns the appropriate icon name for a given object type
     * @param {string} type - The category/type of the astronomical object
     * @returns {string} The Iconify icon identifier
     */
    function getIcon(type: string) {
        return iconMap[type as keyof typeof iconMap] || 'lucide:sparkles';
    }
</script>

<button 
    {onclick}
    onmouseover={onHover}
    onfocus={onHover}
    class="w-full flex items-center justify-between p-3 rounded-xl transition-all cursor-pointer border border-transparent
        {isSelected ? 'bg-accent/20 border-accent/50 shadow-inner' : 'hover:bg-panel/50'}"
>
    <div class="flex items-center gap-4">
        <div class="p-2 shrink-0 flex items-center justify-center rounded-lg {isSelected ? 'bg-accent text-white shadow-[0_0_10px_var(--color-accent-glow)]' : 'bg-surface text-copy-muted'}">
            {#if result.id === 'sun'}
                <Sun size={16} />
            {:else if result.category === 'nebula'}
                <NebulaIcon size={16} class="scale-120" />
            {:else}
                <Icon icon={getIcon(result.category)} width={16} height={16} />
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