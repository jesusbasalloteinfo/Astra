// src/lib/stores/devices.svelte.ts
import { browser } from '$app/environment';
import { deviceAPI } from '$lib/api/devices';
import type { Device, DeviceInfo } from '$lib/types/devices';

class DeviceStore {
    activeId = $state<string | null>(browser ? localStorage.getItem('active_device_id') : null);

    all = $state<Device[]>(
        browser ? JSON.parse(localStorage.getItem('device_list_cache') || '[]') : []
    );
    activeDetails = $state<DeviceInfo | null>(null);

    isLoading = $state(false);
    isFetchingDetails = $state(false);

    selectedComponents = $state<Record<string, { telescope?: string, camera?: string, focuser?: string }>>(
        browser ? JSON.parse(localStorage.getItem('device_selected_components') || '{}') : {}
    );

    // Polling interval
    #refreshInterval: ReturnType<typeof setInterval> | null = null;

    // Active first
    activeBase = $derived.by(() => {
        if (this.all.length === 0) return null;
        
        const manual = this.all.find(d => d.device_id === this.activeId);
        if (manual) return manual;
        
        return this.all[0];
    });

    get effectiveActiveId() {
        return this.activeBase?.device_id || null;
    }

    activeComponents = $derived.by(() => {
        if (!this.effectiveActiveId) return {};
        return this.selectedComponents[this.effectiveActiveId] || {};
    });

    async fetchAll(silent = false) {
        if (!silent) this.isLoading = true;
        
        try {
            this.all = await deviceAPI.getDevices();

            if (browser) {
                localStorage.setItem('device_list_cache', JSON.stringify(this.all));
            }
            
            if (this.all.length > 0 && !this.activeId) {
                this.select(this.all[0].device_id);
            } else if (this.effectiveActiveId) {
                // Also refresh active details
                await this.fetchDetails(this.effectiveActiveId, silent);
            }
        } catch (e) {
            console.error("Error fetching devices", e);
        } finally {
            if (!silent) this.isLoading = false;
        }
    }

    select(id: string | null) {
        if (id === this.activeId && id !== null) {
            this.fetchDetails(id, true);
            return;
        }

        this.activeId = id;
        if (browser) {
            if (id) localStorage.setItem('active_device_id', id);
            else localStorage.removeItem('active_device_id');
        }

        if (id) {
            this.fetchDetails(id, false);
        } else {
            this.activeDetails = null;
        }
    }
    
    setComponent(deviceId: string, type: 'telescope' | 'camera' | 'focuser', value: string | undefined) {
        if (!this.selectedComponents[deviceId]) {
            this.selectedComponents[deviceId] = {};
        }
        
        if (value === undefined) {
            delete this.selectedComponents[deviceId][type];
        } else {
            this.selectedComponents[deviceId][type] = value;
        }
        
        if (browser) {
            localStorage.setItem('device_selected_components', JSON.stringify(this.selectedComponents));
        }
    }

    async fetchDetails(id: string, silent = false) {
        if (!silent) this.isFetchingDetails = true;
        
        try {
            this.activeDetails = await deviceAPI.getDeviceInfo(id);
            
            // Dynamic component sync
            if (this.activeDetails?.components) {
                const comps = this.activeDetails.components;
                const saved = this.selectedComponents[id] || {};
                
                // --- Telescopes ---
                if (comps.telescope?.length) {
                    if (!saved.telescope || !comps.telescope.includes(saved.telescope)) {
                        this.setComponent(id, 'telescope', comps.telescope[0]);
                    }
                } else if (saved.telescope) {
                    this.setComponent(id, 'telescope', undefined);
                }

                // --- Cameras (not yet) ---
                if (comps.camera?.length) {
                    if (!saved.camera || !comps.camera.includes(saved.camera)) {
                        this.setComponent(id, 'camera', comps.camera[0]);
                    }
                } else if (saved.camera) {
                    this.setComponent(id, 'camera', undefined);
                }

                // --- Focusers (not yet) ---
                if (comps.focuser?.length) {
                    if (!saved.focuser || !comps.focuser.includes(saved.focuser)) {
                        this.setComponent(id, 'focuser', comps.focuser[0]);
                    }
                } else if (saved.focuser) {
                    this.setComponent(id, 'focuser', undefined);
                }
            }
        } catch (e) {
            console.error("Error fetching device details", e);
            if (!silent) this.activeDetails = null;
        } finally {
            if (!silent) this.isFetchingDetails = false;
        }
    }

    async update(id: string, data: { name: string }) {
        this.isLoading = true;
        try {
            await deviceAPI.updateDevice(id, data);
            const index = this.all.findIndex(d => d.device_id === id);
            if (index !== -1) {
                this.all[index] = { ...this.all[index], ...data };
            }
            if (this.activeDetails && this.activeDetails.device_id === id) {
                this.activeDetails = { ...this.activeDetails, ...data };
            }
        } catch (e) {
            console.error("Error updating device", e);
        } finally {
            this.isLoading = false;
        }
    }

    async deleteDevice(id: string) {
        this.isLoading = true;
        try {
            await deviceAPI.deleteDevice(id);
            this.all = this.all.filter(d => d.device_id !== id);
            if (this.activeId === id) {
                this.select(this.all.length > 0 ? this.all[0].device_id : null);
            }
        } catch (e) {
            console.error("Error deleting device", e);
        } finally {
            this.isLoading = false;
        }
    }

    async refreshAll() {
        await this.fetchAll(true);
    }

    async refreshActiveDetails() {
        if (this.effectiveActiveId) {
            await this.fetchDetails(this.effectiveActiveId, true);
        }
    }

    // Global reloading
    startAutoRefresh(intervalMs = 10000) {
        if (this.#refreshInterval) return; 
        
        this.#refreshInterval = setInterval(() => {
            this.refreshAll();
        }, intervalMs);
    }

    stopAutoRefresh() {
        if (this.#refreshInterval) {
            clearInterval(this.#refreshInterval);
            this.#refreshInterval = null;
        }
    }
}

export const deviceStore = new DeviceStore();