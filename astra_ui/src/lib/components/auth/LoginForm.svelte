<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import * as m from '$lib/paraglide/messages.js';
    import { authStore } from '$lib/stores/auth.svelte';

    let { 
        /** Callback function to toggle between login and register modes */
        onToggleMode 
    } = $props<{ onToggleMode: () => void }>();

    /** Input value for the username field */
    let username = $state('');
    /** Input value for the password field */
    let password = $state('');
    /** Whether a login request is currently in progress */
    let loading = $state(false);
    /** Error message to display if login fails */
    let error = $state('');

    /**
     * Validates input and attempts to log in the user
     * Redirects to dashboard upon success
     */
    async function handleLogin() {
        if (!username.trim()) {
            error = m.login_no_user();
            return;
        }
        
        if (!password.trim()) {
            error = m.login_no_password();
            return;
        }

        loading = true;
        error = '';

        try {
            await authStore.login(username.trim(), password);
            const destination = page.url.searchParams.get('goto') ?? '/dashboard';
            goto(destination);
        } catch (e) {
            error = m.login_login_error();
        } finally {
            loading = false;
        }
    }
</script>

<div class="flex flex-col gap-5">
    <div class="flex flex-col gap-4">
        <!-- Username -->
        <div class="flex flex-col gap-2">
            <label for="username" class="text-sm font-medium text-slate-300">
                {m.login_username_input()}
            </label>
            <input
                id="username"
                type="text"
                bind:value={username}
                placeholder={m.login_username_input().toLowerCase()}
                class="w-full px-4 py-3 bg-white/5 border {error && !username ? 'border-red-500/50' : 'border-white/10 focus:border-blue-500/50'} rounded-xl text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 transition-all"
            />
        </div>

        <!-- Password -->
        <div class="flex flex-col gap-2">
            <label for="password" class="text-sm font-medium text-slate-300">
                {m.login_password_input()}
            </label>
            <input
                id="password"
                type="password"
                bind:value={password}
                placeholder="••••••••"
                onkeydown={(e) => e.key === 'Enter' && handleLogin()}
                class="w-full px-4 py-3 bg-white/5 border {error && !password ? 'border-red-500/50' : 'border-white/10 focus:border-blue-500/50'} rounded-xl text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 transition-all"
            />
        </div>

        {#if error}
            <p class="text-red-400 text-sm animate-in fade-in slide-in-from-top-1">{error}</p>
        {/if}
    </div>

    <button
        onclick={handleLogin}
        disabled={loading}
        class="w-full py-3.5 mt-2 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/30 active:scale-[0.98] flex justify-center items-center h-13">
        {#if loading}
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        {:else}
            {m.login_input_button()}
        {/if}
    </button>

    <button 
        onclick={onToggleMode}
        class="text-sm text-slate-400 hover:text-white transition-colors">
        {m.login_no_account()}
    </button>
</div>
