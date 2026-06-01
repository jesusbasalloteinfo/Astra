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

<!-- src/lib/components/dashboard/Sidebar.svelte -->
<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import NavItem from '$lib/components/dashboard/NavItem.svelte';
    import ThemeSelector from '$lib/themes/ThemeSelector.svelte';
    import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
    import ProfileSettings from '$lib/components/dashboard/ProfileSettings.svelte';
    import { LayoutDashboard, History, Telescope, MapPin, User, Plus, LogOut } from 'lucide-svelte';
    import { authStore } from '$lib/stores/auth.svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { obsStore } from '$lib/stores/observations.svelte';
	import { newObsStore } from '$lib/stores/newObservation.svelte';

    /** Sidebar navigation items configuration */
    const navItems = [
        { href: '/dashboard',           icon: LayoutDashboard, label: m.dash_side_home() },
        { href: '/dashboard/sessions',  icon: History,         label: m.dash_side_sessions() },
        { href: '/dashboard/devices',   icon: Telescope,       label: m.dash_side_devices() },
        { href: '/dashboard/location',  icon: MapPin,          label: m.dash_side_location() },
    ];

    /** Whether the profile settings modal is open */
    let profileOpen = $state(false);

    /**
     * Logs out the current user and redirects to the landing page
     */
    async function handleLogout() {
        const destination = '/';
        // Start navigation first
        const nav = goto(destination);
        // Then perform logout cleanup
        await authStore.logout();
        await nav;
    }
</script>

<aside class="w-70 shrink-0 flex flex-col border-r border-border bg-secondary h-screen sticky top-0">

    <!-- Logo -->
    <div class="px-5 py-5 border-b border-border">
        <a href="/" class="flex items-center gap-3 hover:opacity-70 transition-opacity">
            <AppLogo class="w-8 h-8" />
            <div>
                <p class="text-sm font-bold text-copy-primary leading-none">{m.name().toUpperCase()}</p>
                <p class="text-[9px] tracking-widest text-accent mt-0.5">{m.dash_side_name().toUpperCase()}</p>
            </div>
        </a>
    </div>

    <!-- New session CTA -->
    <div class="px-4 pt-4">
        <button 
            onclick={() => newObsStore.open()}
            class="cursor-pointer w-full flex items-center justify-center gap-2 py-2.5 rounded-lg
                bg-accent hover:bg-accent-hover text-white text-sm font-semibold transition-colors">
            <Plus size={16} />
            {m.dash_side_new_session()}
        </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 flex flex-col gap-2">
        {#each navItems as item}
            <NavItem href={item.href} icon={item.icon} label={item.label} />
        {/each}
    </nav>

    <!-- Bottom -->
    <div class="px-4 py-4 border-t border-border flex flex-col gap-3">
        <div class="flex items-center gap-2">
            <ThemeSelector 
                class="flex-1 min-w-0" 
                placement="top" 
                classButton="bg-surface border border-border text-copy-secondary hover:text-copy-primary hover:bg-panel rounded-lg"
                classDropdown="bg-panel border border-border rounded-xl"
            />
            <LanguageSwitcher
                placement="top"
                classButton="bg-surface border border-border text-copy-secondary hover:text-copy-primary hover:bg-panel rounded-lg px-2 py-2 flex-shrink-0"
                classDropdown="bg-panel border border-border rounded-xl"
                classActive="bg-surface text-accent font-semibold"
                classInactive="text-copy-secondary hover:bg-surface hover:text-copy-primary" />
        </div>
        <button
            onclick={() => profileOpen = true}
            class="cursor-pointer flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                   text-copy-secondary hover:text-copy-primary hover:bg-surface transition-colors w-full text-left">
            {#if authStore.user?.profile_picture_url}
                <img src={authStore.user.profile_picture_url} alt="Profile" class="w-4.25 h-4.25 rounded-full object-cover" />
            {:else}
                <User size={17} />
            {/if}
            {m.dash_side_profile()}
        </button>
        <button
            onclick={handleLogout}
            class="cursor-pointer flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-copy-secondary hover:text-danger hover:bg-danger-surface transition-colors w-full text-left">
            <LogOut size={17} />
            {m.dash_side_logout()}
        </button>
                
    </div>
</aside>

<!-- Profile modal -->
<Modal bind:open={profileOpen} title={m.dash_side_profile()} size="sm">
    <ProfileSettings />
</Modal>