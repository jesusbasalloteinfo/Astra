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

// src/lib/components/skyMap/core/SelectionController.ts

import * as THREE from 'three';
import { CameraController } from './CameraController';
import { Planetary } from '../entities/Planetary';
import { Sidereal } from '../entities/Sidereal';
import { TargetReticle } from '../entities/TargetReticle';
import { skyEngine } from '$lib/stores/skyEngine.svelte';
import { selectionStore } from '$lib/stores/activeSelection.svelte'; 
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

/**
 * SelectionController
 * 
 * Manages user interactions for selecting celestial objects in the 3D scene.
 * Uses raycasting to detect clicks on planetary and sidereal objects.
 */
export class SelectionController {
    /** The Three.js raycaster used for object picking. */
    private raycaster: THREE.Raycaster = new THREE.Raycaster();
    /** Current pointer position in normalized device coordinates. */
    private pointer: THREE.Vector2 = new THREE.Vector2();
    /** Pointer position when the mouse/touch was first pressed. */
    private pointerDownPos = { x: 0, y: 0 }; // Distinguish click from drag
    /** Whether the user is currently dragging the view. */
    private isDragging: boolean = false;
    /** The ID of the currently selected celestial object. */
    public selectedId: string | null = null;

    /**
     * Creates an instance of SelectionController.
     * @param {HTMLDivElement} container - The container element for event listeners.
     * @param {CameraController} cameraCtrl - The camera controller for raycasting.
     * @param {Planetary} planetary - The planetary entities manager.
     * @param {Sidereal} sidereal - The sidereal entities manager.
     * @param {TargetReticle} targetReticle - The reticle to show on selection.
     */
    constructor(
        private container: HTMLDivElement,
        private cameraCtrl: CameraController,
        private planetary: Planetary,
        private sidereal: Sidereal,
        private targetReticle: TargetReticle
    ) {
        // Ray hitbox
        this.raycaster.params.Points.threshold = 10;

        // Listeners
        this.container.addEventListener('pointerdown', this.onPointerDown);
        this.container.addEventListener('pointermove', this.onPointerMove);
        this.container.addEventListener('pointerup', this.onPointerUp);
    }

    /**
     * Performs a double raycast to find an object under the pointer.
     * Checks first planetary objects (priority), then sidereal.
     * @returns {{ id: string, isPlanet: boolean } | null} The hit object information or null.
     * @private
     */
    private getHit(): { id: string, isPlanet: boolean } | null {
        // 1. Raycast 3D Planet Meshes (when zoomed in)
        const meshes3D = this.planetary.get3DMeshes();
        if (meshes3D.length > 0) {
            const intersects3D = this.raycaster.intersectObjects(meshes3D, true);
            if (intersects3D.length > 0) {
                let obj: THREE.Object3D | null = intersects3D[0].object;
                while (obj && !obj.userData?.planetId) {
                    obj = obj.parent;
                }
                if (obj && obj.userData?.planetId) {
                    return { id: obj.userData.planetId, isPlanet: true };
                }
            }
        }

        // 2. Raycast Planetary Points Mesh
        this.raycaster.params.Points.threshold = 10; // Big hitbox
        let intersects = this.raycaster.intersectObject(this.planetary.getPointsMesh(), false);
        
        if (intersects.length > 0 && intersects[0].index !== undefined) {
            const id = this.planetary.getIdByIndex(intersects[0].index);
            if (id) return { id, isPlanet: true };
        }

        // 3. Raycast Sidereal Points Mesh
        this.raycaster.params.Points.threshold = 5; // Smaller hitbox
        intersects = this.raycaster.intersectObject(this.sidereal.getPointsMesh(), false);
        
        if (intersects.length > 0 && intersects[0].index !== undefined) {
            const id = this.sidereal.getIdByIndex(intersects[0].index);
            if (id) return { id, isPlanet: false };
        }

        return null;
    }

    /**
     * Shoots a ray from the camera at the given viewport coordinates.
     * If an object is hit, it is selected.
     * @param {number} posX - X coordinate in normalized device space (-1 to +1).
     * @param {number} posY - Y coordinate in normalized device space (-1 to +1).
     * @private
     */
    private raycast(posX:number, posY:number){
        this.pointer.x = posX;
        this.pointer.y = posY;

        this.raycaster.setFromCamera(this.pointer, this.cameraCtrl.camera);

        // Shoot ray to planetary and sidereal objects
        const result = this.getHit();

        if (result) {
            this.selectById(result.id);
        } else {
            // Void click -> clear selection
            this.selectedId = null;
            this.targetReticle.hide();
            selectionStore.clear();
        }
    }

