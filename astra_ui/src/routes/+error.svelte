<script lang="ts">
    import { page } from '$app/state';
    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import * as m from '$lib/paraglide/messages.js';
    import { browser } from '$app/environment';
    import { goto } from '$app/navigation';

    let lang = $derived(page.params.lang ?? '');
    let status = $derived(page.status);
    let message = $derived(page.error?.message);

    /**
     * Returns to the previous page or falls back to the dashboard/home
     */
    function handleBack() {
        if (browser && document.referrer && document.referrer.includes(window.location.host)) {
            window.history.back();
        } else {
            // Default fallback: Dashboard if possible (it will redirect to landing if not logged in)
            goto('/dashboard');
        }
    }
</script>

<svelte:head>
    <title>{status} - {m.name().toUpperCase()}</title>
</svelte:head>

<div class="min-h-svh bg-astralanding-dark text-slate-200 flex items-center justify-center relative overflow-y-auto py-8 lg:py-12 px-6">
    
    <Stars />

    <div class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[150vw] max-w-200 h-100 bg-blue-600/10 rounded-full blur-[100px] md:blur-[200px] pointer-events-none z-0"></div>

    <div class="relative z-10 w-full max-w-md landscape:max-w-4xl lg:max-w-4xl flex flex-col landscape:flex-row lg:flex-row items-center justify-center gap-8 landscape:gap-16 lg:gap-24 m-auto">

        <a href="/{lang}" class="flex flex-col items-center text-center landscape:items-start landscape:text-left lg:items-start lg:text-left gap-3 opacity-80 hover:opacity-100 transition-opacity shrink-0">
            <AppLogo class="w-12 h-12 landscape:w-16 landscape:h-16 lg:w-20 lg:h-20" />
            <div>
                <h1 class="text-2xl landscape:text-3xl lg:text-4xl font-bold text-white leading-none">{m.name().toUpperCase()}</h1>
                <p class="text-[10px] landscape:text-xs lg:text-sm tracking-widest text-blue-300 font-medium mt-2">{m.name_sign().toUpperCase()}</p>
            </div>
        </a>

        <div class="w-full flex flex-col max-w-md">
            <div class="bg-white/5 border border-white/10 rounded-2xl p-6 md:p-8 backdrop-blur-md shadow-2xl w-full text-center lg:text-left">
                
                <h2 class="text-6xl font-bold text-blue-500 mb-4">{status}</h2>
                <h3 class="text-2xl font-semibold text-white mb-2">
                    {status === 404 ? m.error_title_404() : m.error_title_unexpected()}
                </h3>
                <p class="text-slate-400 text-sm mb-6 lg:mb-8">
                    {#if (status === 404 && (!message || message === 'Not Found')) || (status === 500 && (!message || message === 'Internal Error'))}
                        {m.error_desc_default()}
                    {:else}
                        {message || m.error_desc_default()}
                    {/if}
                </p>

                <div class="flex justify-center gap-4 flex-wrap">
                    <button 
                        onclick={handleBack} 
                        class="inline-flex items-center px-6 py-3 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-400 font-medium transition-all cursor-pointer outline-none"
                    >
                        {m.obs_sidedock_return()}
                    </button>
                    
                    <a 
                        href="/{lang}" 
                        class="inline-flex items-center px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 font-medium transition-all"
                    >
                        {m.login_return_home()}
                    </a>
                </div>

            </div>
        </div>
    </div>
</div>
