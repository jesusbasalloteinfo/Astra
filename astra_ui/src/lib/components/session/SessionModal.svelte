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
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/ui/Modal.svelte';
    import { newObsStore } from '$lib/stores/newObservation.svelte';
    import { obsStore } from '$lib/stores/observations.svelte';
    import { m } from '$lib/paraglide/messages';
    import { Telescope, Sparkles, TextAlignStart, CircleAlert } from 'lucide-svelte';

    /** The name of the session being created */
    let name = $state('');

    /** The optional description of the session being created */
    let description = $state('');

    /** Whether the creation process is currently in progress */
    let isSubmitting = $state(false);

    /** Error message to display if creation fails */
    let errorMessage = $state<string | null>(null);

    /**
     * Handles the creation of a new session
     * Validates input, creates the session in the store, and redirects to the new session page
     */
    async function handleSubmit() {
        if (!name.trim() || isSubmitting) return;

        isSubmitting = true;
        errorMessage = null;
        try {
            const id = await obsStore.create({
                name: name.trim(),
                description: description.trim()
            });
            newObsStore.close();
            name = '';
            description = '';
            await goto(`/observation/${id}`);
        } catch (error: any) {
            console.error("Error creating session:", error);
            if (error.status === 409 || error.response?.status === 409) {
                errorMessage = m.dash_observ_error_exists();
            } else {
                errorMessage = "An unexpected error occurred";
            }
        } finally {
            isSubmitting = false;
        }
    }
</script>

<Modal bind:open={newObsStore.showNewObsModal} size="md">
    <div class="flex flex-col items-center gap-8 py-2">

        <!-- Header -->
        <div class="flex flex-col items-center gap-3">
            <div class="relative group">
                <div class="absolute inset-0 bg-accent/20 blur-xl rounded-full group-hover:bg-accent/30 transition-colors"></div>
                <div class="relative w-16 h-16 rounded-full bg-panel border border-white/10 flex items-center justify-center text-accent shadow-2xl">
                    <Telescope size={30} strokeWidth={1.5} />
                </div>
            </div>
            <div class="text-center">
                <h2 class="text-xl font-bold text-copy-primary tracking-tight">{m.dash_observ_new_session()}</h2>
                <p class="text-[10px] text-accent font-mono uppercase tracking-[0.2em] opacity-80">{m.dash_observ_new_subtitle()}</p>
            </div>
        </div>

        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="w-full space-y-6">

            {#if errorMessage}
                <div class="p-3 bg-danger/10 border border-danger/20 rounded-xl flex items-center gap-3 text-danger animate-in fade-in slide-in-from-top-2 duration-300">
                    <CircleAlert size={16} />
                    <p class="text-xs font-bold tracking-wide">{errorMessage}</p>
                </div>
            {/if}

            <!-- Name -->

            <div class="space-y-2 group">
                <label for="obs-name" class="text-[10px] font-bold text-copy-muted uppercase tracking-widest px-1 flex justify-between">
                    {m.dash_observ_edit_name_title()}
                    <span class="text-accent/50 text-[9px] group-focus-within:text-accent transition-colors">{m.dash_observ_new_required()}</span>
                </label>
                <input
                    id="obs-name"
                    bind:value={name}
                    placeholder={m.dash_observ_new_name_placeholder()}
                    class="w-full px-4 py-3 bg-secondary/30 border border-border rounded-xl text-copy-primary 
                           placeholder:text-copy-muted/30 focus:outline-none focus:border-accent/50 
                           focus:bg-secondary/50 transition-all shadow-inner"
                    required
                />
            </div>

            <!-- Description -->
            <div class="space-y-2">
                <label for="obs-desc" class="text-[10px] font-bold text-copy-muted uppercase tracking-widest px-1 flex items-center gap-2">
                    <TextAlignStart  size={10} />
                    {m.dash_observ_edit_description_title()}
                </label>
                <textarea
                    id="obs-desc"
                    bind:value={description}
                    placeholder={m.dash_observ_new_description_placeholder()}
                    rows="3"
                    class="w-full px-4 py-3 bg-secondary/30 border border-border rounded-xl text-copy-primary 
                           placeholder:text-copy-muted/30 focus:outline-none focus:border-accent/50 
                           focus:bg-secondary/50 transition-all shadow-inner resize-none text-sm leading-relaxed"
                ></textarea>
            </div>

            <!-- Actions -->
            <div class="flex flex-col gap-3 pt-2">
                <button 
                    type="submit"
                    disabled={isSubmitting || !name.trim()}
                    class="cursor-pointer w-full py-4 bg-accent hover:bg-accent-hover disabled:opacity-30 
                           text-white font-bold rounded-xl shadow-lg shadow-accent/20 transition-all
                           flex items-center justify-center gap-3 active:scale-[0.98]">
                    <span class="uppercase tracking-[0.15em] text-xs">
                        {isSubmitting ? m.dash_observ_action_creating() : m.dash_observ_action_create()}
                    </span>
                    <Sparkles size={14} class="opacity-70" />
                </button>

                <button 
                    type="button"
                    onclick={() => newObsStore.close()}
                    class="cursor-pointer text-[10px] font-bold text-copy-muted hover:text-copy-primary transition-colors py-2 uppercase tracking-widest">
                    {m.dash_observ_action_cancel()}
                </button>
            </div>
        </form>
    </div>
</Modal>