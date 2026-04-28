<script lang="ts">
    import { deviceStore } from '$lib/stores/devices.svelte';
    import { Cpu, Trash2, Pen, Camera, Telescope, ChevronDown } from 'lucide-svelte';
    import Modal from '../ui/Modal.svelte';
    import * as m from '$lib/paraglide/messages.js';

    let { id, name, owner, isOnline } = $props(); 

    let showDeleteModal = $state(false);
    let showEditModal = $state(false);
    let editName = $state(name);

    const isActive = $derived(deviceStore.effectiveActiveId === id);
    const details = $derived(isActive ? deviceStore.activeDetails : null);

    async function handleDelete() {
        await deviceStore.deleteDevice(id);
        showDeleteModal = false;
    }

    async function handleUpdate() {
        if (!editName.trim()) return;
        await deviceStore.update(id, { name: editName });
        showEditModal = false;
    }

    function openEdit() {
        editName = name;
        showEditModal = true;
    }
</script>

<div class="group relative flex flex-col bg-panel border border-border rounded-xl transition-all duration-300
            {isActive ? 'border-accent/40 bg-accent/5' : 'hover:bg-surface'}">
    
    <button 
        onclick={() => deviceStore.select(id)}
        class="flex items-center gap-4 p-4 w-full cursor-pointer pr-24 text-left rounded-xl outline-none">
        
        <div class="p-2.5 rounded-xl transition-all duration-300
            {isActive 
                ? 'bg-accent text-white shadow-[0_0_15px_var(--color-accent-glow)]' 
                : 'bg-secondary/50 text-copy-muted group-hover:text-copy-primary'}">
            <Cpu size={18} />
        </div>

        <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-copy-primary truncate">{name}</span>
                
                {#if isActive}
                    <span class="text-[9px] font-bold text-accent uppercase tracking-tighter bg-accent/10 px-1.5 py-0.5 rounded">
                        {m.dash_device_active()}
                    </span>
                {/if}
            </div>
            
            <div class="flex items-center gap-3 text-[11px] font-mono text-copy-muted mt-1.5 opacity-80">
                <div class="flex items-center gap-1.5">
                    {#if isOnline}
                        <div class="w-1.5 h-1.5 bg-success rounded-full shadow-[0_0_5px_var(--color-success)] animate-pulse"></div>
                        <span class="text-success uppercase tracking-wider font-bold text-[9px]">{m.dash_device_online()}</span>
                    {:else}
                        <div class="w-1.5 h-1.5 bg-danger rounded-full"></div>
                        <span class="text-danger uppercase tracking-wider font-bold text-[9px]">{m.dash_device_offline()}</span>
                    {/if}
                </div>
                <span class="opacity-30">•</span>
                <span>ID: {id.substring(0,8)}...</span>
            </div>
        </div>
    </button>

    <div class="absolute top-4 right-3 opacity-0 group-hover:opacity-100 transition-all translate-x-2 group-hover:translate-x-0 flex items-center gap-1">
        <button 
            onclick={openEdit}
            class="cursor-pointer p-2 rounded-lg bg-panel border border-border text-copy-muted hover:text-accent hover:border-accent/30 transition-all shadow-sm">
            <Pen size={14} />
        </button>
        <button 
            onclick={() => showDeleteModal = true}
            class="cursor-pointer p-2 rounded-lg bg-panel border border-border text-copy-muted hover:text-danger hover:border-danger/30 transition-all shadow-sm">
            <Trash2 size={14} />
        </button>
    </div>

    {#if isActive}
        <div class="px-4 pb-4">
            <div class="pt-3 border-t border-border/50">
                {#if isOnline && details?.components}
                    <div class="grid grid-cols-2 gap-4">
                        
                        {#if details.components.telescope?.length}
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[9px] font-black uppercase text-copy-muted flex items-center gap-1.5">
                                    <Telescope size={12}/> {m.dash_device_telescope()}
                                </label>
                                <div class="relative">
                                    <select 
                                        value={deviceStore.selectedComponents[id]?.telescope || ''}
                                        onchange={(e) => deviceStore.setComponent(id, 'telescope', e.currentTarget.value)}
                                        class="w-full bg-secondary/50 border border-border rounded-lg pl-3 pr-8 py-2 text-[11px] text-copy-primary font-mono focus:outline-none focus:border-accent transition-colors appearance-none cursor-pointer truncate">
                                        {#each details.components.telescope as t}
                                            <option value={t}>{t}</option>
                                        {/each}
                                    </select>
                                    <ChevronDown size={12} class="absolute right-2.5 top-1/2 -translate-y-1/2 text-copy-muted pointer-events-none" />
                                </div>
                            </div>
                        {/if}
                        
                        {#if details.components.camera?.length}
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[9px] font-black uppercase text-copy-muted flex items-center gap-1.5">
                                    <Camera size={12}/> {m.dash_device_camera()}
                                </label>
                                <div class="relative">
                                    <select 
                                        value={deviceStore.selectedComponents[id]?.camera || ''}
                                        onchange={(e) => deviceStore.setComponent(id, 'camera', e.currentTarget.value)}
                                        class="w-full bg-secondary/50 border border-border rounded-lg pl-3 pr-8 py-2 text-[11px] text-copy-primary font-mono focus:outline-none focus:border-accent transition-colors appearance-none cursor-pointer truncate">
                                        {#each details.components.camera as c}
                                            <option value={c}>{c}</option>
                                        {/each}
                                    </select>
                                    <ChevronDown size={12} class="absolute right-2.5 top-1/2 -translate-y-1/2 text-copy-muted pointer-events-none" />
                                </div>
                            </div>
                        {/if}

                    </div>

                    {#if !details.components.telescope?.length && !details.components.camera?.length && !details.components.focuser?.length}
                        <p class="text-xs text-copy-muted italic mt-2">{m.dash_device_no_components()}</p>
                    {/if}
                {:else if isOnline && deviceStore.isFetchingDetails}
                    <p class="text-[10px] text-accent animate-pulse font-medium tracking-widest uppercase">{m.dash_device_fetching()}</p>
                {/if}
            </div>
        </div>
    {/if}
</div>

<Modal bind:open={showEditModal} title={m.dash_device_edit_title()}>
    <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <label for="edit-name" class="text-sm font-medium text-copy-muted">{m.dash_device_edit_name_label()}</label>
            <input
                id="edit-name"
                type="text"
                placeholder={m.dash_device_edit_name_placeholder()}
                bind:value={editName}
                class="w-full px-4 py-2 bg-secondary border border-border rounded-xl text-copy-primary focus:outline-none focus:border-accent transition-colors"
            />
        </div>
        <div class="flex justify-end gap-3 mt-4">
            <button onclick={() => showEditModal = false} class="cursor-pointer px-4 py-2 text-sm font-medium text-copy-muted hover:text-copy-primary">
                {m.dash_device_edit_cancel()}
            </button>
            <button onclick={handleUpdate} class="cursor-pointer px-4 py-2 bg-accent hover:bg-accent-hover text-white text-sm font-bold rounded-xl shadow-lg shadow-accent/20">
                {m.dash_device_edit_save()}
            </button>
        </div>
    </div>
</Modal>

<Modal bind:open={showDeleteModal} title={m.dash_device_del_title()} size="sm">
     <p class="text-sm text-copy-muted mb-6">
        {m.dash_device_del_confirm({ name })}
        {m.dash_device_del_warning()}
    </p>
    <div class="flex justify-end gap-3">
        <button onclick={() => showDeleteModal = false} class="cursor-pointer px-4 py-2 text-sm font-medium text-copy-muted hover:text-copy-primary">
            {m.dash_device_edit_cancel()}
        </button>
        <button onclick={handleDelete} class="cursor-pointer px-4 py-2 bg-danger-surface hover:opacity-90 text-danger text-sm font-bold rounded-xl transition-all shadow-lg shadow-danger-surface/20">
            {m.dash_device_del_action()}
        </button>
    </div>
</Modal>