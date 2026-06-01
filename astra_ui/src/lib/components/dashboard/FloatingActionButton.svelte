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

<!-- src/lib/components/dashboard/FloatingActionButton.svelte -->
<script lang="ts">
    import { Plus } from 'lucide-svelte';
    import { newObsStore } from '$lib/stores/newObservation.svelte';
    import { scale } from 'svelte/transition';
</script>

<div class="lg:hidden fixed bottom-20 landscape:bottom-16 right-4 z-30">
    <button 
        onclick={() => newObsStore.open()}
        in:scale={{ duration: 300, delay: 200, start: 0.5 }}
        class="w-14 h-14 landscape:w-12 landscape:h-12 bg-accent text-white rounded-full flex items-center justify-center shadow-lg shadow-accent/40 active:scale-90 active:bg-accent-hover transition-all"
        aria-label="New Session"
    >
        <Plus class="w-6 h-6" />
    </button>
</div>