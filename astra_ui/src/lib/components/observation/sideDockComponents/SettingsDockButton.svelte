<!-- src/lib/components/observation/sideDockComponents/SettingsDockButton.svelte -->
<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { toInlangBool } from '$lib/utils/i18n';
    import { Settings2, GitBranch, MountainSnow, Tag, Languages, Layers, Cloud } from 'lucide-svelte';
    import DockPopover from './DockPopover.svelte';
    import ConfigEntry from './ConfigEntry.svelte';

    let {
        showConstellations = $bindable(),
        showConstellationLabels = $bindable(),
        useLatinConstellations = $bindable(),
        showGround = $bindable(),
        solidGround = $bindable(),
        showAtmosphere = $bindable(),
        atmosphereLocked = false
    } = $props();

    let showConstellationsMenu = $state(showConstellations);
    let showGroundMenu = $state(solidGround);

    function toggleConstellations() {
        showConstellations = !showConstellations;
        showConstellationsMenu = showConstellations;
    }
</script>

<DockPopover 
    icon={Settings2} 
    title={m.obs_sidedock_settings()} 
    buttonTitle={m.obs_sidedock_settings()}
>
    <!-- Constellations -->
    <ConfigEntry 
        icon={GitBranch}
        label={m.obs_sidedock_constellations_title()}
        active={showConstellations}
        onToggle={toggleConstellations}
        submenuOpen={showConstellationsMenu}
        onToggleSubmenu={() => showConstellationsMenu = !showConstellationsMenu}
    >
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
    </ConfigEntry>

    <!-- Atmosphere Toggle -->
    <ConfigEntry 
        icon={Cloud}
        label={m.obs_sidedock_atmosphere()}
        active={showAtmosphere}
        disabled={atmosphereLocked}
        onToggle={() => showAtmosphere = !showAtmosphere}
    />

    <!-- Horizon Menu -->
    <ConfigEntry 
        icon={MountainSnow}
        label={m.obs_sidedock_horizon()}
        active={showGround}
        onToggle={() => showGround = !showGround}
        submenuOpen={showGroundMenu}
        onToggleSubmenu={() => showGroundMenu = !showGroundMenu}
    >
        <button onclick={() => solidGround = !solidGround} 
            class="cursor-pointer flex items-center justify-between px-2 py-1.5 rounded text-[11px] hover:bg-panel/40 transition-colors">
            <div class="flex items-center gap-2 {solidGround ? 'text-accent' : 'text-copy-muted'}">
                <Layers size={12}/> 
                <span>{solidGround ? m.obs_sidedock_horizon_solid() : m.obs_sidedock_horizon_radar()}</span>
            </div>
        </button>
    </ConfigEntry>
</DockPopover>