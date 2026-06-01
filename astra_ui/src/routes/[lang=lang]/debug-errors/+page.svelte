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
    import { page } from '$app/state';
    
    let lang = $derived(page.params.lang ?? 'es');

    function triggerClientError() {
        throw new Error("Error disparado desde el cliente (navegador).");
    }
</script>

<div class="min-h-screen bg-slate-950 text-white p-12 flex flex-col items-center justify-center space-y-8">
    <h1 class="text-4xl font-bold border-b border-blue-500 pb-4">Depuración de Errores Astra</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Error 500 (Servidor) -->
        <a 
            href="?trigger=500" 
            class="bg-red-900/20 hover:bg-red-900/40 border border-red-500/50 p-6 rounded-xl transition-all text-center"
        >
            <h2 class="text-xl font-bold mb-2">Error 500</h2>
            <p class="text-sm text-slate-400 mb-4">Fallo en el servidor (+page.server.ts)</p>
            <span class="bg-red-500 px-3 py-1 rounded text-xs">Disparar</span>
        </a>

        <!-- Error 418 (Teapot) -->
        <a 
            href="?trigger=418" 
            class="bg-amber-900/20 hover:bg-amber-900/40 border border-amber-500/50 p-6 rounded-xl transition-all text-center"
        >
            <h2 class="text-xl font-bold mb-2">Error 418</h2>
            <p class="text-sm text-slate-400 mb-4">I'm a teapot (SvelteKit error helper)</p>
            <span class="bg-amber-500 px-3 py-1 rounded text-xs text-black">Disparar</span>
        </a>

        <!-- Error Cliente -->
        <button 
            onclick={triggerClientError}
            class="bg-blue-900/20 hover:bg-blue-900/40 border border-blue-500/50 p-6 rounded-xl transition-all text-center cursor-pointer"
        >
            <h2 class="text-xl font-bold mb-2">Error Cliente</h2>
            <p class="text-sm text-slate-400 mb-4">Error de JS en el navegador</p>
            <span class="bg-blue-500 px-3 py-1 rounded text-xs">Disparar</span>
        </button>
    </div>

    <a href="/{lang}" class="text-slate-500 hover:text-white transition-colors underline">Volver al inicio</a>
</div>
