/*
 * ASTRA - Automated Smart Telescope Remote Assistant
 * Copyright (C) 2026 Jesus Basallote
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

// src/lib/stores/devices.svelte.ts
import { browser } from '$app/environment';
import { deviceAPI } from '$lib/api/devices';
import type { Device, DeviceInfo } from '$lib/types/devices';

/**
 * Store for managing astronomical devices (telescopes, cameras, focusers).
 * Handles device list, active device details, component selection, and auto-refresh.
 */
class DeviceStore {
    /** ID of the currently active device. */
    activeId = $state<string | null>(browser ? localStorage.getItem('active_device_id') : null);

    /** List of all discovered devices. */
    all = $state<Device[]>(
        browser ? JSON.parse(localStorage.getItem('device_list_cache') || '[]') : []
    );
    /** Detailed information about the active device. */
    activeDetails = $state<DeviceInfo | null>(null);

    /** Indicates if the store is loading the device list. */
    isLoading = $state(false);
    /** Indicates if the store is fetching details for the active device. */
    isFetchingDetails = $state(false);

    /** Map of selected components for each device. */
    selectedComponents = $state<Record<string, { telescope?: string, camera?: string, focuser?: string }>>(
        browser ? JSON.parse(localStorage.getItem('device_selected_components') || '{}') : {}
    );

    /** Polling interval reference for auto-refresh. */
    #refreshInterval: ReturnType<typeof setInterval> | null = null;

    /** Computed property that returns the active device object. */
    activeBase = $derived.by(() => {
        if (this.all.length === 0) return null;
        
        const manual = this.all.find(d => d.device_id === this.activeId);
        if (manual) return manual;
        
        return this.all[0];
    });

    /** Returns the device_id of the effective active device. */
    get effectiveActiveId() {
        return this.activeBase?.device_id || null;
    }

    /** Computed property that returns the selected components for the active device. */
    activeComponents = $derived.by(() => {
        if (!this.effectiveActiveId) return {};
        return this.selectedComponents[this.effectiveActiveId] || {};
    });

    /**
     * Fetches all devices from the API.
     * 
     * @param silent - If true, prevents setting the global isLoading state.
     * @returns A promise that resolves when the fetch is complete.
     */
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

    /**
     * Selects a device as the active one.
     * 
     * @param id - The ID of the device to select, or null to deselect.
     */
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
    
    /**
     * Sets a specific component (telescope, camera, focuser) for a device.
     * 
     * @param deviceId - The ID of the device.
     * @param type - The type of component.
     * @param value - The name of the component, or undefined to clear.
     */
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

    /**
     * Fetches detailed information for a specific device.
     * 
     * @param id - The ID of the device.
     * @param silent - If true, prevents setting the fetching state.
     * @returns A promise that resolves when the fetch is complete.
     */
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

    /**
     * Updates device information.
     * 
     * @param id - The ID of the device to update.
     * @param data - The new data for the device.
     * @returns A promise that resolves when the update is complete.
     */
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

    /**
     * Deletes a device.
     * 
     * @param id - The ID of the device to delete.
     * @returns A promise that resolves when the deletion is complete.
     */
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

    /**
     * Refreshes the device list silently.
     */
    async refreshAll() {
        await this.fetchAll(true);
    }

    /**
     * Refreshes the details of the active device silently.
     */
    async refreshActiveDetails() {
        if (this.effectiveActiveId) {
            await this.fetchDetails(this.effectiveActiveId, true);
        }
    }

    /**
     * Starts the auto-refresh cycle for the device list.
     * 
     * @param intervalMs - The interval in milliseconds.
     */
    startAutoRefresh(intervalMs = 10000) {
        if (this.#refreshInterval) return; 
        
        this.#refreshInterval = setInterval(() => {
            this.refreshAll();
        }, intervalMs);
    }

    /**
     * Stops the auto-refresh cycle.
     */
    stopAutoRefresh() {
        if (this.#refreshInterval) {
            clearInterval(this.#refreshInterval);
            this.#refreshInterval = null;
        }
    }


    /**
     * Clears all device data and resets the store.
     */
    clear() {
        this.stopAutoRefresh();
        this.all = [];
        this.activeId = null;
        this.activeDetails = null;
        this.selectedComponents = {};
        if (browser) {
            localStorage.removeItem('active_device_id');
            localStorage.removeItem('device_list_cache');
            localStorage.removeItem('device_selected_components');
        }
    }
}

/**
 * Singleton instance of DeviceStore.
 */
export const deviceStore = new DeviceStore();