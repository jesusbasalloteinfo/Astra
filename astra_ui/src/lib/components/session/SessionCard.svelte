<script lang="ts">
    import { Calendar, Clock, Telescope, ChevronRight } from 'lucide-svelte';

    let {
        id,
        name,
        date,
        duration,
        telescope,
        objectsObserved = 0,
        type = 'observation',
    }: {
        id: string;
        name: string;
        date: string;
        duration: string;
        telescope: string;
        objectsObserved?: number;
        type?: 'observation' | 'learning';
    } = $props();

    const typeStyles = {
        observation: 'bg-accent/10 text-accent',
        learning:    'bg-purple-500/10 text-purple-400',
    };
</script>

<a href="/sessions/{id}"
   class="group flex items-center gap-4 p-4 bg-panel border border-border rounded-xl
          hover:bg-surface transition-colors cursor-pointer">

    <!-- Type indicator -->
    <div class="w-1 self-stretch rounded-full {type === 'observation' ? 'bg-accent' : 'bg-purple-400'}"></div>

    <!-- Info -->
    <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-2">
            <span class="text-sm font-semibold text-copy-primary truncate">{name}</span>
            <span class="text-[10px] font-medium px-2 py-0.5 rounded-full {typeStyles[type]}">
                {type}
            </span>
        </div>
        <div class="flex items-center gap-4 text-xs text-copy-muted">
            <span class="flex items-center gap-1">
                <Calendar size={11} />
                {date}
            </span>
            <span class="flex items-center gap-1">
                <Clock size={11} />
                {duration}
            </span>
            <span class="flex items-center gap-1">
                <Telescope size={11} />
                {telescope}
            </span>
        </div>
    </div>

    <!-- Objects count -->
    <div class="text-right flex-shrink-0">
        <p class="text-lg font-bold text-copy-primary">{objectsObserved}</p>
        <p class="text-[10px] text-copy-muted">objects</p>
    </div>

    <!-- Arrow -->
    <ChevronRight size={16} class="text-copy-muted group-hover:text-copy-primary group-hover:translate-x-0.5 transition-all flex-shrink-0" />
</a>