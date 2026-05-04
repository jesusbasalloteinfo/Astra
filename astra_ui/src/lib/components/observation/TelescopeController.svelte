<script lang="ts">
    import { deviceStore } from '$lib/stores/devices.svelte';
    import { SatelliteDish, LoaderCircle, Crosshair, Telescope, Camera, ChevronDown, OctagonAlert } from 'lucide-svelte';
    import * as m from '$lib/paraglide/messages.js';
	import { deviceAPI } from '$lib/api/devices';

    let { 
        onCenter = () => {},
        canCenter = false
    }: {
        onCenter?: () => void,
        canCenter?: boolean
    } = $props();

    const isOnline = $derived(
        deviceStore.activeDetails?.is_online ?? 
        deviceStore.activeBase?.is_online ?? 
        false
    );

    const activeComps = $derived(deviceStore.activeComponents);

    let isAborting = $state(false);

    async function handleAbort() {
        const activeId = deviceStore.effectiveActiveId;
        const activeTelescope = deviceStore.activeComponents?.telescope;
        
        if (!activeId || !activeTelescope) return;

        isAborting = true;
        try {
            await deviceAPI.abortTelescope(activeId, activeTelescope);
        } catch (e) {
            console.error("Error aborting telescope movement:", e);
        } finally {
            isAborting = false;
        }
    }
</script>

<div class="relative group pointer-events-auto">
    <button class="flex items-center gap-2 bg-surface backdrop-blur-xl border border-border rounded-full py-1.5 px-3 shadow-[0_4px_15px_rgba(0,0,0,0.3)] hover:bg-panel/60 transition-colors cursor-default">
        <div class="relative flex h-2 w-2">
            {#if isOnline}
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
            {:else}
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-danger opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-danger"></span>
            {/if}
        </div>
        
        {#if deviceStore.isLoading && deviceStore.all.length === 0 && isOnline}
            <LoaderCircle size={12} class="text-accent animate-spin" />
            <span class="text-[10px] font-bold text-copy-primary tracking-wider">{m.dash_device_loading()}</span>
        {:else if deviceStore.activeBase && isOnline}
            <SatelliteDish size={12} class="text-copy-muted group-hover:text-copy-primary transition-colors" />
            <span class="text-[10px] font-bold text-copy-primary tracking-wider">{deviceStore.activeBase.name}</span>
            <ChevronDown size={12} class="text-copy-muted ml-1" />
        {:else}
            <SatelliteDish size={12} class="text-copy-muted group-hover:text-copy-primary transition-colors" />
            <span class="text-[10px] font-bold text-copy-primary tracking-wider">{m.dash_device_not_connected()}</span>
        {/if}
    </button>

    {#if deviceStore.activeBase && isOnline}
        <div class="absolute left-0 top-full pt-2 w-56 opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all origin-top-left z-50">
            <div class="p-3 bg-surface backdrop-blur-xl border border-border rounded-2xl shadow-xl flex flex-col gap-2">
                
                <span class="text-[9px] font-bold text-accent px-2 pb-1.5 border-b border-border/50 uppercase tracking-widest">
                    {m.obs_telescope_controller_title()}
                </span>

                <button
                    onclick={onCenter}
                    disabled={!canCenter}
                    class="flex items-center gap-2 px-2 py-2 rounded-lg text-xs transition-colors {canCenter ? 'text-copy-primary hover:bg-panel/40 cursor-pointer' : 'text-copy-muted opacity-50 cursor-not-allowed'}"
                >
                    <Crosshair size={14} class={canCenter ? 'text-accent' : ''} />
                    {m.obs_telescope_controller_center()}
                </button>

                {#if activeComps?.telescope}
                    <button
                        onclick={handleAbort}
                        disabled={isAborting}
                        class="flex items-center gap-2 px-2 py-2 rounded-lg text-xs transition-colors text-danger hover:bg-danger/10 hover:text-danger-hover cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group/abort"
                    >
                        {#if isAborting}
                            <LoaderCircle size={14} class="animate-spin" />
                            {m.obs_telescope_controller_aborting()}
                        {:else}
                            <OctagonAlert size={14} class="group-hover/abort:fill-danger/20 transition-colors" />
                            {m.obs_telescope_controller_abort()}
                        {/if}
                    </button>
                {/if}

                {#if activeComps.telescope || activeComps.camera}
                    <div class="flex flex-col gap-1.5 px-2.5 py-2 bg-panel/30 rounded-xl border border-border/50">
                        {#if activeComps.telescope}
                            <div class="flex items-center gap-2 text-[10px] text-copy-muted" title={m.obs_telescope_controller_active_telescope()}>
                                <Telescope size={12} class="text-copy-secondary shrink-0" />
                                <span class="truncate font-mono">{activeComps.telescope}</span>
                            </div>
                        {/if}
                        {#if activeComps.camera}
                            <div class="flex items-center gap-2 text-[10px] text-copy-muted" title={m.obs_telescope_controller_active_camera()}>
                                <Camera size={12} class="text-copy-secondary shrink-0" />
                                <span class="truncate font-mono">{activeComps.camera}</span>
                            </div>
                        {/if}
                    </div>
                {/if}

            </div>
        </div>
    {/if}
</div>