<!-- src/lib/components/dashboard/MobileBottomNav.svelte -->
<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { LayoutDashboard, History, Telescope, MapPin } from 'lucide-svelte';
    import { page } from '$app/state';

    const navItems = $derived([
        { href: '/dashboard',           icon: LayoutDashboard, label: m.dash_side_home() },
        { href: '/dashboard/sessions',  icon: History,         label: m.dash_side_sessions() },
        { href: '/dashboard/devices',   icon: Telescope,       label: m.dash_side_telescope() },
        { href: '/dashboard/location',  icon: MapPin,          label: m.dash_side_location() },
    ]);
</script>

<nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-secondary/90 backdrop-blur-lg border-t border-border z-40 pb-safe">
    <div class="flex items-center justify-around h-16 landscape:h-12 px-2">
        {#each navItems as item}
            {@const isActive = page.url.pathname === item.href || (item.href !== '/dashboard' && page.url.pathname.startsWith(item.href))}
            <a 
                href={item.href} 
                class="flex flex-col items-center justify-center w-full h-full gap-1 transition-colors {isActive ? 'text-accent' : 'text-copy-secondary hover:text-copy-primary'}"
            >
                <item.icon class="w-5 h-5 landscape:w-4 landscape:h-4 {isActive ? 'stroke-[2.5px]' : 'stroke-2'}" />
                <span class="text-[10px] font-bold uppercase tracking-tight {isActive ? 'opacity-100' : 'opacity-70'} landscape:hidden">{item.label}</span>
            </a>
        {/each}
    </div>
</nav>
