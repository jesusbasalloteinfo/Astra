<script lang="ts">
	import { m } from "$lib/paraglide/messages";
	import { getLocale } from "$lib/paraglide/runtime";
	import { formatNumber, getMoonPhaseName } from "$lib/utils/i18n";

    /**
     * Component props
     * @type {{ age?: number, illuminationPct: number, nextNewMoon?: string | null, nextFullMoon?: string | null }}
     * @property {number} [age=0] - The age of the moon in days
     * @property {number} illuminationPct - The percentage of the moon that is illuminated
     * @property {string|null} [nextNewMoon=null] - ISO date string of the next new moon
     * @property {string|null} [nextFullMoon=null] - ISO date string of the next full moon
     */
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

    /** Whether the moon is currently in the "New Moon" phase */
    let isNewMoon = $derived(illuminationPct < 1);

    /** Whether the moon is currently in the "Full Moon" phase */
    let isFullMoon = $derived(illuminationPct > 99);

    /** Whether the moon is waxing (growing) */
    let isWaxing = $derived(age <= 14.76);

    /** Whether the moon is in a crescent phase (less than 50% illumination) */
    let isCrescent = $derived(illuminationPct < 50);
    
    /** X-radius for the SVG terminator ellipse, calculated based on illumination */
    let ellipseRx = $derived(50 * Math.abs(1 - 2 * (illuminationPct / 100)));

    /** Opacity of the moon's glow based on illumination */
    let glowOpacity = $derived((illuminationPct / 100) * 0.5);

    /** Blur amount for the moon's glow based on illumination */
    let glowBlur = $derived((illuminationPct / 100) * 12);

    /** Translated name of the current moon phase */
    let phaseName = $derived(getMoonPhaseName(isNewMoon, isFullMoon, isWaxing, isCrescent, illuminationPct));

    /**
     * Formats an ISO date string into a localized short date and time
     * @param {string|null|undefined} isoString - The ISO date string to format
     * @returns {string} Formatted date string or '—' if input is null/undefined
     */
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
            <h4 class="text-[10px] uppercase tracking-wider text-copy-muted mb-1">{m.obs_targetinfo_lunar_title()}</h4>
            <div class="flex flex-col gap-2">
                <div class="flex items-baseline gap-2">
                    <span class="text-xl font-bold text-white tabular-nums">{formatNumber(illuminationPct, 1)}%</span>
                    <span class="text-[10px] font-bold uppercase tracking-wider text-accent">{phaseName}</span>
                </div>
                <span class="text-[10px] text-copy-muted font-mono">{m.obs_targetinfo_lunar_age({ count: age.toFixed(1) })}</span>
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
                    <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5 block">{m.obs_targetinfo_lunar_next_new()}</span>
                    <span class="text-xs font-mono text-copy-primary">{formatPhaseDate(nextNewMoon)}</span>
                </div>
            {/if}
            
            {#if nextFullMoon}
                <div class="text-right">
                    <span class="text-[8px] uppercase font-bold text-copy-muted mb-0.5 block">{m.obs_targetinfo_lunar_next_full()}</span>
                    <span class="text-xs font-mono text-copy-primary">{formatPhaseDate(nextFullMoon)}</span>
                </div>
            {/if}
        </div>
    {/if}
</div>