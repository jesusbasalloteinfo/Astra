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

// src/lib/components/skyMap/entities/Environment.ts

import * as THREE from 'three';
import { DOME_RADIUS, GROUND_RADIUS, EYE_LEVEL, CARDINAL_LABELS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';

// --- Atmosphere Shaders ---
/** Vertex shader for the atmospheric Rayleigh scattering effect. */
const skyVertexShader = `
    varying vec3 vWorldPosition;
    void main() {
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        gl_Position = projectionMatrix * viewMatrix * worldPosition;
    }
`;

/** Fragment shader for the atmospheric Rayleigh scattering effect. */
const skyFragmentShader = `
    varying vec3 vWorldPosition;
    uniform vec3 sunPosition;

    void main() {
        vec3 viewDir = normalize(vWorldPosition);
        vec3 sunDir = sunPosition;

        float viewAlt = max(0.0, viewDir.y);
        float sunAlt = sunDir.y;
        float cosTheta = dot(viewDir, sunDir);

        // --- Base Colors ---
        vec3 dayZenith = vec3(0.12, 0.28, 0.70);
        vec3 dayHorizon = vec3(0.45, 0.65, 0.85);
        
        // Night with slight atmosphere brightness
        // vec3 nightZenith = vec3(0.000, 0.001, 0.003);
        // vec3 nightHorizon = vec3(0.002, 0.005, 0.015);

        // Total dark night
        vec3 nightZenith = vec3(0.0);
        vec3 nightHorizon = vec3(0.0005, 0.001, 0.002);

        // Day/Night transition
        float dayFactor = smoothstep(-0.25, 0.1, sunAlt);
        
        vec3 zenithColor = mix(nightZenith, dayZenith, dayFactor);
        vec3 horizonColor = mix(nightHorizon, dayHorizon, dayFactor);

        // 2. Sky Simulation
        // Pure, smooth gradient
        vec3 skyColor = mix(horizonColor, zenithColor, pow(viewAlt, 0.4));

        // 3. Sunset/sunrise
        float sunsetIn = smoothstep(0.25, 0.0, sunAlt); 
        float sunsetOut = smoothstep(-0.15, 0.0, sunAlt); 
        float sunsetTime = sunsetIn * sunsetOut;

        float sunProximity = max(0.0, cosTheta);
        float radialGlow = pow(sunProximity, 4.0); 

        vec3 goldenColor = vec3(1.0, 0.6, 0.2);
        vec3 deepOrange = vec3(1.0, 0.25, 0.05);
        vec3 sunsetColor = mix(goldenColor, deepOrange, sunsetIn);

        skyColor = mix(skyColor, sunsetColor, radialGlow * sunsetTime * 0.85);

        // 4. Tone Mapping
        skyColor = vec3(1.0) - exp(-skyColor * 2.5);

        // Dark sky
        skyColor = max(vec3(0.0), skyColor - 0.005);

        gl_FragColor = vec4(skyColor, 1.0);
    }
`;

/**
 * Environment Entity
 * 
 * Responsible for rendering non-celestial static elements, such as the 
 * ground sphere, atmospheric Rayleigh simulation, and cardinal direction markers on the horizon.
 */
export class Environment {
    /** Container for all environment-related meshes and sprites. */
    public group = new THREE.Group();
    /** The mesh representing the ground. */
    private groundMesh: THREE.Mesh;
    /** The mesh representing the sky dome for atmospheric effects. */
    private skyMesh: THREE.Mesh;
    /** Shader material for the atmosphere. */
    private skyMaterial: THREE.ShaderMaterial; 
    /** Base color of the ground before daylight adjustments. */
    private baseGroundColor: number;
    /** Factor used to track daylight changes for optimization. */
    private lastDayFactor: number = -1;
    /** Array of sprites for cardinal direction labels. */
    private cardinalSprites: { sprite: THREE.Sprite, az: number, textKey: string }[] = [];

    /**
     * Creates an instance of Environment.
     * @param {number} groundColor - Initial ground color hex value.
     * @param {string} cardinalColor - CSS color string for cardinal direction text.
     * @param {Record<string, string>} [initialLabels] - Map of direction keys to localized labels.
     */
    constructor(groundColor: number, cardinalColor: string, initialLabels?: Record<string, string>) {
        this.baseGroundColor = groundColor;
        // Create the Ground
        const geo = new THREE.SphereGeometry(GROUND_RADIUS, 128, 128);
        const mat = new THREE.MeshBasicMaterial({
            color: groundColor, 
            side: THREE.FrontSide, 
            depthWrite: true, 
            depthTest: true });
        this.groundMesh = new THREE.Mesh(geo, mat);

        // Position is exactly below the camera eye level by its radius amount
        this.groundMesh.position.set(0, -GROUND_RADIUS - EYE_LEVEL, 0);
        this.groundMesh.renderOrder = 10;
        this.group.add(this.groundMesh);

        this.setGroundMode(false);

        const skyGeo = new THREE.SphereGeometry(DOME_RADIUS, 32, 32);
        this.skyMaterial = new THREE.ShaderMaterial({
            uniforms: {
                sunPosition: { value: new THREE.Vector3(0, -1, 0).normalize() } // Night by default
            },
            vertexShader: skyVertexShader,
            fragmentShader: skyFragmentShader,
            side: THREE.BackSide,
            depthWrite: false
        });
        this.skyMesh = new THREE.Mesh(skyGeo, this.skyMaterial);
        this.skyMesh.renderOrder = 0; 
        this.group.add(this.skyMesh);

        // Create Cardinal Labels
        CARDINAL_LABELS.forEach(({ text: key, az }) => {
            const labelText = initialLabels ? (initialLabels[key] || key) : key;
            const sprite = this.createCardinalSprite(labelText, cardinalColor)            
            const azRad = (180 - az) * (Math.PI / 180);
            sprite.position.set(
                (DOME_RADIUS - 20) * Math.sin(azRad),
                0,
                (DOME_RADIUS - 20) * Math.cos(azRad)
            );
            this.group.add(sprite);
            this.cardinalSprites.push({ sprite, az, textKey: key });
        });
    }

    /**
     * Switches between solid and translucent ground modes.
     * @param {boolean} isSolid - If true, ground is opaque; otherwise, it's translucent.
     */
    setGroundMode(isSolid: boolean) {
        const mat = this.groundMesh.material as THREE.MeshBasicMaterial;
        
        if (isSolid) {
            mat.opacity = 1.0;
            mat.transparent = false;
            mat.depthWrite = true; 
            this.groundMesh.renderOrder = 10; 
        } else {
            mat.opacity = 0.6; 
            mat.transparent = true;
            mat.depthWrite = false;
            this.groundMesh.renderOrder = 10; 
        }
        
        mat.needsUpdate = true;
    }

    /**
     * Updates the atmosphere shader with the sun's altitude and azimuth.
     * @param {number} alt - Sun altitude in degrees.
     * @param {number} az - Sun azimuth in degrees.
     */
    updateSunPosition(alt: number, az: number) {
        const pos = new Float32Array(3);
        altAzToXYZ(pos, 0, alt, az);
        this.skyMaterial.uniforms.sunPosition.value.set(pos[0], pos[1], pos[2]).normalize();
    }

    /**
     * Toggles the visibility of the atmospheric Rayleigh simulation.
     * @param {boolean} enabled - Whether to enable the atmosphere.
     */
    setAtmosphereEnabled(enabled: boolean) {
        this.skyMesh.visible = enabled;
    }

    /**
     * Returns whether the atmospheric Rayleigh simulation is currently visible.
     * @returns {boolean} True if the atmosphere is enabled.
     */
    isAtmosphereEnabled(): boolean {
        return this.skyMesh.visible;
    }
    
    /**
     * Updates the color and localized text of the cardinal direction labels.
     * @param {string} color - CSS color string for the text.
     * @param {Record<string, string>} [labels] - Map of direction keys to new localized labels.
     */
    updateCardinalLabels(color: string, labels?: Record<string, string>) {
        this.cardinalSprites.forEach(item => {
            const text = labels ? (labels[item.textKey] || item.textKey) : item.textKey;

            // Dispose old texture
            item.sprite.material.map?.dispose();

            // Create new texture using the same logic
            item.sprite.material.map = this.createCardinalTexture(text, color);
            item.sprite.material.needsUpdate = true;
        });
    }

    /**
     * Generates a 2D Canvas-based text sprite for a cardinal direction.
     * @param {string} text - The direction text (e.g., 'N', 'S').
     * @param {string} cardinalColor - CSS color string for the text.
     * @returns {THREE.Sprite} The generated sprite.
     */
    createCardinalSprite(text: string, cardinalColor: string): THREE.Sprite {
        const mat    = new THREE.SpriteMaterial({ 
            map: this.createCardinalTexture(text, cardinalColor), 
            transparent: true, 
            depthWrite: false
        });
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(20, 20, 1);
        return sprite;
    }

    /**
     * Creates a canvas texture containing the specified text.
     * @param {string} text - The text to render.
     * @param {string} color - CSS color string for the text.
     * @returns {THREE.CanvasTexture} The generated texture.
     * @private
     */
    private createCardinalTexture(text: string, color: string): THREE.CanvasTexture {
        const canvas = document.createElement('canvas');
        canvas.width  = 128; canvas.height = 128;
        const ctx = canvas.getContext('2d')!;
        ctx.fillStyle    = color;
        ctx.font         = '72px Inter, system-ui, sans-serif';
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 64, 64);
        return new THREE.CanvasTexture(canvas);
    }

    /**
     * Toggles the visibility of the ground plane.
     * @param {boolean} visible - Whether the ground should be visible.
     */
    setGroundVisible(visible: boolean) {
        this.groundMesh.visible = visible;
    }

    /**
     * Dynamically updates the ground base color.
     * @param {number} color - Hex color value for the ground.
     */
    setGroundColor(color: number) {
        this.baseGroundColor = color;
        this.lastDayFactor = -1; // Reset to force updateDaylight calculation
        (this.groundMesh.material as THREE.MeshBasicMaterial).color.setHex(color);
    }

    /**
     * Updates the ground color based on daylight to provide better contrast.
     * @param {number} daylightFade - Fade factor for daylight (1.0 = night, 0.0 = day).
     */
    updateDaylight(daylightFade: number) {
        if (!this.groundMesh) return;

        const dayFactor = 1.0 - daylightFade; // 0 (night) to 1 (day)

        // Update ground color every frame
        const color = new THREE.Color(this.baseGroundColor);

        // Only adjust if atmosphere is ON and it is currently daytime
        if (this.isAtmosphereEnabled() && dayFactor > 0) {
            const hsl = { h: 0, s: 0, l: 0 };
            color.getHSL(hsl);

            // Lighten the ground slightly
            hsl.l = Math.min(0.7, hsl.l + (dayFactor * 0.03));

            color.setHSL(hsl.h, hsl.s, hsl.l);
        }

        (this.groundMesh.material as THREE.MeshBasicMaterial).color.copy(color);
    }

    /**
     * Safely disposes of geometries, materials, and textures to prevent memory leaks.
     */
    dispose() {
        this.group.children.forEach(child => {
            if (child instanceof THREE.Sprite) {
                child.material.map?.dispose();
                child.material.dispose();
            } else if (child instanceof THREE.Mesh) {
                child.geometry.dispose();
                (child.material as THREE.Material).dispose();
            }
        });
    }
}