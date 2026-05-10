<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import * as m from '$lib/paraglide/messages.js';
    import { authAPI } from '$lib/api/auth';

    import AuthLayout from '$lib/components/auth/AuthLayout.svelte';

    let username = $state('');
    let loading = $state(false);
    let error = $state('');

    async function handleLogin() {
        if (!username.trim()) {
            error = m.login_no_user();
            return;
        }

        loading = true;
        error = '';

        try {
            await authAPI.login(username.trim());
            const destination = page.url.searchParams.get('goto') ?? '/dashboard';
            goto(destination);
        } catch (e) {
            error = m.login_login_error();
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>{m.login_title({name: m.name().toUpperCase()})}</title>
    <meta name="description" content={m.login_title({name: m.name().toUpperCase()})} />
</svelte:head>

<AuthLayout 
    title={m.login_welcome()} 
    subtitle={m.login_input_msg()}
    backLink="/"
    backText={m.login_return_home()}
>
    <div class="flex flex-col gap-5">
        
        <div class="flex flex-col gap-2">
            <label for="username" class="text-sm font-medium text-slate-300">
                {m.login_username_input()}
            </label>
            <input
                id="username"
                type="text"
                bind:value={username}
                placeholder={m.login_username_input().toLowerCase()}
                onkeydown={(e) => e.key === 'Enter' && handleLogin()}
                aria-invalid={error ? 'true' : 'false'}
                class="w-full px-4 py-3.5 bg-white/5 border {error ? 'border-red-500/50 focus:border-red-500' : 'border-white/10 focus:border-blue-500/50'} rounded-xl text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 transition-all"
            />
            {#if error}
                <p class="text-red-400 text-sm mt-1 animate-in fade-in slide-in-from-top-1">{error}</p>
            {/if}
        </div>

        <button
            onclick={handleLogin}
            disabled={loading}
            class="w-full py-3.5 mt-2 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/30 active:scale-[0.98] flex justify-center items-center h-[52px]">
            {#if loading}
                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            {:else}
                {m.login_input_button()}
            {/if}
        </button>
    </div>
</AuthLayout>