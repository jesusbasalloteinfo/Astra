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
   class="flex items-center justify-start gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
          {active
              ? 'bg-surface text-copy-primary'
              : 'text-copy-secondary hover:text-copy-primary hover:bg-surface'}">
    <Icon size={17} class={active ? 'text-accent' : ''} />
    {label}
</a>