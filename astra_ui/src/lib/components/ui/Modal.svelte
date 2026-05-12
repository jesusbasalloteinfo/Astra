<!-- src/lib/components/ui/Modal.svelte -->
<script lang="ts">
    import { X } from 'lucide-svelte';
    import { fade, scale } from 'svelte/transition';

    let {
        open = $bindable(false),
        title = '',
        size = 'md',
        onclose,
        children,
    }: {
        open: boolean;
        title?: string;
        size?: 'sm' | 'md' | 'lg' | 'xl';
        onclose?: () => void;
        children: any;
    } = $props();

    const sizes = {
        sm: 'max-w-sm',
        md: 'max-w-md',
        lg: 'max-w-lg',
        xl: 'max-w-2xl',
    };

    function close() {
        open = false;
        onclose?.();
    }

    function handleBackdrop(e: MouseEvent) {
        if (e.target === e.currentTarget) close();
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') close();
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
    <!-- Backdrop -->
    <div
        transition:fade={{ duration: 150 }}
        onclick={handleBackdrop}
        onkeydown={handleKeydown}
        role="presentation"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm cursor-default outline-none">

        <!-- Panel -->
        <div
            transition:scale={{ duration: 150, start: 0.95 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'modal-title' : undefined}
            class="w-full {sizes[size]} bg-panel border border-border rounded-2xl shadow-2xl flex flex-col max-h-[95svh]">

            <!-- Header -->
            {#if title}
                <div class="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
                    <h2 class="text-base font-semibold text-copy-primary">{title}</h2>
                    <button
                        onclick={close}
                        class="cursor-pointer text-copy-muted hover:text-copy-primary transition-colors p-1 rounded-lg hover:bg-surface">
                        <X size={18} />
                    </button>
                </div>
            {:else}
                <div class="flex items-center justify-end px-6 py-4 shrink-0">
                    <button
                        onclick={close}
                        class="cursor-pointer text-copy-muted hover:text-copy-primary transition-colors p-1 rounded-lg bg-panel/50 backdrop-blur hover:bg-surface">
                        <X size={18} />
                    </button>
                </div>
            {/if}

            <!-- Content -->
            <div class="px-6 py-4 overflow-y-auto flex-1 no-scrollbar">
                {@render children()}
            </div>
        </div>
    </div>
{/if}