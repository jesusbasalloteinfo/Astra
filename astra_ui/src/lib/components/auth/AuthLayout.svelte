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
    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import * as m from '$lib/paraglide/messages.js';

    let { 
        /** Content to be rendered inside the layout card */
        children, 
        /** Primary title for the authentication screen */
        title, 
        /** Descriptive subtitle under the title */
        subtitle, 
        /** URL for the back navigation link */
        backLink = "/", 
        /** Text to display for the back navigation link at the bottom */
        backText 
    } = $props();
</script>

<div class="min-h-svh bg-astralanding-dark text-slate-200 flex items-center justify-center relative overflow-y-auto py-8 lg:py-12 px-6">
    
    <Stars />

    <div class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[150vw] max-w-200 h-100 bg-blue-600/10 rounded-full blur-[100px] md:blur-[200px] pointer-events-none z-0"></div>

    <div class="relative z-10 w-full max-w-md landscape:max-w-4xl lg:max-w-4xl flex flex-col landscape:flex-row lg:flex-row items-center justify-center gap-8 landscape:gap-16 lg:gap-24 m-auto">

        <a href={backLink} class="flex flex-col items-center text-center landscape:items-start landscape:text-left lg:items-start lg:text-left gap-3 opacity-80 hover:opacity-100 transition-opacity shrink-0">
            <AppLogo class="w-12 h-12 landscape:w-16 landscape:h-16 lg:w-20 lg:h-20" />
            <div>
                <h1 class="text-2xl landscape:text-3xl lg:text-4xl font-bold text-white leading-none">{m.name().toUpperCase()}</h1>
                <p class="text-[10px] landscape:text-xs lg:text-sm tracking-widest text-blue-300 font-medium mt-2">{m.name_sign().toUpperCase()}</p>
            </div>
        </a>

        <div class="w-full flex flex-col max-w-md">
            <div class="bg-white/5 border border-white/10 rounded-2xl p-6 md:p-8 backdrop-blur-md shadow-2xl w-full">
                
                <h2 class="text-2xl font-bold text-white mb-2">{title}</h2>
                <p class="text-slate-400 text-sm mb-6 lg:mb-8">{subtitle}</p>

                {@render children()}

            </div>
            
            {#if backText}
                <p class="text-center landscape:text-right lg:text-right text-slate-500 text-sm mt-6 landscape:mt-4 lg:mt-4">
                    <a href={backLink} class="hover:text-blue-400 transition-colors">{backText}</a>
                </p>
            {/if}
        </div>
    </div>
</div>