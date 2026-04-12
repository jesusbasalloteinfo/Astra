<!-- src/lib/components/dashboard/NavItem.svelte -->
<script lang="ts">
    import { page } from '$app/state';
    import type { Component } from 'svelte';

    let {
        href,
        icon: Icon,
        label,
    }: {
        href: string;
        icon: any;
        label: string;
    } = $props();

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