<script lang="ts">
    import { page } from '$app/state';

    // Seeded random number generator to ensure SSR and Client match
    // while still being "random" on every refresh
    function seededRandom(seed: number) {
        return function() {
            seed = (seed * 9301 + 49297) % 233280;
            return seed / 233280;
        };
    }

	// Get the seed from the server load function
    const seedValue = $derived(page.data.starSeed || 0.12345);
    
    const STAR_COUNT = 75;
    
    // We use a derived to recalculate stars if the seed changes (e.g. navigation)
    // and to ensure the random generator starts fresh with the same seed
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