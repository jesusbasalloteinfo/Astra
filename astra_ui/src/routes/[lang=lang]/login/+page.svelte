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
