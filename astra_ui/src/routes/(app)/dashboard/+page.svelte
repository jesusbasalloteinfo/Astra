<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { getLocale, setLocale } from '$lib/paraglide/runtime.js';
    import { AVAILABLE_LANGUAGES, type LanguageCode } from '$lib/config/languages';

    const SUPPORTED_LOCALES = AVAILABLE_LANGUAGES.map(l => l.code);



    let currentLocale = $state(getLocale());

</script>

<div class="flex flex-col items-center justify-center min-h-[50vh] p-8 space-y-6 font-sans">
    
    <div class="text-center space-y-2">
        <h1 class="text-4xl font-bold text-slate-800 tracking-tight">
            {m.name()}
        </h1>
        <p class="text-slate-500">
            Test language: <span class="font-mono font-bold text-indigo-600 uppercase">{currentLocale}</span>
        </p>
    </div>

    <div class="flex gap-4 p-2 bg-slate-100 rounded-xl shadow-inner">
    </div>

</div>
