// src/lib/stores/activeSelection.svelte.ts

class ActiveSelection {
    targetId: string | null = $state(null);

    clear() {
        this.targetId = null;
    }
}

export const selectionStore = new ActiveSelection();