<!--
  ASTRA - Automated Smart Telescope Remote Assistant
  Copyright (C) 2026 Jesus Basallote
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
  
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script lang="ts">
    import { deviceStore } from '$lib/stores/devices.svelte';
    import { SatelliteDish, LoaderCircle, Crosshair, Telescope, Camera, ChevronDown, OctagonAlert } from 'lucide-svelte';
    import * as m from '$lib/paraglide/messages.js';
    import { deviceAPI } from '$lib/api/devices';

    let { 
        /** Callback function to center the view on the telescope's current target */
        onCenter = () => {},
        /** Whether the centering action is currently allowed */
        canCenter = false
    }: {
        onCenter?: () => void,
        canCenter?: boolean
    } = $props();

    /** Whether the active telescope is currently online */
    const isOnline = $derived(
        deviceStore.activeDetails?.is_online ?? 
        deviceStore.activeBase?.is_online ?? 
        false
    );

    /** List of active components for the current device */
    const activeComps = $derived(deviceStore.activeComponents);

    /** Whether a telescope movement abort operation is in progress */
    let isAborting = $state(false);
    
    /** Whether the controller dropdown menu is open */
    let isOpen = $state(false);

    /**
     * Attempts to abort all current telescope movement
     */
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
    
    /**
     * Closes the dropdown menu when clicking outside the component
     * @param {MouseEvent} e - The click event
     */
    function handleOutsideClick(e: MouseEvent) {
        if (isOpen && !(e.target as Element).closest('.telescope-controller-container')) {
            isOpen = false;
        }
    }
</script>

<svelte:window onclick={handleOutsideClick} />

