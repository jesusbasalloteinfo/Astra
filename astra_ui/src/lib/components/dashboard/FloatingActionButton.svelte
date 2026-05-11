<!-- src/lib/components/dashboard/FloatingActionButton.svelte -->
<script lang="ts">
    import { Plus } from 'lucide-svelte';
    import { newObsStore } from '$lib/stores/newObservation.svelte';
    import { scale } from 'svelte/transition';
</script>

<div class="lg:hidden fixed bottom-20 landscape:bottom-16 right-4 z-30">
    <button 
        onclick={() => newObsStore.open()}
        in:scale={{ duration: 300, delay: 200, start: 0.5 }}
        class="w-14 h-14 landscape:w-12 landscape:h-12 bg-accent text-white rounded-full flex items-center justify-center shadow-lg shadow-accent/40 active:scale-90 active:bg-accent-hover transition-all"
        aria-label="New Session"
    >
        <Plus class="w-6 h-6" />
    </button>
</div>