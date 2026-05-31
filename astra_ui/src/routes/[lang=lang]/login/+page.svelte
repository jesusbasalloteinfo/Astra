<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import AuthLayout from '$lib/components/auth/AuthLayout.svelte';
    import LoginForm from '$lib/components/auth/LoginForm.svelte';
    import RegisterForm from '$lib/components/auth/RegisterForm.svelte';

    let isRegister = $state(false);

    function toggleMode() {
        isRegister = !isRegister;
    }
</script>

<svelte:head>
    <title>{isRegister ? m.register_title({name: m.name().toUpperCase()}) : m.login_title({name: m.name().toUpperCase()})}</title>
    <meta name="description" content={isRegister ? m.register_title({name: m.name().toUpperCase()}) : m.login_title({name: m.name().toUpperCase()})} />
</svelte:head>

<AuthLayout 
    title={isRegister ? m.login_register_title() : m.login_welcome()} 
    subtitle={isRegister ? '' : m.login_input_msg()}
    backLink="/"
    backText={m.login_return_home()}
>
    {#if isRegister}
        <RegisterForm onToggleMode={toggleMode} />
    {:else}
        <LoginForm onToggleMode={toggleMode} />
    {/if}
</AuthLayout>
