<!-- src/lib/components/observation/SideDock.svelte -->
<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { toInlangBool } from '$lib/utils/i18n';
    import { ArrowLeft, Search, Settings2, GitBranch, MountainSnow, Sparkles, Tag, Languages, ChevronDown, ChevronUp } from 'lucide-svelte';
	import { slide } from 'svelte/transition';

    let {
        showConstellations = $bindable(),
        showConstellationLabels = $bindable(),
        useLatinConstellations = $bindable(),
        showGround = $bindable(),
        searchOpen = $bindable(),
        chatOpen = $bindable()
    } = $props();

    let showConstellationsMenu = $state(showConstellations);

    function toggleConstellations() {
        showConstellations = !showConstellations;
        showConstellationsMenu = showConstellations;
    }

</script>

<div class="bg-surface backdrop-blur-xl border border-border  rounded-3xl p-2 flex flex-col gap-3 shadow-[0_8px_32px_rgba(0,0,0,0.3)] pointer-events-auto">
    
    <!-- Return to dashboard -->
    <a href="/dashboard/sessions" title="Return" class="p-3 rounded-full hover:bg-panel/50 text-copy-muted hover:text-white transition-all">
        <ArrowLeft size={20} />
    </a>

    <div class="w-full h-px bg-border/50 my-1"></div>

    <button title="Search" onclick={() => searchOpen = true} class="p-3 rounded-full hover:bg-panel/50 text-copy-muted hover:text-accent transition-all cursor-pointer">
        <Search size={20} />
    </button>

    <!-- Visual settings menu -->
    <div class="relative group">
        <button title={m.obs_sidedock_settings()}
            class="p-3 rounded-full hover:bg-panel/50 text-copy-muted hover:text-white transition-all cursor-pointer">
            <Settings2 size={20} />
        </button>
        <div class="absolute left-full top-1/2 -translate-y-1/2 pl-4 opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all">
            <div class="p-3 bg-surface backdrop-blur-xl border border-border rounded-2xl w-48 shadow-xl flex flex-col gap-1">
                <span class="text-xs font-bold text-accent px-2 pb-2 mb-1 border-b border-border/50 uppercase tracking-widest">{m.obs_sidedock_settings()}</span>
                
                <div class="flex items-center justify-between w-full">
                    <button onclick={toggleConstellations} 
                        class="cursor-pointer flex items-center gap-2 px-2 py-1.5 rounded hover:bg-panel/40 text-xs flex-1 {showConstellations ? 'text-accent' : 'text-copy-muted'}">
                        <GitBranch size={14}/> {m.obs_sidedock_constellations_title()}
                    </button>
                    
                    {#if showConstellations}
                        <button onclick={() => showConstellationsMenu = !showConstellationsMenu} 
                            class="p-1.5 text-copy-muted hover:text-white hover:bg-panel/40 rounded transition-all ml-1 cursor-pointer"
                            title={m.obs_sidedock_constellations_title()}>
                            {#if showConstellationsMenu}
                                <ChevronUp size={14}/>
                            {:else}
                                <ChevronDown size={14}/>
                            {/if}
                        </button>
                    {/if}
                </div>

                {#if showConstellations && showConstellationsMenu}
                    <div transition:slide={{ duration: 200 }} class="flex flex-col ml-4 border-l border-border/50 pl-1 my-1 overflow-hidden">
                        
                        <button onclick={() => showConstellationLabels = !showConstellationLabels} 
                            class="cursor-pointer flex items-center gap-2 px-2 py-1.5 rounded hover:bg-panel/40 text-[11px] {showConstellationLabels ? 'text-accent' : 'text-copy-muted'}">
                            <Tag size={12}/> {m.obs_sidedock_constellations_show_label()}
                        </button>
                        
                        <button onclick={() => useLatinConstellations = !useLatinConstellations} 
                            disabled={!showConstellationLabels}
                            class="cursor-pointer flex items-center justify-between px-2 py-1.5 rounded text-[11px] transition-opacity {showConstellationLabels ? 'hover:bg-panel/40 text-copy-primary' : 'opacity-40 cursor-not-allowed'}">
                            <div class="flex items-center gap-2">
                                <Languages size={12} class={useLatinConstellations ? 'text-accent' : 'text-copy-muted'}/> 
                                <span class={useLatinConstellations ? 'text-accent' : 'text-copy-muted'}>{m.obs_sidedock_constellations_language()}</span>
                            </div>
                            <span class="text-[9px] bg-panel/50 border border-border px-1.5 py-0.5 rounded font-bold uppercase transition-colors {useLatinConstellations ? 'text-accent border-accent/30' : 'text-copy-muted'}">
                                {m.obs_sidedock_constellations_language_options({latin:toInlangBool(useLatinConstellations)})}
                            </span>
                        </button>
                    </div>
                {/if}
                
                <button onclick={() => showGround = !showGround} 
                    class="cursor-pointer flex items-center gap-2 px-2 py-1.5 rounded hover:bg-panel/40 text-xs {showGround ? 'text-accent' : 'text-copy-muted'}">
                    <MountainSnow size={14}/> {m.obs_sidedock_horizon()}
                </button>
            </div>
        </div>
    </div>

    <div class="w-full h-px bg-border/50 my-1"></div>

    <button title={m.obs_ai_title()} onclick={() => chatOpen = !chatOpen} class="cursor-pointer p-3 rounded-full transition-all shadow-inner {chatOpen ? 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]' : 'hover:bg-panel/50 text-copy-muted hover:text-purple-400'}">
        <Sparkles size={20} />
    </button>
</div>