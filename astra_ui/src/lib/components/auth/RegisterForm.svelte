<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import * as m from '$lib/paraglide/messages.js';
    import { authStore } from '$lib/stores/auth.svelte';
    import { authAPI } from '$lib/api/auth';

    let { 
        /** Callback function to toggle between login and register modes */
        onToggleMode 
    } = $props<{ onToggleMode: () => void }>();

    /** Input value for the username field */
    let username = $state('');
    /** Input value for the email field */
    let email = $state('');
    /** Input value for the password field */
    let password = $state('');
    /** Input value for the password confirmation field */
    let confirmPassword = $state('');
    /** Whether a registration request is currently in progress */
    let loading = $state(false);
    /** Error message to display if registration fails */
    let error = $state('');

    /** Regular expression for basic email validation */
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    /**
     * Validates input and attempts to register a new user
     * Auto-logs in the user and redirects to dashboard upon success
     */
    async function handleRegister() {
        // Validations
        if (!username.trim()) {
            error = m.login_no_user();
            return;
        }
        
        if (!email.trim()) {
            error = m.login_no_email();
            return;
        }
        if (!emailRegex.test(email.trim())) {
            error = m.login_invalid_email();
            return;
        }

        if (!password.trim()) {
            error = m.login_no_password();
            return;
        }

        if (password.length < 8) {
            error = m.login_password_too_short();
            return;
        }
        if (password !== confirmPassword) {
            error = m.login_passwords_not_match();
            return;
        }

        loading = true;
        error = '';

        try {
            await authAPI.register(username.trim(), email.trim(), password);
            // Auto-login after register, syncing current UI settings
            await authStore.login(username.trim(), password, true);
            
            const destination = page.url.searchParams.get('goto') ?? '/dashboard';
            goto(destination);
        } catch (e) {
            error = m.login_register_error();
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

        <!-- Email -->
        <div class="flex flex-col gap-2">
            <label for="email" class="text-sm font-medium text-slate-300">
                {m.login_email_input()}
            </label>
            <input
                id="email"
                type="email"
                bind:value={email}
                placeholder={m.login_email_input().toLowerCase()}
                class="w-full px-4 py-3 bg-white/5 border {error && (!email || !emailRegex.test(email)) ? 'border-red-500/50' : 'border-white/10 focus:border-blue-500/50'} rounded-xl text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 transition-all"
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
                onkeydown={(e) => e.key === 'Enter' && handleRegister()}
                class="w-full px-4 py-3 bg-white/5 border {error && !password ? 'border-red-500/50' : 'border-white/10 focus:border-blue-500/50'} rounded-xl text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 transition-all"
            />
        </div>

        <!-- Confirm Password -->
        <div class="flex flex-col gap-2">
            <label for="confirmPassword" class="text-sm font-medium text-slate-300">
                {m.login_confirm_password_input()}
            </label>
            <input
                id="confirmPassword"
                type="password"
                bind:value={confirmPassword}
                placeholder="••••••••"
                onkeydown={(e) => e.key === 'Enter' && handleRegister()}
                class="w-full px-4 py-3 bg-white/5 border {error && password !== confirmPassword ? 'border-red-500/50' : 'border-white/10 focus:border-blue-500/50'} rounded-xl text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 transition-all"
            />
        </div>

        {#if error}
            <p class="text-red-400 text-sm animate-in fade-in slide-in-from-top-1">{error}</p>
        {/if}
    </div>

    <button
        onclick={handleRegister}
        disabled={loading}
        class="w-full py-3.5 mt-2 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/30 active:scale-[0.98] flex justify-center items-center h-13">
        {#if loading}
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        {:else}
            {m.login_register_button()}
        {/if}
    </button>

    <button 
        onclick={onToggleMode}
        class="text-sm text-slate-400 hover:text-white transition-colors">
        {m.login_has_account()}
    </button>
</div>
