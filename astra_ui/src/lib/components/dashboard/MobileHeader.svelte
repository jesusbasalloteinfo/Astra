<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import MobileThemeSelector from './MobileThemeSelector.svelte';
    import MobileLanguageSelector from './MobileLanguageSelector.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
    import { User, LogOut, Settings, X } from 'lucide-svelte';
    import { authStore } from '$lib/stores/auth.svelte';
    import { obsStore } from '$lib/stores/observations.svelte';
    import { goto } from '$app/navigation';
    import { fade, fly } from 'svelte/transition';
	import ProfileSettings from './ProfileSettings.svelte';

    /** Whether the mobile settings/profile overlay is open */
    let isSettingsOpen = $state(false);
    /** Whether the profile settings modal is open */
    let profileOpen = $state(false);

    /**
     * Logs out the current user and redirects to the landing page
     */
    async function handleLogout() {
        const nav = goto('/');
        await authStore.logout();
        await nav;
    }
</script>

<header class="lg:hidden fixed top-0 left-0 right-0 bg-secondary/80 backdrop-blur-lg border-b border-border z-40 px-4 h-16 landscape:h-14 flex items-center justify-between">
    <a href="/dashboard" class="flex items-center gap-3">
        <AppLogo class="w-8 h-8 landscape:w-7 landscape:h-7" />
        <div class="flex flex-col justify-center">
            <span class="text-sm font-black text-copy-primary uppercase tracking-tight leading-none">{m.name().toUpperCase()}</span>
            <span class="text-[8px] text-accent font-bold tracking-widest uppercase mt-0.5">{m.dash_side_name().toUpperCase()}</span>
        </div>
    </a>

    <button 
        onclick={() => isSettingsOpen = true}
        class="flex items-center gap-2 p-1.5 pl-3 bg-surface border border-border rounded-full active:scale-95 transition-all"
    >
        <span class="text-xs font-bold text-copy-primary truncate max-w-20">{authStore.user?.username || 'User'}</span>
        <div class="w-8 h-8 landscape:w-7 landscape:h-7 rounded-full bg-accent/10 flex items-center justify-center text-accent border border-accent/20 overflow-hidden">
            {#if authStore.user?.profile_picture_url}
                <img src={authStore.user.profile_picture_url} alt="Profile" class="w-full h-full object-cover" />
            {:else}
                <User class="w-4 h-4 landscape:w-3.5 landscape:h-3.5" />
            {/if}
        </div>
    </button>
</header>

{#if isSettingsOpen}
    <button 
        class="fixed inset-0 w-full h-full bg-black/60 backdrop-blur-sm z-60 lg:hidden cursor-default"
        transition:fade={{ duration: 200 }}
        onclick={() => isSettingsOpen = false}
        aria-label="Close settings"
    ></button>

    <div 
        class="fixed inset-x-0 bottom-0 bg-panel border-t border-border z-70 lg:hidden rounded-t-4xl shadow-2xl max-h-[85svh] flex flex-col"
        transition:fly={{ y: '100%', duration: 300 }}
    >
        <div class="p-6 pb-4 border-b border-border flex items-center justify-between shrink-0">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-2xl bg-accent flex items-center justify-center text-white shadow-lg shadow-accent/20 overflow-hidden">
                    {#if authStore.user?.profile_picture_url}
                        <img src={authStore.user.profile_picture_url} alt="Profile" class="w-full h-full object-cover" />
                    {:else}
                        <User size={24} />
                    {/if}
                </div>
                <div>
                    <h3 class="text-lg font-bold text-copy-primary">{authStore.user?.username}</h3>
                    <p class="text-xs text-copy-muted">{authStore.user?.email}</p>
                </div>
            </div>
            <button 
                onclick={() => isSettingsOpen = false}
                class="p-2 bg-surface border border-border text-copy-muted rounded-full hover:text-copy-primary transition-colors"
            >
                <X size={20} />
            </button>
        </div>

        <div class="p-6 overflow-y-auto space-y-6">
            <MobileThemeSelector />
            <MobileLanguageSelector />

            <div class="grid grid-cols-2 gap-3 pt-4">
                <button
                    onclick={() => { profileOpen = true; isSettingsOpen = false; }}
                    class="flex items-center justify-center gap-2 px-4 py-3.5 rounded-xl bg-surface border border-border text-sm font-bold text-copy-secondary active:bg-border transition-all active:scale-95"
                >
                    <Settings size={18} />
                    {m.dash_side_profile()}
                </button>
                <button
                    onclick={handleLogout}
                    class="flex items-center justify-center gap-2 px-4 py-3.5 rounded-xl bg-danger/10 border border-danger/20 text-sm font-bold text-danger active:bg-danger/20 transition-all active:scale-95"
                >
                    <LogOut size={18} />
                    {m.dash_side_logout()}
                </button>
            </div>
        </div>
    </div>
{/if}

<Modal bind:open={profileOpen} title={m.dash_side_profile()} size="sm">
    <ProfileSettings />
</Modal>