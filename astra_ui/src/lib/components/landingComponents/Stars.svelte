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
    import { page } from '$app/state';

    /**
     * Creates a seeded pseudo-random number generator
     * @param {number} seed - The seed value to initialize the generator
     * @returns {() => number} A function that returns a pseudo-random number between 0 and 1
     */
    function seededRandom(seed: number) {
        return function() {
            seed = (seed * 9301 + 49297) % 233280;
            return seed / 233280;
        };
    }

	/** Seed value derived from server data to ensure hydration match */
    const seedValue = $derived(page.data.starSeed || 0.12345);
    
    /** Total number of stars to render */
    const STAR_COUNT = 75;
    
    /** Derived array of star properties generated from the seed */
    const stars = $derived.by(() => {
        const rnd = seededRandom(seedValue * 10000);
        return Array.from({ length: STAR_COUNT }).map((_, i) => ({
            id: i,
            top: `${rnd() * 100}%`,
            left: `${rnd() * 100}%`,
            size: (rnd() * 3) + 1,
            delay: `${rnd() * 5}s`,
            duration: `${rnd() * 3 + 2}s`,
            opacity: rnd() * 0.7 + 0.3
        }));
    });
</script>

<div class="fixed inset-0 pointer-events-none z-0 overflow-hidden" aria-hidden="true">
	{#each stars as star (star.id)}
		<div
			class="animate-twinkle absolute rounded-full bg-white transition-opacity duration-1000"
			style:top={star.top}
			style:left={star.left}
			style:width="{star.size}px"
			style:height="{star.size}px"
			style:animation-delay={star.delay}
			style:animation-duration={star.duration}
			style:opacity={star.opacity}
		></div>
	{/each}
</div>

<style>
	@keyframes twinkle {
		0%, 100% { 
            opacity: 0.3; 
            transform: scale(1); 
        }
		50% { 
            opacity: 1; 
            transform: scale(1.2); 
        }
	}
	
	.animate-twinkle {
		animation: twinkle ease-in-out infinite;
	}
</style>