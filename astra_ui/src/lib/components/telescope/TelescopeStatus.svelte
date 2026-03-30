<script lang="ts">
    import { Telescope, Wifi, WifiOff, Settings } from 'lucide-svelte';

    let {
        connected = false,
        name = 'No telescope configured',
        pointing = '',
        onconfig,
    }: {
        connected?: boolean;
        name?: string;
        pointing?: string;
        onconfig?: () => void;
    } = $props();
</script>

<div class="bg-panel border border-border rounded-xl p-5">
    <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
            <Telescope size={16} class="text-copy-muted" />
            <span class="text-xs font-semibold text-copy-muted uppercase tracking-wider">Telescope</span>
        </div>
        <button
            onclick={onconfig}
            class="text-copy-muted hover:text-copy-primary transition-colors p-1 rounded-lg hover:bg-surface">
            <Settings size={14} />
        </button>
    </div>

    <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0
                    {connected ? 'bg-green-500/10' : 'bg-surface'}">
            {#if connected}
                <Wifi size={16} class="text-green-400" />
            {:else}
                <WifiOff size={16} class="text-copy-muted" />
            {/if}
        </div>
        <div class="min-w-0">
            <p class="text-sm font-semibold text-copy-primary truncate">{name}</p>
            {#if connected && pointing}
                <p class="text-xs text-copy-muted truncate">Pointing: {pointing}</p>
            {:else if connected}
                <p class="text-xs text-green-400">Connected</p>
            {:else}
                <p class="text-xs text-copy-muted">Disconnected</p>
            {/if}
        </div>
    </div>
</div>