<!-- src/lib/components/observation/TelescopePill.svelte -->
<script lang="ts">
    import { SatelliteDish } from 'lucide-svelte';
</script>

<button class="flex items-center gap-2 bg-surface backdrop-blur-xl border border-border rounded-full py-1.5 px-3 shadow-[0_4px_15px_rgba(0,0,0,0.3)] hover:bg-panel/40 transition-colors group pointer-events-auto">
    <div class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
    </div>
    <SatelliteDish size={12} class="text-copy-muted group-hover:text-copy-primary transition-colors" />
    <span class="text-[10px] font-bold text-copy-primary tracking-wider">DUMMY TELESCOPE</span>
</button>