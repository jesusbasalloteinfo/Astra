<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import * as m from '$lib/paraglide/messages.js';

    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import { authAPI } from '$lib/api/auth';

    let username = $state('');
    let loading = $state(false);
    let error = $state('');
    // Where to go after login
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

<div class="min-h-screen bg-astralanding-dark text-slate-200 flex items-center justify-center relative">

    <Stars />

    <!-- Luminance background -->
    <div class="absolute w-[800px] h-[400px] bg-blue-600/10 rounded-full blur-[200px] pointer-events-none"></div>

    <div class="relative z-10 w-full max-w-md px-6">

        <!-- Logo -->
        <a href="/" class="flex items-center justify-center gap-3 mb-10 opacity-80 hover:opacity-100 transition-opacity">
            <AppLogo class="w-10 h-10" />
            <div>
                <h1 class="text-xl font-bold text-white">{m.name().toUpperCase()}</h1>
                <p class="text-[10px] tracking-widest text-blue-300 font-medium">{m.name_sign().toUpperCase()}</p>
            </div>
        </a>

        <!-- Card -->
        <div class="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-md">

            <h2 class="text-2xl font-bold text-white mb-2">{m.login_welcome()}</h2>
            <p class="text-slate-400 text-sm mb-8">{m.login_input_msg()}</p>

            <div class="flex flex-col gap-4">

                <!-- Username field -->
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
                        class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500
                               focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                    />
                </div>

                <!-- Error -->
                {#if error}
                    <p class="text-red-400 text-sm">{error}</p>
                {/if}

                <!-- Submit -->
                <button
                    onclick={handleLogin}
                    disabled={loading}
                    class="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
                           text-white font-bold rounded-xl transition-all hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]">
                    {#if loading}
                        {m.login_sign_in_process()}
                    {:else}
                        {m.login_input_button()}
                    {/if}
                </button>
            </div>
        </div>

        <!-- Back link -->
        <p class="text-center text-slate-500 text-sm mt-6">
            <a href="/" class="hover:text-blue-300 transition-colors">{m.login_return_home()}</a>
        </p>
    </div>
</div>