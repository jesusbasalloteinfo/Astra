<!-- src/lib/components/observation/targetDetailsPanelComponents/InfoBlockCard.svelte -->
<script lang="ts">
    import type { Snippet } from 'svelte';

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

    const theme = $derived.by(() => {
        if (variant === 'funFact') return { icon: 'text-yellow-500/70', bg: 'bg-yellow-500/5', border: 'border-yellow-500/10', largeIcon: 'text-yellow-500 opacity-[0.07]' };
        if (variant === 'visualTip') return { icon: 'text-blue-400/70', bg: 'bg-blue-400/5', border: 'border-blue-400/10', largeIcon: 'text-blue-400 opacity-[0.07]' };
        return { icon: 'text-copy-muted', bg: 'bg-panel/30 hover:bg-panel/50', border: 'border-border', largeIcon: 'text-copy-muted opacity-5' };
    });

    const shouldRender = $derived(text || headerAction);
</script>

{#if shouldRender}
    <div class="space-y-2">
        <div class="flex items-center justify-between mb-1.5">
            <div class="flex items-center gap-1.5 {theme.icon}">
                <IconComponent size={14} />
                <h3 class="text-[10px] font-bold uppercase tracking-widest">{title}</h3>
            </div>
            
            {#if headerAction}
                {@render headerAction()}
            {/if}
        </div>

        {#if text}
            <div class="relative overflow-hidden {theme.bg} p-4 rounded-xl border {theme.border} shadow-inner group transition-colors">
                <div class="absolute -right-4 -bottom-4 {theme.largeIcon} group-hover:scale-110 transition-transform duration-700">
                    <IconComponent size={64} strokeWidth={1} />
                </div>
                <p class="relative text-sm text-copy-primary/90 leading-relaxed whitespace-pre-wrap">
                    {text}
                </p>
            </div>
        {/if}
    </div>
{/if}