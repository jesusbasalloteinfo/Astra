<script lang="ts">
    import { deviceStore } from '$lib/stores/devices.svelte';
    import { SatelliteDish, LoaderCircle } from 'lucide-svelte';
    import * as m from '$lib/paraglide/messages.js';

    const isOnline = $derived(
        deviceStore.activeDetails?.is_online ?? 
        deviceStore.activeBase?.is_online ?? 
        false
    );
</script>

<button class="flex items-center gap-2 bg-surface backdrop-blur-xl border border-border rounded-full py-1.5 px-3 shadow-[0_4px_15px_rgba(0,0,0,0.3)] hover:bg-panel/40 transition-colors group pointer-events-auto">
    <div class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
    </div>
    
    {#if deviceStore.isLoading && deviceStore.all.length === 0 && isOnline}
        <LoaderCircle size={12} class="text-accent animate-spin" />
        <span class="text-[10px] font-bold text-copy-primary tracking-wider">{m.dash_device_loading()}</span>
    {:else if deviceStore.activeBase && isOnline}
        <SatelliteDish size={12} class="text-copy-muted group-hover:text-copy-primary transition-colors" />
        <span class="text-[10px] font-bold text-copy-primary tracking-wider">{deviceStore.activeBase.name}</span>
    {:else}
        <SatelliteDish size={12} class="text-copy-muted group-hover:text-copy-primary transition-colors" />
        <span class="text-[10px] font-bold text-copy-primary tracking-wider">{m.dash_device_not_connected()}</span>
    {/if}
</button>