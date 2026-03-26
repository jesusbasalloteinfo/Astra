<script lang="ts">
	let stars = $state<{id: number, top: string, left: string, size: number, delay: string, duration: string, opacity: number}[]>([]);

	// $effect only runs in browser for good hidration
	$effect(() => {
		const starCount = 75; 
		stars = Array.from({ length: starCount }).map((_, i) => ({
			id: i,
			top: `${Math.random() * 100}%`,
			left: `${Math.random() * 100}%`,
			size: Math.random() * 3 + 1,
			delay: `${Math.random() * 5}s`,
			duration: `${Math.random() * 3 + 2}s`,
			opacity: Math.random() * 0.7 + 0.3
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