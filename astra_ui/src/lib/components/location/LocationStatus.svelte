<script lang="ts">
    import { MapPin, Thermometer, Droplets, Settings } from 'lucide-svelte';

    let {
        configured = false,
        name = 'No location set',
        temperature,
        humidity,
        onconfig,
    }: {
        configured?: boolean;
        name?: string;
        temperature?: number;
        humidity?: number;
        onconfig?: () => void;
    } = $props();
</script>

<div class="bg-panel border border-border rounded-xl p-5">
    <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
            <MapPin size={16} class="text-copy-muted" />
            <span class="text-xs font-semibold text-copy-muted uppercase tracking-wider">Location</span>
        </div>
        <button
            onclick={onconfig}
            class="text-copy-muted hover:text-copy-primary transition-colors p-1 rounded-lg hover:bg-surface">
            <Settings size={14} />
        </button>
    </div>

    <p class="text-sm font-semibold text-copy-primary mb-3 truncate">{name}</p>

    {#if configured && (temperature !== undefined || humidity !== undefined)}
        <div class="flex items-center gap-4">
            {#if temperature !== undefined}
                <div class="flex items-center gap-1.5 text-xs text-copy-secondary">
                    <Thermometer size={13} class="text-copy-muted" />
                    {temperature}°C
                </div>
            {/if}
            {#if humidity !== undefined}
                <div class="flex items-center gap-1.5 text-xs text-copy-secondary">
                    <Droplets size={13} class="text-copy-muted" />
                    {humidity}%
                </div>
            {/if}
        </div>
    {:else}
        <p class="text-xs text-copy-muted">No conditions data</p>
    {/if}
</div>