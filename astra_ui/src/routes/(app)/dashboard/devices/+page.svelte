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
    import { Cpu } from 'lucide-svelte';
    import { deviceStore } from '$lib/stores/devices.svelte';
    import * as m from '$lib/paraglide/messages.js'; // Asumiendo que tienes mensajes para devices
    import DeviceSettings from '$lib/components/devices/DeviceSettings.svelte';
    import { onMount } from 'svelte';

    onMount(() => {
        if (deviceStore.all.length === 0) {
            deviceStore.fetchAll();
        }
    });
</script>

<div class="max-w-3xl mx-auto p-6">
    <div class="flex items-center justify-between mb-10">
        <div class="flex items-center gap-4">
            <div class="hidden sm:flex w-12 h-12 rounded-2xl bg-accent/10 items-center justify-center text-accent">
                <Cpu size={24} />
            </div>
            <div>
                <h1 class="text-2xl font-bold text-copy-primary">
                    {m.dash_device_list_title()}
                </h1>
                <p class="text-sm text-copy-muted mt-1">
                    {m.dash_location_found({count: deviceStore.all.length})}
                </p>
            </div>
        </div>
    </div>

    <DeviceSettings />
</div>