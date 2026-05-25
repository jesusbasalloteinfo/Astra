<!-- src/lib/components/observation/targetDetailsPanelComponents/InfoBlockCard.svelte -->
<script lang="ts">
    import type { Snippet } from 'svelte';
    import { ChevronDown } from 'lucide-svelte';

    let {
        title,
        text = null,
        icon: IconComponent,
        variant = 'default',
        headerAction = undefined
    } = $props<{
        title: string;
        text?: string | null;
        icon: any; // Lucide Icon
        variant?: 'default' | 'funFact' | 'visualTip';
        headerAction?: Snippet; // Svelte 5 Snippet
    }>();

    let isExpanded = $state(false);

    const theme = $derived.by(() => {
        if (variant === 'funFact') return { icon: 'text-yellow-500/70', bg: 'bg-yellow-500/5', border: 'border-yellow-500/10', largeIcon: 'text-yellow-500 opacity-[0.07]' };
        if (variant === 'visualTip') return { icon: 'text-blue-400/70', bg: 'bg-blue-400/5', border: 'border-blue-400/10', largeIcon: 'text-blue-400 opacity-[0.07]' };
        return { icon: 'text-copy-muted', bg: 'bg-panel/30 hover:bg-panel/50', border: 'border-border', largeIcon: 'text-copy-muted opacity-5' };
    });
</script>

{#if text || headerAction}
    <div class="space-y-2">
        <div class="flex items-center justify-between mb-1.5 px-1">
            <div class="flex items-center gap-1.5 {theme.icon}">
                <IconComponent size={14} />
                <h3 class="text-[10px] font-bold uppercase tracking-widest">{title}</h3>
            </div>
            
            {#if headerAction}
                {@render headerAction()}
            {/if}
        </div>

        {#if text}
            <button 
                onclick={() => isExpanded = !isExpanded}
                class="w-full text-left relative overflow-hidden {theme.bg} p-4 rounded-xl border {theme.border} shadow-inner group transition-all duration-300 cursor-pointer"
            >
                <div class="absolute -right-4 -bottom-4 {theme.largeIcon} group-hover:scale-110 transition-transform duration-700">
                    <IconComponent size={64} strokeWidth={1} />
                </div>
                
                <p class="relative text-sm text-copy-primary/90 text-justify leading-relaxed whitespace-pre-wrap {isExpanded ? '' : 'line-clamp-3'}">
                    {text}
                </p>

                {#if text.length > 150}
                    <div class="relative mt-2 flex justify-center text-copy-muted/50 group-hover:text-copy-muted transition-colors cursor-pointer">
                        <ChevronDown size={14} class="transition-transform duration-300 {isExpanded ? 'rotate-180' : ''}" />
                    </div>
                {/if}
            </button>
        {/if}
    </div>
{/if}