<div class="relative pointer-events-auto telescope-controller-container z-50">
    <button 
        onclick={() => isOpen = !isOpen}
        class="flex items-center gap-2 bg-surface backdrop-blur-xl border border-border rounded-full py-1.5 px-3 shadow-[0_4px_15px_rgba(0,0,0,0.3)] hover:bg-panel/60 transition-colors cursor-pointer"
        aria-expanded={isOpen}
    >
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
            <SatelliteDish size={12} class="{isOpen ? 'text-accent' : 'text-copy-muted'} transition-colors" />
            <span class="text-[10px] font-bold text-copy-primary tracking-wider">{deviceStore.activeBase.name}</span>
            <ChevronDown size={12} class="{isOpen ? 'rotate-180 text-accent' : 'text-copy-muted'} transition-transform ml-1" />
        {:else}
            <SatelliteDish size={12} class="text-copy-muted transition-colors" />
            <span class="text-[10px] font-bold text-copy-primary tracking-wider">{m.dash_device_not_connected()}</span>
        {/if}
    </button>

    {#if true || (deviceStore.activeBase && isOnline)}
        <div class="absolute left-0 top-full pt-2 w-48 lg:w-56 transition-all origin-top-left {isOpen ? 'opacity-100 pointer-events-auto scale-100' : 'opacity-0 pointer-events-none scale-95'}">
            <div class="p-2 lg:p-3 bg-surface backdrop-blur-xl border border-border rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-1.5 lg:gap-2">
                
                <span class="text-[9px] font-bold text-accent px-2 pb-1.5 border-b border-border/50 uppercase tracking-widest">
                    {m.obs_telescope_controller_title()}
                </span>

                <button
                    onclick={() => {
                        onCenter();
                        isOpen = false;
                    }}
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



<!-- <div class="relative pointer-events-auto telescope-controller-container z-50">
    <button 
        onclick={() => isOpen = !isOpen}
        class="flex items-center gap-1.5 lg:gap-2 bg-surface backdrop-blur-xl border border-border rounded-full py-1 lg:py-2 px-2.5 lg:px-4 shadow-[0_4px_15px_rgba(0,0,0,0.3)] hover:bg-panel/60 transition-all cursor-pointer"
        aria-expanded={isOpen}
    >
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
            <LoaderCircle size={12} class="text-accent animate-spin lg:w-[14px] lg:h-[14px]" />
            <span class="text-[9px] lg:text-xs font-bold text-copy-primary tracking-wider">{m.dash_device_loading()}</span>
        {:else if deviceStore.activeBase && isOnline}
            <SatelliteDish size={12} class="{isOpen ? 'text-accent' : 'text-copy-muted'} transition-colors lg:w-[14px] lg:h-[14px]" />
            <span class="text-[9px] lg:text-xs font-bold text-copy-primary tracking-wider">{deviceStore.activeBase.name}</span>
            <ChevronDown size={12} class="{isOpen ? 'rotate-180 text-accent' : 'text-copy-muted'} transition-transform ml-0.5 lg:ml-1 lg:w-[14px] lg:h-[14px]" />
        {:else}
            <SatelliteDish size={12} class="text-copy-muted transition-colors lg:w-[14px] lg:h-[14px]" />
            <span class="text-[9px] lg:text-xs font-bold text-copy-primary tracking-wider">{m.dash_device_not_connected()}</span>
        {/if}
    </button>

    {#if true || (deviceStore.activeBase && isOnline)}
        <div class="absolute left-0 top-full pt-1.5 lg:pt-2 w-44 lg:w-56 transition-all origin-top-left {isOpen ? 'opacity-100 pointer-events-auto scale-100' : 'opacity-0 pointer-events-none scale-95'}">
            <div class="p-1.5 lg:p-3 bg-surface backdrop-blur-xl border border-border rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-1 lg:gap-2">
                
                <span class="text-[8px] lg:text-[9px] font-bold text-accent px-1.5 lg:px-2 pb-1 lg:pb-1.5 border-b border-border/50 uppercase tracking-widest">
                    {m.obs_telescope_controller_title()}
                </span>

                <button
                    onclick={() => {
                        onCenter();
                        isOpen = false;
                    }}
                    disabled={!canCenter}
                    class="flex items-center gap-2 lg:gap-2.5 px-2 lg:px-2.5 py-1.5 lg:py-2.5 rounded-md lg:rounded-lg text-[10px] lg:text-sm transition-colors {canCenter ? 'text-copy-primary hover:bg-panel/40 cursor-pointer' : 'text-copy-muted opacity-50 cursor-not-allowed'}"
                >
                    <Crosshair size={14} class="{canCenter ? 'text-accent' : ''} lg:w-[16px] lg:h-[16px]" />
                    {m.obs_telescope_controller_center()}
                </button>

                {#if activeComps?.telescope}
                    <button
                        onclick={handleAbort}
                        disabled={isAborting}
                        class="flex items-center gap-2 lg:gap-2.5 px-2 lg:px-2.5 py-1.5 lg:py-2.5 rounded-md lg:rounded-lg text-[10px] lg:text-sm transition-colors text-danger hover:bg-danger/10 hover:text-danger-hover cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group/abort"
                    >
                        {#if isAborting}
                            <LoaderCircle size={14} class="animate-spin lg:w-[16px] lg:h-[16px]" />
                            {m.obs_telescope_controller_aborting()}
                        {:else}
                            <OctagonAlert size={14} class="group-hover/abort:fill-danger/20 transition-colors lg:w-[16px] lg:h-[16px]" />
                            {m.obs_telescope_controller_abort()}
                        {/if}
                    </button>
                {/if}

                {#if activeComps.telescope || activeComps.camera}
                    <div class="flex flex-col gap-1 lg:gap-2 px-2 lg:px-3 py-1.5 lg:py-2.5 bg-panel/30 rounded-lg lg:rounded-xl border border-border/50 mt-0.5 lg:mt-1">
                        {#if activeComps.telescope}
                            <div class="flex items-center gap-1.5 lg:gap-2 text-[9px] lg:text-xs text-copy-muted" title={m.obs_telescope_controller_active_telescope()}>
                                <Telescope size={12} class="text-copy-secondary shrink-0 lg:w-[14px] lg:h-[14px]" />
                                <span class="truncate font-mono">{activeComps.telescope}</span>
                            </div>
                        {/if}
                        {#if activeComps.camera}
                            <div class="flex items-center gap-1.5 lg:gap-2 text-[9px] lg:text-xs text-copy-muted" title={m.obs_telescope_controller_active_camera()}>
                                <Camera size={12} class="text-copy-secondary shrink-0 lg:w-[14px] lg:h-[14px]" />
                                <span class="truncate font-mono">{activeComps.camera}</span>
                            </div>
                        {/if}
                    </div>
                {/if}

            </div>
        </div>
    {/if}
</div> -->