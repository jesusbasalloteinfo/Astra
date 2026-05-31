<script lang="ts">
    import { X } from 'lucide-svelte';
    import { fade, fly } from 'svelte/transition';
    import * as m from '$lib/paraglide/messages.js';
    import LanguageSelector from '$lib/components/LanguageSwitcher.svelte';
    import AppLogo from '../AppLogo.svelte';

    let { 
        /** Whether the menu is currently open (bindable) */
        isOpen = $bindable(), 
        /** Array of navigation link objects */
        navLinks, 
        /** Callback function triggered upon navigation */
        onNavigate = () => {} 
    } = $props();

    /**
     * Closes the mobile menu
     */
    function close() {
        isOpen = false;
    }

    /**
     * Handles navigation when a menu link is clicked
     * @param {string} href - The destination URL
     */
    function handleNavigate(href: string) {
        onNavigate?.(href);
        close();
    }
</script>

{#if isOpen}
    <button 
        class="fixed inset-0 bg-astralanding-darker/60 backdrop-blur-md z-60 lg:hidden cursor-default"
        transition:fade={{ duration: 200 }}
        title="Close"
        onclick={close}
        aria-label="Close menu"
    ></button>

    <div 
        class="fixed inset-y-0 right-0 w-full max-w-sm bg-astralanding-panel border-l border-white/10 z-70 lg:hidden shadow-2xl overflow-y-auto"
        transition:fly={{ x: '100%', duration: 300 }}
    >
        <div class="flex flex-col h-full p-6 md:p-8">
            <div class="flex items-center justify-between mb-8 md:mb-12">
                <div class="flex items-center">
                    <AppLogo class="w-8 h-8 md:w-10 md:h-10 mr-3" />
                    <span class="text-xl font-bold text-white tracking-tight">{m.name().toUpperCase()}</span>
                </div>
                <button 
                    class="p-2 text-slate-400 hover:text-white transition-colors"
                    onclick={close}
                >
                    <X size={24} />
                </button>
            </div>

            <div class="flex flex-col h-full">
                <nav class="flex flex-col gap-6 mb-8">
                    {#each navLinks as link}
                        <a 
                            href={link.href} 
                            onclick={() => handleNavigate(link.href)}
                            class="text-2xl md:text-xl font-semibold text-slate-300 hover:text-white transition-colors"
                        >
                            {link.name}
                        </a>
                    {/each}
                </nav>

                <div class="mt-auto pt-8 border-t border-white/10 space-y-4">
                    <LanguageSelector
                        classButton="w-full text-white bg-white/5 border-white/10 rounded-xl hover:bg-white/10 backdrop-blur-sm justify-between px-4 py-3"
                        classDropdown="bg-astralanding-dark/95 border-white/10 rounded-xl w-full"
                        classActive="bg-blue-500/10 text-blue-400 font-semibold"
                        classInactive="text-slate-300 hover:bg-white/10 hover:text-white"
                        placement="top" />

                    <a 
                        href="/dashboard" 
                        class="block w-full px-6 py-4 bg-linear-to-r from-blue-600 to-indigo-600 text-white rounded-xl text-center font-bold text-lg shadow-lg shadow-blue-500/20 active:scale-[0.98] transition-transform"
                    >
                        {m.landing_cta()}
                    </a>
                </div>
            </div>
        </div>
    </div>
{/if}