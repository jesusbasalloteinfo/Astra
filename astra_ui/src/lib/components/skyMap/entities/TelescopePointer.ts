// src/lib/components/skyMap/entities/TelescopePointer.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';

/**
 * TelescopePointer Entity
 * 
 * Manages the rendering and animation of a visual pointer that indicates the telescope's current pointing position in the sky.
 */
export class TelescopePointer {
    /** The Three.js sprite used for visual representation. */
    public sprite: THREE.Sprite;

    /** The target position to interpolate towards. */
    private targetPos: THREE.Vector3 | null = null;
    /** Flag to handle initial positioning without interpolation. */
    private isFirstPosition: boolean = true;

    /**
     * Creates an instance of TelescopePointer.
     */
    constructor() {
        const mat = new THREE.SpriteMaterial({ 
            transparent: true, 
            depthWrite: false, 
            depthTest: false,
            color: 0xff0000 //10b981
        });
        
        this.sprite = new THREE.Sprite(mat);
        this.sprite.visible = false;
        
        this.sprite.material.map = this.createTexture();
        this.sprite.scale.set(18, 18, 1);
    }

    /**
     * Creates the SVG-based texture for the telescope pointer.
     * @returns {THREE.Texture} The generated texture.
     * @private
     */
    private createTexture(): THREE.Texture {
        const svg = `
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="40" fill="none" stroke="white" stroke-width="4" 
                        stroke-dasharray="40 22.75" 
                        transform="rotate(-72 50 50)" />

                <line x1="50" y1="5" x2="50" y2="20" stroke="white" stroke-width="4" />
                <line x1="50" y1="80" x2="50" y2="95" stroke="white" stroke-width="4" />
                <line x1="5" y1="50" x2="20" y2="50" stroke="white" stroke-width="4" />
                <line x1="80" y1="50" x2="95" y2="50" stroke="white" stroke-width="4" />
            </svg>
        `;
        const encoded = encodeURIComponent(svg);
        return new THREE.TextureLoader().load(`data:image/svg+xml;utf8,${encoded}`);
    }

    /**
     * Updates the target telescope position in the sky.
     * Converts altitude and azimuth to Cartesian coordinates.
     * @param {number} alt - Telescope altitude in degrees.
     * @param {number} az - Telescope azimuth in degrees.
     */
    updatePosition(alt: number, az: number) {
        const altRad = alt * (Math.PI / 180);
        const azRad  = (180 - az) * (Math.PI / 180);
        
        const newPos = new THREE.Vector3(
            DOME_RADIUS * Math.cos(altRad) * Math.sin(azRad),
            DOME_RADIUS * Math.sin(altRad),
            DOME_RADIUS * Math.cos(altRad) * Math.cos(azRad)
        );

        this.targetPos = newPos;
        this.sprite.visible = true;
    
        if (this.isFirstPosition) {
            this.sprite.position.copy(this.targetPos);
            this.isFirstPosition = false;
        }
    }

    /**
     * Updates the pointer's animation (rotation/pulsing) and interpolates its position.
     * Should be called in the main render loop.
     */
    update(){
        this.sprite.material.rotation += 0.008;
        const time = performance.now() * 0.003;
        this.sprite.material.opacity = 0.8 + Math.sin(time) * 0.2;

        // position interpolation
        if (this.sprite.visible && this.targetPos) {
            this.sprite.position.lerp(this.targetPos, 0.01);

            // Always in the dome
            this.sprite.position.normalize().multiplyScalar(DOME_RADIUS);
        }
    }

    /**
     * Hides the telescope pointer and resets its state.
     */
    hide() {
        this.sprite.visible = false;
        this.isFirstPosition = true; 
        this.targetPos = null;
    }

    /**
     * Cleans up Three.js resources used by the pointer.
     */
    dispose() {
        if (this.sprite.material.map) this.sprite.material.map.dispose();
        this.sprite.material.dispose();
    }
}