    /**
     * Selects a celestial object by its ID.
     * Updates the UI stores, positions the reticle, and initiates a camera "fly-to".
     * @param {string} id - The unique ID of the object to select.
     */
    public selectById(id: string) {
        if (id === this.selectedId) return;

        const pos = skyEngine.positions.get(id);
        const info = catalogStore.getInfo(id);

        if (!pos || !info) {
            this.selectedId = null;
            this.targetReticle.hide();
            selectionStore.clear();
            return;
        }

        if (id === this.selectedId) {
            this.cameraCtrl.isTracking = true;
            this.cameraCtrl.flyTo(pos.alt, pos.az);
            return; 
        }

        this.selectedId = id;
        const isPlanet = id in catalogStore.planetaryData;
        selectionStore.select(id, isPlanet ? 'planetary' : 'sidereal');

        let hexColor = '#ed1556'//isPlanet ? '#f59e0b' : '#38bdf8'; 
        let baseSize = isPlanet ? 4 : Math.max(1, 5 - (info.mag ?? 0));

        const entity = isPlanet ? this.planetary : this.sidereal;
        
        // Get vertex index
        const index = entity.getIndexById ? entity.getIndexById(id) : undefined;

        if (index !== undefined) {
            const geometry = (entity.getPointsMesh() as THREE.Points).geometry;
            
            // Size
            baseSize = geometry.attributes.size.getX(index);
            
            // Colour
            const r = geometry.attributes.color.getX(index);
            const g = geometry.attributes.color.getY(index);
            const b = geometry.attributes.color.getZ(index);
            hexColor = '#' + new THREE.Color(r, g, b).getHexString();
        }

        this.targetReticle.lockOn(isPlanet, hexColor, baseSize);
        this.cameraCtrl.isTracking = true;
        this.cameraCtrl.flyTo(pos.alt, pos.az);
    }

    /**
     * Handles the pointer down event to distinguish between clicks and drags.
     * @param {PointerEvent} event - The pointer event.
     * @private
     */
    private onPointerDown = (event: PointerEvent) => {
        this.pointerDownPos = { x: event.clientX, y: event.clientY };
        this.isDragging = true;
        this.container.style.cursor = 'grabbing'; 
    };

    /** 
     * Handles the pointer move event.
     * Updates the cursor style if an object is hoverable.
     * @param {PointerEvent} event - The pointer event.
     * @private
     */
    private onPointerMove = (event: PointerEvent) => {
        if (this.isDragging) return;

        const rect = this.container.getBoundingClientRect();
        this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.pointer, this.cameraCtrl.camera);

        const result = this.getHit();

        // Activate cursor detection
        this.container.style.cursor = result ? 'pointer' : 'default';
    };

    /** 
     * Handles the pointer up event.
     * Triggers selection if the interaction was a click (not a drag).
     * @param {PointerEvent} event - The pointer event.
     * @private
     */
    private onPointerUp = (event: PointerEvent) => {
        this.isDragging = false;

        // Update for the pointer
        this.onPointerMove(event);

        const deltaX = Math.abs(event.clientX - this.pointerDownPos.x);
        const deltaY = Math.abs(event.clientY - this.pointerDownPos.y);
        
        // Dragging detected, so cancel
        if (deltaX > 5 || deltaY > 5) return;

        const rect = this.container.getBoundingClientRect();
        const posX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        const posY = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycast(posX, posY)
    };

    /**
     * Clears the current selection and hides the reticle.
     */
    public clearSelection() {
        if (this.selectedId) {
            this.selectedId = null;
            this.targetReticle.hide();
            selectionStore.clear();
            this.cameraCtrl.isTracking = false; 
        }
    }
    
    /**
     * Cleans up event listeners when the controller is disposed.
     */
    dispose() {
        this.container.removeEventListener('pointerdown', this.onPointerDown);
        this.container.removeEventListener('pointermove', this.onPointerMove);
        this.container.removeEventListener('pointerup', this.onPointerUp);
    }
}