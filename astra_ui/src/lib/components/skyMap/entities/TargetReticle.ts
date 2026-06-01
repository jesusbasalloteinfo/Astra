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

// src/lib/components/skyMap/entities/TargetReticle.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { createCrosshairTexture } from '../utils/crosshair';
import { selectionStore } from '$lib/stores/activeSelection.svelte';
import type { PositionUpdates } from '$lib/stores/skyEngine.svelte';

/**
 * TargetReticle Entity
 * 
 * Manages the rendering and animation of a target reticle that follows the currently selected celestial object.
 */
export class TargetReticle {
    /** The Three.js sprite used for visual representation. */
    public sprite: THREE.Sprite;

    /**
     * Creates an instance of TargetReticle.
     */
    constructor() {
        const mat = new THREE.SpriteMaterial({ 
            transparent: true, 
            depthWrite: false, 
            depthTest: false 
        });
        
        this.sprite = new THREE.Sprite(mat);
        this.sprite.visible = false;
    }

    /**
     * Locks the reticle onto a new target.
     * Generates a new texture based on the object type and scales it appropriately.
     * @param {boolean} isPlanet - Whether the target is a planetary object.
     * @param {string} hexColor - Color hex string for the reticle.
     * @param {number} baseSize - Base size of the target object for scaling.
     */
    lockOn(isPlanet: boolean, hexColor: string, baseSize: number) {
        // Clean up old texture to prevent memory leaks
        if (this.sprite.material.map) {
            this.sprite.material.map.dispose();
        }

        if (isPlanet) {
            // Scale for planets with clipping
            this.sprite.material.map = createCrosshairTexture('focus', hexColor);
            const reticleSize = Math.max(25, Math.min(50, baseSize * 0.8 + 12));
            this.sprite.scale.set(reticleSize, reticleSize, 1);
        } else {
            // Scale for sidereal objects
            this.sprite.material.map = createCrosshairTexture('sidereal', hexColor);
            const reticleSize = Math.max(15, baseSize * 3 + 8); 
            this.sprite.scale.set(reticleSize, reticleSize, 1);
        }
        
        this.sprite.visible = true;
    }

    /**
     * Hides the reticle (e.g., when the selection is cleared).
     */
    hide() {
        this.sprite.visible = false;
    }

    /**
     * Updates the 3D position based on the selected object's coordinates.
     * Handles rotation and pulsing (opacity) animations.
     * Should be called in the main render loop.
     * @param {PositionUpdates} updates - Current celestial positions.
     */
    update(updates: PositionUpdates) {
        if (!this.sprite.visible || !selectionStore.targetId) return;

        const pos = updates.get(selectionStore.targetId);
        
        if (pos) {
            const altRad = pos.alt * (Math.PI / 180);
            const azRad  = (180 - pos.az) * (Math.PI / 180);
            
            this.sprite.position.set(
                DOME_RADIUS * Math.cos(altRad) * Math.sin(azRad),
                DOME_RADIUS * Math.sin(altRad),
                DOME_RADIUS * Math.cos(altRad) * Math.cos(azRad)
            );
        }
        // Animations
        this.sprite.material.rotation += 0.006;
        const time = performance.now() * 0.003;
        this.sprite.material.opacity = 0.8 + Math.sin(time) * 0.2;
    }

    /**
     * Cleans up Three.js resources used by the reticle.
     */
    dispose() {
        if (this.sprite.material.map) {
            this.sprite.material.map.dispose();
        }
        this.sprite.material.dispose();
    }
}