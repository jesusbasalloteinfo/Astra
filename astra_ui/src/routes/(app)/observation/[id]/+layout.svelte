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

<!-- src/routes/(app)/observation/[id]/+layout.svelte -->
<script lang="ts">
    import { page } from '$app/state';
    import { activeObs } from '$lib/stores/activeObservation.svelte';
    import { CircleAlert } from 'lucide-svelte';
    import { catalogStore } from '$lib/stores/skyCatalog.svelte';
    import { skyEngine } from '$lib/stores/skyEngine.svelte';
    import { timeEngine } from '$lib/stores/timeEngine.svelte';
    import { selectionStore } from '$lib/stores/activeSelection.svelte';
    import { locStore } from '$lib/stores/location.svelte';
    import { authStore } from '$lib/stores/auth.svelte';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import { fade } from 'svelte/transition';
	import * as m from '$lib/paraglide/messages';
    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';

    let { children } = $props();

    $effect(() => {
        if (authStore.isLoading) return;

        if (locStore.all.length === 0) {
            goto('/dashboard/sessions');
            return;
        }

        const id = page.params.id;
        if (id) {
            catalogStore.isRunning = true;
            skyEngine.isRunning = true;
            activeObs.setSession(id);
        }
        return () => {
            console.log("Shutting down engines...");
            catalogStore.isRunning = false;
            skyEngine.isRunning = false;
            timeEngine.setLive(true);
            skyEngine.reset();
            // Do not wipe catalogStore completely so re-entering the observation is instant!
            selectionStore.clear();
            activeObs.clear();
        };
    });

    /**
     * Returns to the previous page or falls back to the dashboard
     */
    function handleBack() {
        if (browser && document.referrer && document.referrer.includes(window.location.host)) {
            window.history.back();
        } else {
            goto('/dashboard');
        }
    }

    let isInitializing = $derived(activeObs.isLoading || (!catalogStore.isLoaded && !activeObs.error));

    let loadingStatusText = $derived.by(() => {
        if (activeObs.isLoading) {
            return m.obs_load_step_session();
        }
        if (!catalogStore.isLoaded) {
            return m.obs_load_step_ephemeris();
        }
        return m.obs_load_step_dome();
    });
</script>

{#if isInitializing}
    <div class="fixed inset-0 z-50 bg-astralanding-dark flex items-center justify-center overflow-hidden select-none" transition:fade={{ duration: 400 }}>
        <Stars />

        <!-- Central glow -->
        <div class="absolute w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div class="relative z-10 flex flex-col items-center">
            
            <!-- Logo with orbital loading ring -->
            <div class="relative mb-10">
                <!-- Spinning ring -->
                <svg class="absolute -inset-6 w-[calc(100%+3rem)] h-[calc(100%+3rem)] animate-spin-slow">
                    <circle 
                        cx="50%" cy="50%" r="48%" 
                        stroke="currentColor" 
                        stroke-width="1" 
                        fill="none" 
                        class="text-blue-500/20"
                    />
                    <circle 
                        cx="50%" cy="50%" r="48%" 
                        stroke="currentColor" 
                        stroke-width="2" 
                        fill="none" 
                        stroke-dasharray="60 180" 
                        class="text-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.5)]"
                    />
                </svg>

                <div class="relative bg-astralanding-dark rounded-full p-2">
                    <AppLogo class="w-20 h-20 drop-shadow-[0_0_20px_rgba(37,99,235,0.5)]" />
                </div>
            </div>

            <div class="text-center px-4">
                <h1 class="text-2xl font-bold text-white tracking-[0.2em] mb-1 truncate max-w-sm">
                    {activeObs.current?.name?.toUpperCase() || m.name().toUpperCase()}
                </h1>
                
                <div class="h-4 overflow-hidden">
                    <p class="text-[10px] font-mono text-blue-400/70 tracking-widest uppercase">
                        {loadingStatusText}
                    </p>
                </div>
            </div>
        </div>
    </div>

{:else if activeObs.error}
    <!-- Error detected -->
    <div class="fixed inset-0 bg-secondary z-50 flex items-center justify-center p-6">
        <div class="w-full max-w-lg p-12 bg-panel border border-border rounded-3xl text-center">
            <div class="w-16 h-16 bg-danger/10 text-danger rounded-full flex items-center justify-center mx-auto mb-4">
                <CircleAlert size={32} />
            </div>
            <h2 class="text-xl font-bold text-copy-primary uppercase font-mono">{m.obs_error_load_title() }</h2>
            <p class="text-sm text-copy-muted max-w-sm mx-auto mt-2 mb-8">
                {activeObs.error || 'The requested observation is not available.'}
            </p>
            <button 
                onclick={handleBack} 
                class="inline-flex items-center gap-2 px-6 py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-bold transition-all shadow-lg shadow-accent/20 cursor-pointer outline-none"
            >
                {m.obs_error_load_btn()}
            </button>
        </div>
    </div>

{:else if activeObs.current && catalogStore.isLoaded}
    {@render children()}
{/if}

<style>
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .animate-spin-slow {
        animation: spin-slow 1.5s linear infinite;
    }
</style>