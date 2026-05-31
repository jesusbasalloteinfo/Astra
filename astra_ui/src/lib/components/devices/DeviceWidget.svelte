<script lang="ts">
    import { Cpu, PowerOff, LoaderCircle, Settings, CircleAlert } from 'lucide-svelte';
    import { fade } from 'svelte/transition';
    import { deviceStore } from '$lib/stores/devices.svelte';
	import { onDestroy, onMount } from 'svelte';
    import * as m from '$lib/paraglide/messages.js';

    let {
        /** Callback function triggered for configuration actions */
        onconfig = () => {}
    } = $props();

    /** Base information of the active device */
    const base = $derived(deviceStore.activeBase);
    /** Detailed status and components of the active device */
    const details = $derived(deviceStore.activeDetails);
    /** Whether device details are currently being fetched */
    const isLoading = $derived(deviceStore.isFetchingDetails);

    /** Whether the active device is currently online */
    const isOnline = $derived(details?.is_online ?? false);
    /** Timer interval for periodic status refreshes */
    let interval: ReturnType<typeof setInterval>;


    onMount(() => {
        if (deviceStore.all.length === 0) {
            deviceStore.fetchAll();
        }

        interval = setInterval(() => {
            deviceStore.refreshActiveDetails();
        }, 10000); 
    });
    
    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

</script>

<div class="bg-panel border border-border rounded-2xl p-4 md:p-5 shadow-sm hover:border-accent/20 transition-all duration-300 group flex flex-col h-full">
    <div class="flex items-center justify-between mb-3 md:mb-4">
        <div class="flex items-center gap-2">
            <div class="p-1 bg-accent/10 rounded-lg text-accent">
                <Cpu size={12} class="md:hidden" />
                <Cpu size={14} class="hidden md:block" />
            </div>
            <span class="text-[9px] md:text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em]">{m.dash_device_list_title()}</span>
        </div>
        <a
            href="/dashboard/devices"
            class="text-copy-muted hover:text-copy-primary transition-colors p-1.5 rounded-lg hover:bg-surface"
            title="{m.dash_device_list_title()}"
        >
            <Settings size={14} />
        </a>
    </div>

    <div class="flex-1 flex flex-col justify-center">
        {#if !base}
            <div in:fade class="text-center py-2">
                <p class="text-[11px] md:text-xs text-copy-muted italic mb-3">{m.dash_device_list_empty()}</p>
                <a href="/dashboard/devices" class="inline-block px-4 py-2 bg-accent/10 hover:bg-accent/20 text-accent text-[9px] md:text-[10px] font-bold uppercase tracking-widest rounded-lg transition-all">
                    {m.dash_device_add()}
                </a>
            </div>

        {:else if isLoading && !details}
            <div in:fade class="flex flex-col items-center justify-center py-4 text-copy-muted">
                <LoaderCircle size={24} class="animate-spin text-accent mb-2" />
                <span class="text-[9px] md:text-[10px] font-bold uppercase tracking-widest animate-pulse">{m.dash_device_status_fetching()}</span>
            </div>

        {:else}
            <div in:fade class="flex items-center justify-between gap-2">
                <div class="min-w-0 pr-2 md:pr-4">
                    <h3 class="text-base md:text-lg font-bold text-copy-primary truncate mb-0.5 md:mb-1">
                        {base.name}
                    </h3>
                    <p class="text-[10px] md:text-[11px] font-mono text-copy-muted opacity-80 truncate">
                        {base.owner} </p>
                </div>

                <div class="flex flex-col items-end gap-2 shrink-0">
                    {#if isOnline}
                        <div class="flex items-center gap-1 px-2 py-0.5 md:px-2.5 md:py-1 bg-success/10 border border-success/20 rounded-full">
                            <div class="w-1 md:w-1.5 h-1 md:h-1.5 bg-success rounded-full animate-pulse"></div>
                            <span class="text-[9px] md:text-[10px] font-bold text-success uppercase tracking-wider">{m.dash_device_online()}</span>
                        </div>
                    {:else}
                        <div class="flex items-center gap-1 px-2 py-0.5 md:px-2.5 md:py-1 bg-danger/10 border border-danger/20 rounded-full">
                            <PowerOff size={9} class="text-danger md:w-2.5" />
                            <span class="text-[9px] md:text-[10px] font-bold text-danger uppercase tracking-wider">{m.dash_device_offline()}</span>
                        </div>
                    {/if}
                </div>
            </div>

            {#if isOnline && details?.components}
                <!-- <div class="grid grid-cols-2 gap-4 mt-4 md:mt-6 pt-3 md:pt-4 border-t border-border/40">
                    <div>
                        <p class="text-[8px] md:text-[9px] uppercase font-black text-copy-muted leading-none mb-1">Placeholder</p>
                        <p class="text-xs md:text-sm font-mono text-copy-primary leading-none">
                            placeholder
                        </p>
                    </div>
                </div> -->
            {:else if !isOnline}
                <div class="mt-4 md:mt-6 pt-3 md:pt-4 border-t border-border/40 flex items-center gap-2 text-warning">
                    <CircleAlert size={12} class="shrink-0 md:w-14" />
                    <p class="text-[9px] md:text-[10px] leading-tight">{m.dash_device_disconnected()}</p>
                </div>
            {/if}
        {/if}
    </div>
</div>