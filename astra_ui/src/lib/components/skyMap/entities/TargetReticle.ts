// src/lib/components/skyMap/entities/TargetReticle.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { createCrosshairTexture } from '../utils/crosshair';
import { selectionStore } from '$lib/stores/activeSelection.svelte';
import type { PositionUpdates } from '$lib/stores/skyEngine.svelte';

/**
 * TargetReticle Entity
 * 
 * Manages the rendering of a target reticle across a selected object.
 */
export class TargetReticle {
    public sprite: THREE.Sprite;

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
     * Locks the reticle onto a new target, generating the appropriate SVG and scale.
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
     * Hides the reticle (e.g., when clicking on empty space).
     */
    hide() {
        this.sprite.visible = false;
    }

    /**
     * Updates the 3D position and handles rotation/pulsing animations.
     * Should be called in the main render loop.
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
     * Disposes of materials and textures.
     */
    dispose() {
        if (this.sprite.material.map) {
            this.sprite.material.map.dispose();
        }
        this.sprite.material.dispose();
    }
}