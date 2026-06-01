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

<!-- src/lib/components/ui/Modal.svelte -->
<script lang="ts">
    import { X } from 'lucide-svelte';
    import { fade, scale } from 'svelte/transition';

    /**
     * Component props
     * @type {{ open: boolean, title?: string, size?: 'sm' | 'md' | 'lg' | 'xl', onclose?: () => void, children: any }}
     * @property {boolean} open - Whether the modal is currently open (bindable)
     * @property {string} [title=''] - Optional title to display in the modal header
     * @property {'sm'|'md'|'lg'|'xl'} [size='md'] - The size constraint of the modal
     * @property {() => void} [onclose] - Optional callback triggered when the modal closes
     * @property {any} children - The content to be rendered inside the modal
     */
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

    /**
     * Closes the modal and calls the onclose callback if provided
     */
    function close() {
        open = false;
        onclose?.();
    }

    /**
     * Handles backdrop clicks to close the modal
     * @param {MouseEvent} e - The mouse event
     */
    function handleBackdrop(e: MouseEvent) {
        if (e.target === e.currentTarget) close();
    }

    /**
     * Handles keyboard events to close the modal (e.g., Escape key)
     * @param {KeyboardEvent} e - The keyboard event
     */
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