<script lang="ts">
	import { getLocale } from "$lib/paraglide/runtime";
	import { formatNumber } from "$lib/utils/i18n";

    let { 
        age = 0, 
        illuminationPct = 0,
        nextNewMoon = null,
        nextFullMoon = null
    } = $props<{ 
        age?: number; 
        illuminationPct: number; 
        nextNewMoon?: string | null;
        nextFullMoon?: string | null;
    }>();

    let isNewMoon = $derived(illuminationPct < 1);
    let isFullMoon = $derived(illuminationPct > 99);
    let isWaxing = $derived(age <= 14.76);
    let isCrescent = $derived(illuminationPct < 50);
    
    // SVG rendering
    let ellipseRx = $derived(50 * Math.abs(1 - 2 * (illuminationPct / 100)));
    let glowOpacity = $derived((illuminationPct / 100) * 0.5);
    let glowBlur = $derived((illuminationPct / 100) * 12);

    let phaseName = $derived.by(() => {
        if (isNewMoon) return 'New Moon';
        if (isFullMoon) return 'Full Moon';
        
        if (isWaxing) {
            if (illuminationPct > 47 && illuminationPct < 53) return 'First Quarter';
            return isCrescent ? 'Waxing Crescent' : 'Waxing Gibbous';
        } else {
            if (illuminationPct > 47 && illuminationPct < 53) return 'Last Quarter';
            return isCrescent ? 'Waning Crescent' : 'Waning Gibbous';
        }
    });

    function formatPhaseDate(isoString: string | null | undefined) {
        if (!isoString) return '—';
        const date = new Date(isoString);
        return date.toLocaleDateString(getLocale(), { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
</script>
<div class="bg-panel/30 rounded-xl p-4 border border-border shadow-inner flex flex-col gap-2.5 group">
    
    <!-- Upper part: Phase and SVG -->
    <div class="flex items-center justify-between">
        <div>
            <h4 class="text-[10px] uppercase tracking-wider text-copy-muted mb-1">Lunar Phase</h4>
            <div class="flex flex-col gap-2">
                <div class="flex items-baseline gap-2">
                    <span class="text-xl font-bold text-white tabular-nums">{formatNumber(illuminationPct, 1)}%</span>
                    <span class="text-[10px] font-bold uppercase tracking-wider text-accent">{phaseName}</span>
                </div>
                <span class="text-[10px] text-copy-muted font-mono">{formatNumber(age, 1)} days old</span>
            </div>
        </div>
        
        <div 
            class="relative w-12 h-12 group-hover:scale-105 transition-all duration-700"
            style="filter: drop-shadow(0 0 {glowBlur}px rgba(255,255,255,{glowOpacity}));"
        >
            <svg viewBox="0 0 100 100" class="w-full h-full rounded-full rotate-[-15deg]">
                <defs>
                    <!-- Illuminated -->
                    <radialGradient id="moonBright" cx="30%" cy="30%" r="70%">
                        <stop offset="0%" stop-color="#ffffff" />
                        <stop offset="100%" stop-color="#e2e8f0" />
                    </radialGradient>
                    
                    <!-- Darkened -->
                    <radialGradient id="moonDark" cx="50%" cy="50%" r="50%">
                        <stop offset="50%" stop-color="#0f172a" /> <!-- Slate-950 -->
                        <stop offset="100%" stop-color="#1e293b" /> <!-- Slate-800 -->
                    </radialGradient>
                </defs>

                <!-- 1: Dark background -->
                <circle cx="50" cy="50" r="50" fill="url(#moonDark)" />
                
                <!-- 2: Ghost border -->
                <circle cx="50" cy="50" r="49.5" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
                
                <!-- 3: Illuminated area -->
                {#if isFullMoon}
                    <!-- Full Moon -->
                    <circle cx="50" cy="50" r="50" fill="url(#moonBright)" />
                {:else if !isNewMoon}
                    <!-- Drawing for intermediate Moon -->
                    
                    {#if isWaxing}
                        <path d="M 50 0 A 50 50 0 0 1 50 100 Z" fill="url(#moonBright)" />
                    {:else}
                        <path d="M 50 0 A 50 50 0 0 0 50 100 Z" fill="url(#moonBright)" />
                    {/if}

                    <!-- 4: Terminator ellipse -->
                    <ellipse 
                        cx="50" cy="50" 
                        rx={ellipseRx} ry="50" 
                        fill={isCrescent ? "url(#moonDark)" : "url(#moonBright)"} 
                    />
                {/if}
                <!-- New Moon, do nothing -->
            </svg>
        </div>
    </div>
    <!-- Lower part: Next phases -->
    {#if nextNewMoon || nextFullMoon}
        <div class="grid grid-cols-2 gap-2 pt-3 border-t border-border/50">
            {#if nextNewMoon}
                <div>
                    <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5 block">Next New</span>
                    <span class="text-xs font-mono text-copy-primary">{formatPhaseDate(nextNewMoon)}</span>
                </div>
            {/if}
            
            {#if nextFullMoon}
                <div class="text-right">
                    <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5 block">Next Full</span>
                    <span class="text-xs font-mono text-copy-primary">{formatPhaseDate(nextFullMoon)}</span>
                </div>
            {/if}
        </div>
    {/if}
</div>