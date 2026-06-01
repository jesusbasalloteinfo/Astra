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
    import Sidebar from '$lib/components/dashboard/Sidebar.svelte';
    import MobileHeader from '$lib/components/dashboard/MobileHeader.svelte';
    import MobileBottomNav from '$lib/components/dashboard/MobileBottomNav.svelte';
    import FloatingActionButton from '$lib/components/dashboard/FloatingActionButton.svelte';
    import { fade } from 'svelte/transition';
    import { page } from '$app/state'; 
    let { children } = $props();
</script>

<div class="min-h-svh flex flex-col lg:flex-row bg-primary text-copy-primary">
    <div class="hidden lg:block">
        <Sidebar />
    </div>

    <MobileHeader />
    <MobileBottomNav />
    <FloatingActionButton />

    <main class="flex-1 min-w-0 p-4 pt-20 pb-28 lg:p-8 landscape:pt-16 landscape:pb-20 lg:landscape:pt-8 lg:landscape:pb-8 overflow-y-auto">
        {#key page.url.pathname}
            <div in:fade={{ duration: 300, delay: 50 }}>
                {@render children()}
            </div>
        {/key}
    </main>
</div>