<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { getLocale, setLocale } from '$lib/paraglide/runtime.js';

    let currentLocale = $derived(getLocale());

    async function switchLocale(locale: 'en' | 'es') {
        // 1. Tell the server to set the cookie properly
        await fetch('/system/set-locale', {
            method: 'POST',
            body: JSON.stringify({ locale }),
            headers: { 'Content-Type': 'application/json' }
        });

        // 2. Update Paraglide on the client immediately (no flicker)
        setLocale(locale);
    }
</script>

<div class="flex flex-col items-center justify-center min-h-[50vh] p-8 space-y-6 font-sans">
    
    <div class="text-center space-y-2">
        <h1 class="text-4xl font-bold text-slate-800 tracking-tight">
            {m.example_message({ username: 'User' })}
        </h1>
        <p class="text-slate-500">
            Idioma actual: <span class="font-mono font-bold text-indigo-600 uppercase">{currentLocale}</span>
        </p>
    </div>

    <div class="flex gap-4 p-2 bg-slate-100 rounded-xl shadow-inner">
        <button 
            onclick={() => switchLocale('en')}
            class="px-6 py-2 rounded-lg font-medium transition-all
            {currentLocale === 'en' 
                ? 'bg-white text-indigo-600 shadow-md scale-105' 
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}"
        >
            🇺🇸 English
        </button>

        <button 
            onclick={() => switchLocale('es')}
            class="px-6 py-2 rounded-lg font-medium transition-all
            {currentLocale === 'es' 
                ? 'bg-white text-indigo-600 shadow-md scale-105' 
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}"
        >
            🇪🇸 Spanish
        </button>
    </div>

</div>
