<script lang="ts">
    import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
    let { children } = $props();
</script>

<nav class="p-4 flex justify-end">
    <LanguageSwitcher />
</nav>

{@render children()}