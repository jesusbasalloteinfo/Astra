<!-- src/routes/(app)/dashboard/+layout.svelte -->
<script lang="ts">
    import Sidebar from '$lib/components/dashboard/Sidebar.svelte';
    let { children } = $props();
</script>

<div class="min-h-screen flex bg-primary text-copy-primary">
    <Sidebar />
    <main class="flex-1 min-w-0 p-8">
        {@render children()}
    </main>
</div>