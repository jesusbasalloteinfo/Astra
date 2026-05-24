<!-- src/lib/components/observation/SideDock.svelte -->
<script lang="ts">
	import { m } from '$lib/paraglide/messages';
    import { ArrowLeft, Search, Sparkles } from 'lucide-svelte';
    import ThemeDockButton from './sideDockComponents/ThemeDockButton.svelte';
    import SettingsDockButton from './sideDockComponents/SettingsDockButton.svelte';

    let {
        showConstellations = $bindable(),
        showConstellationLabels = $bindable(),
        useLatinConstellations = $bindable(),
        showGround = $bindable(),
        solidGround = $bindable(),
        showAtmosphere = $bindable(),
        atmosphereLocked = false,
        searchOpen = $bindable(),
        chatOpen = $bindable()
    } = $props();

</script>

<div class="bg-surface backdrop-blur-xl border border-border rounded-3xl p-2 max-lg:landscape:p-1.5 flex flex-col items-center gap-3 max-lg:landscape:gap-1 shadow-[0_8px_32px_rgba(0,0,0,0.3)] pointer-events-auto">

    <!-- Return to dashboard -->
    <a href="/dashboard/sessions" title="Return" class="flex items-center justify-center p-3 max-lg:landscape:p-2 rounded-full hover:bg-panel/50 text-copy-muted hover:text-white transition-all">
        <ArrowLeft size={20} class="max-lg:landscape:w-4 max-lg:landscape:h-4" />
    </a>

    <div class="w-full h-px bg-border/50 my-1 max-lg:landscape:my-0.5"></div>

    <button title="Search" onclick={() => searchOpen = true} class="flex items-center justify-center p-3 max-lg:landscape:p-2 rounded-full hover:bg-panel/50 text-copy-muted hover:text-accent transition-all cursor-pointer">
        <Search size={20} class="max-lg:landscape:w-4 max-lg:landscape:h-4" />
    </button>

    <SettingsDockButton 
        bind:showConstellations 
        bind:showConstellationLabels 
        bind:useLatinConstellations 
        bind:showGround 
        bind:solidGround 
        bind:showAtmosphere 
        {atmosphereLocked} 
    />

    <ThemeDockButton />

    <div class="w-full h-px bg-border/50 my-1 landscape:my-0.5"></div>

    <button title={m.obs_assistant_title()} onclick={() => chatOpen = !chatOpen} class="flex items-center justify-center cursor-pointer p-3 max-lg:landscape:p-2 rounded-full transition-all shadow-inner {chatOpen ? 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]' : 'hover:bg-panel/50 text-copy-muted hover:text-purple-400'}">
        <Sparkles size={20} class="max-lg:landscape:w-4 max-lg:landscape:h-4" />
    </button>
</div>