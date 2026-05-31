<script lang="ts">
    import { Calendar, History, ChevronRight, Trash2, Pencil } from 'lucide-svelte';
    import { obsStore } from '$lib/stores/observations.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
	import { m } from '$lib/paraglide/messages';
	import { formatDate } from '$lib/utils/date';
	import { locStore } from '$lib/stores/location.svelte';
	import { authStore } from '$lib/stores/auth.svelte';

    /**
     * Component props
     * @type {{ id: string, name: string, creation: string, lastUsed: string, telescope?: string, description?: string | null }}
     * @property {string} id - The unique ID of the observation session
     * @property {string} name - The name of the session
     * @property {string} creation - ISO date string of session creation
     * @property {string} lastUsed - ISO date string of last session activity
     * @property {string} [telescope='Generic'] - Name of the telescope used
     * @property {string|null} [description=null] - Optional description of the session
     */
	let { id, name, creation, lastUsed, telescope = 'Generic', description= null } = $props();

    /** Whether the delete confirmation modal is visible */
	let showDeleteModal = $state(false);

    /** Whether the edit session modal is visible */
	let showEditModal = $state(false);

    /** The name value currently being edited in the modal */
	let editName = $state(name);

    /** The description value currently being edited in the modal */
	let editDescription = $state(description || '');

    /** Formatted creation date string */
	const formattedCreation = $derived(formatDate(creation));
    /** Formatted last activity date string */
	const formattedActivity = $derived(formatDate(lastUsed));

    /** Whether there is at least one location available in the store */
	const hasLocation = $derived(locStore.all.length > 0);

    /** Whether the application state is ready (auth not loading) */
	const isReady = $derived(!authStore.isLoading);

    /**
     * Deletes the session from the store and closes the modal
     */
    async function handleDelete() {
        await obsStore.remove(id);
        showDeleteModal = false;
    }

    /**
     * Updates the session details in the store and closes the modal
     */
    async function handleUpdate() {
        await obsStore.update(id, { 
            name: editName,
            description: editDescription 
        });
        showEditModal = false;
    }
</script>

<div class="group relative flex items-center">
    <a href={(hasLocation && isReady) ? `/observation/${id}` : undefined}
       class="flex flex-1 items-center gap-3 md:gap-4 p-3 md:p-4 bg-panel border border-border rounded-xl
              transition-all pr-24 md:pr-12 [@media(hover:none)]:pr-24
              {(hasLocation && isReady) ? 'hover:bg-surface cursor-pointer' : 'opacity-60 cursor-not-allowed'}">
        
        <div class="w-1 self-stretch rounded-full shadow-[0_0_10px_var(--color-accent-glow)] {(hasLocation && isReady) ? 'bg-accent' : 'bg-copy-muted'}"></div>

        <div class="flex-1 min-w-0 space-y-1.5 md:space-y-2">
            <div class="text-sm font-bold text-copy-primary truncate {(hasLocation && isReady) ? '' : 'text-copy-muted'}">{name}</div>
            {#if description!=null}
                <div class="text-[11px] md:text-xs text-copy-muted line-clamp-1">{description || m.dash_observ_no_description()}</div>
            {/if}
            <div class="flex items-center gap-3 md:gap-4 text-[10px] md:text-xs text-copy-muted">
                <span class="flex items-center gap-1" title={m.dash_observ_creation_date()}><Calendar size={11} /> {formattedCreation}</span>
                <span class="flex items-center gap-1" title={m.dash_observ_last_activity()}><History size={11} /> {formattedActivity}</span>
                <!-- <span class="flex items-center gap-1"><Telescope size={11} /> {telescope}</span> -->
            </div>
        </div>

        <!-- Hidden when inside -->
        <div class="transition-opacity duration-200 group-hover:opacity-0 hidden md:block">
            {#if hasLocation && isReady}
                <ChevronRight size={16} class="text-copy-muted" />
            {/if}
        </div>
    </a>

    <!-- Action buttons -->
    <div class="absolute right-3 flex items-center gap-1.5 transition-all
                md:opacity-0 md:group-hover:opacity-100 
                md:translate-x-2 md:group-hover:translate-x-0
                [@media(hover:none)]:opacity-100 [@media(hover:none)]:translate-x-0">
        <button 
            onclick={() => showEditModal = true}
            class="cursor-pointer p-2 rounded-lg bg-panel border border-border text-copy-muted hover:text-accent hover:border-accent/30 transition-all shadow-sm active:scale-90">
            <Pencil size={14} />
        </button>
        <button 
            onclick={() => showDeleteModal = true}
            class="cursor-pointer p-2 rounded-lg bg-panel border border-border text-copy-muted hover:text-danger hover:border-danger/30 transition-all shadow-sm active:scale-90">
            <Trash2 size={14} />
        </button>
    </div>
</div>

<!-- Edit Modal -->
<Modal bind:open={showEditModal} title={m.dash_observ_edit_title()}>
    <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <label for="edit-name" class="text-sm font-medium text-copy-muted">{m.dash_observ_edit_name_title()}</label>
            <input
                id="edit-name"
                type="text"
                placeholder={m.dash_observ_edit_name_title()}
                bind:value={editName}
                class="w-full px-4 py-2 bg-secondary border border-border rounded-xl text-copy-primary focus:outline-none focus:border-accent transition-colors"
            />
        </div>
        <div class="flex flex-col gap-2">
            <label for="edit-description" class="text-sm font-medium text-copy-muted">{m.dash_observ_edit_description_title()}</label>
            <textarea
                id="edit-description"
                rows="3"
                placeholder={m.dash_observ_edit_description_title()}
                bind:value={editDescription}
                class="w-full px-4 py-2 bg-secondary border border-border rounded-xl text-copy-primary focus:outline-none focus:border-accent transition-colors resize-none"
            ></textarea>
        </div>
        <div class="flex justify-end gap-3 mt-4">
            <button onclick={() => showEditModal = false} class="cursor-pointer px-4 py-2 text-sm font-medium text-copy-muted">
                {m.dash_observ_action_cancel()}
            </button>
            <button onclick={handleUpdate} class="cursor-pointer px-4 py-2 bg-accent hover:bg-accent-hover text-white text-sm font-bold rounded-xl shadow-lg shadow-accent/20">
                {m.dash_observ_action_save()}
            </button>
        </div>
    </div>
</Modal>

<!-- Delete Modal -->
<Modal bind:open={showDeleteModal} title={m.dash_observ_del_title()} size="sm">
    <p class="text-sm text-copy-muted mb-6">
        {m.dash_observ_del_title_prefix()}
        <span class="text-copy-primary font-medium">"{name}"</span>
        {m.dash_observ_del_title_suffix()}
    </p>
    <div class="flex justify-end gap-3">
        <button onclick={() => showDeleteModal = false} class="cursor-pointer px-4 py-2 text-sm font-medium text-copy-muted hover:text-copy-primary">
            {m.dash_observ_action_cancel()}
        </button>
        <button onclick={handleDelete} class="cursor-pointer px-4 py-2 bg-danger-surface hover:opacity-90 text-danger text-sm font-bold rounded-xl transition-all shadow-lg shadow-danger-surface/20">
            {m.dash_observ_action_delete()}
        </button>
    </div>
</Modal>
