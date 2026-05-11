<!-- src/lib/components/observation/sideDockComponents/DockPopover.svelte -->
<script lang="ts">

    let { 
        icon: IconComponent, 
        title = '', 
        buttonTitle = '',
        active = false,
        activeClass = 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]',
        children 
    } = $props();
</script>

<div class="relative group">
    <!-- Trigger Button -->
    <button 
        title={buttonTitle}
        class="cursor-pointer p-3 rounded-full transition-all shadow-inner 
               {active 
                ? activeClass 
                : 'hover:bg-panel/50 text-copy-muted hover:text-white'}"
    >
        {#if IconComponent}
            <IconComponent size={20} />
        {/if}
    </button>

    <!-- Popover Menu -->
    <div class="absolute left-full top-1/2 -translate-y-1/2 pl-4 opacity-0 pointer-events-none 
                group-hover:opacity-100 group-hover:pointer-events-auto transition-all z-50">
        <div class="p-3 bg-surface backdrop-blur-xl border border-border rounded-2xl w-52 shadow-xl flex flex-col gap-2">
            {#if title}
                <span class="text-[10px] font-bold text-accent px-2 pb-1.5 mb-1 border-b border-border/50 uppercase tracking-widest leading-tight">
                    {title}
                </span>
            {/if}
            
            <div class="flex flex-col gap-1">
                {@render children()}
            </div>
        </div>
    </div>
</div>