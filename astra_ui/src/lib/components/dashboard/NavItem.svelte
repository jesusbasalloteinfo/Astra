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

<!-- src/lib/components/dashboard/NavItem.svelte -->
<script lang="ts">
    import { page } from '$app/state';
    import type { Component } from 'svelte';

    let {
        /** Destination URL for the navigation link */
        href,
        /** Icon component to display */
        icon: Icon,
        /** Text label for the navigation link */
        label,
    }: {
        href: string;
        icon: any;
        label: string;
    } = $props();

    /** Whether the navigation item is currently active based on the URL path */
    let active = $derived(page.url.pathname === href);
</script>

<a {href}
   class="relative flex items-center justify-start gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
          {active
              ? 'bg-surface text-copy-primary font-semibold shadow-xs'
              : 'text-copy-secondary hover:text-copy-primary hover:bg-surface'}">
    {#if active}
        <span class="absolute left-0 top-2 bottom-2 w-1 bg-accent rounded-r-full"></span>
    {/if}
    <Icon size={17} class="transition-colors duration-200 {active ? 'text-accent' : ''}" />
    {label}
</a>