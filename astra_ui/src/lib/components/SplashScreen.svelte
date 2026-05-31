<script lang="ts">
    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';

    /** List of status messages displayed during initialization */
    const statusSteps = [
        "Initializing core...",
        "Connecting to Astra interface...",
        "Fetching encrypted sessions...",
        "Synchronizing observer state...",
        "Rendering interface..."
    ];
    
    /** Current step index of the status message sequence */
    let currentStep = $state(0);

    onMount(() => {
        const interval = setInterval(() => {
            currentStep = (currentStep + 1) % statusSteps.length;
        }, 300); // Fast message changing
        return () => clearInterval(interval);
    });
</script>

<div class="min-h-screen bg-astralanding-dark flex items-center justify-center relative overflow-hidden">
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

        <div class="text-center">
            <h1 class="text-2xl font-bold text-white tracking-[0.2em] mb-1">
                {m.name().toUpperCase()}
            </h1>
            
            <div class="h-4 overflow-hidden">
                <p class="text-[10px] font-mono text-blue-400/60 tracking-widest uppercase">
                    {statusSteps[currentStep]}
                </p>
            </div>
        </div>
    </div>
</div>

<style>
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .animate-spin-slow {
        animation: spin-slow 1.5s linear infinite;
    }
</style>