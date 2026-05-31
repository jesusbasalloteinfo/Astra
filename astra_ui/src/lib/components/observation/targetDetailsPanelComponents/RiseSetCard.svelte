<script lang="ts">
    import { Sunrise, Sunset, Navigation } from 'lucide-svelte';
    import { m } from '$lib/paraglide/messages';

    /**
     * Component props
     * @type {{ rise?: string, transit?: string, set?: string }}
     * @property {string} [rise='—'] - Local time of the object's rise
     * @property {string} [transit='—'] - Local time of the object's transit (highest point)
     * @property {string} [set='—'] - Local time of the object's set
     */
    let { 
        rise = '—', 
        transit = '—', 
        set = '—' 
    } = $props<{ 
        rise?: string; 
        transit?: string; 
        set?: string; 
    }>();
</script>

<div class="bg-panel/20 rounded-xl p-3 border border-border">
    <h3 class="text-[10px] text-copy-muted uppercase tracking-widest mb-3">{m.obs_targetinfo_riseset_title()}</h3>
    
    <div class="grid grid-cols-3 items-center divide-x divide-border/50 text-copy-primary">
        
        <div class="flex flex-col items-center gap-1">
            <Sunrise size={16} class="text-orange-400/80" />
            <div class="flex flex-col items-center">
                <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5">{m.obs_targetinfo_riseset_rise()}</span>
                <span class="text-xs font-mono font-medium">{rise}</span>
            </div>
        </div>
        
        <div class="flex flex-col items-center gap-1 pl-1">
            <Navigation size={16} class="text-blue-400/80" />
            <div class="flex flex-col items-center">
                <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5">{m.obs_targetinfo_riseset_transit()}</span>
                <span class="text-xs font-mono font-medium">{transit}</span>
            </div>
        </div>
        
        <div class="flex flex-col items-center gap-1 pl-1">
            <Sunset size={16} class="text-purple-400/80" />
            <div class="flex flex-col items-center">
                <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5">{m.obs_targetinfo_riseset_set()}</span>
                <span class="text-xs font-mono font-medium">{set}</span>
            </div>
        </div>
        
    </div>
</div>