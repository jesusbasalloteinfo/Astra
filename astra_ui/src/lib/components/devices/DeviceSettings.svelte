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
    import { deviceAPI } from '$lib/api/devices';
    import { Cpu, Plus, X, LoaderCircle, KeyRound } from 'lucide-svelte';
    import { slide } from 'svelte/transition';
    import * as m from '$lib/paraglide/messages.js';
    import DeviceCard from './DeviceCard.svelte';

    /** Whether the "Add Device" (pairing) section is visible */
    let isAdding = $state(false);
    /** Input value for the device pairing token/PIN */
    let pairingToken = $state('');
    /** Whether a pairing request is currently in progress */
    let isPairing = $state(false);
    /** Error message to display if pairing fails */
    let pairingError = $state<string | null>(null);

    /** Whether the current pairing token input is valid */
    const isValid = $derived(pairingToken.trim().length > 0);

    /**
     * Attempts to pair a new device using the provided token
     */
    async function handlePair() {
        if (!isValid) return;
        
        isPairing = true;
        pairingError = null;

        try {
            await deviceAPI.pairDevice({ pin: pairingToken.trim() });
            
            await deviceStore.fetchAll();
            
            isAdding = false;
            pairingToken = '';
        } catch (e: any) {
            console.error("Pairing Error", e);
            pairingError = m.dash_device_pair_error(); 
        } finally {
            isPairing = false;
        }
    }
</script>

<div class="space-y-4">
    <div class="flex items-center justify-between px-1">
        <h3 class="text-[10px] font-bold text-copy-muted uppercase tracking-[0.2em] flex items-center gap-2">
            <Cpu size={12} class="text-accent" />
            {m.dash_device_list_title()}
        </h3>
    </div>
    
    <div class="flex flex-col gap-2.5">
        {#if deviceStore.isLoading && deviceStore.all.length === 0}
            {#each Array(2) as _}
                <div class="h-20 w-full bg-panel/50 animate-pulse rounded-xl border border-border"></div>
            {/each}
        {:else}
            {#each deviceStore.all as device (device.device_id)}
                <DeviceCard 
                    id={device.device_id}
                    name={device.name}
                    owner={device.owner}
                    isOnline={device.is_online} />
            {:else}
                <div class="py-10 text-center border-2 border-dashed border-border rounded-2xl bg-panel/20">
                    <p class="text-xs text-copy-muted italic">{m.dash_device_list_empty()}</p>
                </div>
            {/each}
        {/if}
    </div>

    <div class="pt-2">
        {#if !isAdding}
            <button 
                onclick={() => isAdding = true}
                class="cursor-pointer w-full flex items-center justify-center gap-2 p-3 rounded-xl border border-dashed border-border 
                       hover:bg-accent/5 hover:border-accent/50 hover:text-accent transition-all text-[11px] font-bold uppercase tracking-widest text-copy-muted">
                <Plus size={14} />
                {m.dash_device_action_pair()}
            </button>
        {:else}
            <div in:slide={{ duration: 200 }} class="p-5 rounded-2xl bg-panel border border-accent/20 space-y-4 shadow-2xl">
                <div class="flex items-center justify-between">
                    <span class="text-[10px] font-black uppercase tracking-widest text-accent">{m.dash_device_new_pairing()}</span>
                    <button onclick={() => { isAdding = false; pairingError = null; }} class="cursor-pointer text-copy-muted hover:text-copy-primary transition-colors">
                        <X size={16} />
                    </button>
                </div>

                <div class="space-y-4">
                    <div class="space-y-1">
                        <span class="text-[9px] font-bold text-copy-muted ml-1 uppercase">{m.dash_device_token_label()}</span>
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-copy-muted">
                                <KeyRound size={16} />
                            </div>
                            <input 
                                bind:value={pairingToken} 
                                placeholder={m.dash_device_token_placeholder()}
                                class="w-full bg-secondary/50 border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm font-mono text-copy-primary focus:border-accent outline-none transition-colors"
                            />
                        </div>
                    </div>

                    {#if pairingError}
                        <div in:slide class="text-xs text-danger font-medium px-1">
                            {pairingError}
                        </div>
                    {/if}

                    <button 
                        onclick={handlePair}
                        disabled={!isValid || isPairing}
                        class="w-full flex items-center justify-center py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg shadow-accent/20 disabled:opacity-30 transition-all active:scale-[0.98]">
                        {#if isPairing}
                            <LoaderCircle size={16} class="animate-spin mr-2" />
                            {m.dash_device_pairing()}
                        {:else}
                            {m.dash_device_pair()}
                        {/if}
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div>