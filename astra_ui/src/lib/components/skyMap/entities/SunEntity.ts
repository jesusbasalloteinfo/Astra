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

// src/lib/components/skyMap/entities/SunEntity.ts

import * as THREE from 'three';
import { AbstractPlanetaryObject } from './AbstractPlanetaryObject';
import { PLANET_SIZE_BASE, PLANET_VISUAL_SIZES, PLANET_COLORS, FOV_DEFAULT } from '../utils/const';

/**
 * Dedicated Vertex Shader for the Sun entity.
 */
const sunVertexShader = `
    attribute float size;
    attribute vec3 color;
    
    varying vec3 vColor;
    varying float vAlphaFactor;
    
    uniform float zoom;

    void main() {
        vColor = color;
        
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        float actualSize = size * zoom;

        gl_PointSize = max(2.5, actualSize);
        vAlphaFactor = min(1.0, actualSize / gl_PointSize);
        gl_Position = projectionMatrix * mvPosition;
    }
`;

/**
 * Dedicated Fragment Shader for the Sun entity.
 * Implements intense core burn, corona glow, and cross diffraction spikes.
 * Does NOT fade out when zooming in (Sun is textureless and rendered via custom shader optics).
 */
const sunFragmentShader = `
    varying vec3 vColor;
    varying float vAlphaFactor;
    uniform float opacity;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist = length(coord);
        
        if (dist > 0.5) discard;

        float masterFade = smoothstep(0.5, 0.25, dist); 
        
        // 1. Radial Light Simulation
        float coreBurn = exp(-pow(dist * 25.0, 2.0)) * 2.5; 
        float innerGlow = exp(-dist * 12.0) * 0.7;
        float outerGlow = exp(-dist * 5.0) * 0.35;
        float radialLight = (coreBurn + innerGlow + outerGlow) * masterFade;
        
        // 2. Diffraction Spikes Simulation
        float spikeX = exp(-abs(coord.x) * 100.0);
        float spikeY = exp(-abs(coord.y) * 100.0);
        float crossShape = max(spikeX, spikeY);
        float spikeStart = smoothstep(0.04, 0.15, dist);
        
        float spikes = crossShape * exp(-dist * 4.0) * 0.8 * masterFade * spikeStart;
        float totalLight = radialLight + spikes;
        
        vec3 sunTint = vec3(1.0, 0.95, 0.85); 
        vec3 finalColor = mix(sunTint, vec3(1.0), smoothstep(0.6, 1.5, totalLight));
        
        float alpha = min(1.0, totalLight);

        gl_FragColor = vec4(finalColor, alpha * opacity * vAlphaFactor);
    }
`;

/**
 * SunEntity
 * 
 * Represents the Sun in the solar system.
 * Characteristics:
 * - Textureless entity rendered with custom optical halo and diffraction shader.
 * - Primary light source generator for sky atmosphere and planetary phase lighting.
 */
export class SunEntity extends AbstractPlanetaryObject {
    /** Points mesh rendering the Sun's optical billboard */
    private sunPointMesh: THREE.Points;
    /** Shader material managing Sun optical uniforms */
    private sunMaterial: THREE.ShaderMaterial;

    constructor(opacity: number = 1.0) {
        const baseSize = (PLANET_VISUAL_SIZES['sun'] ?? (PLANET_SIZE_BASE * 8.0)) * 3.8;
        const colorHex = PLANET_COLORS['sun'] ?? 0xfffae6;

        super('sun', 'Sun', baseSize, colorHex, -0.65, -1.55);

        // 1. Geometry with single vertex at entity local origin (0,0,0)
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, 0, 0]), 3));
        geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array([this.color.r, this.color.g, this.color.b]), 3));
        geo.setAttribute('size', new THREE.BufferAttribute(new Float32Array([this.baseSize]), 1));

        // 2. Sun Shader Material
        this.sunMaterial = new THREE.ShaderMaterial({
            uniforms: {
                zoom: { value: 1.0 },
                fov: { value: FOV_DEFAULT },
                opacity: { value: opacity }
            },
            vertexShader: sunVertexShader,
            fragmentShader: sunFragmentShader,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            depthTest: true
        });

        this.sunPointMesh = new THREE.Points(geo, this.sunMaterial);
        this.sunPointMesh.renderOrder = 2;
        this.sunPointMesh.userData = { planetId: 'sun' };

        this.group.add(this.sunPointMesh);
    }

    /**
     * Updates the Sun position and shader uniforms.
     */
    public update(
        alt: number,
        az: number,
        zoomFactor: number,
        daylightFade: number = 1.0,
        currentFov: number = FOV_DEFAULT
    ): void {
        this.setPosition(alt, az);
        this.sunMaterial.uniforms.zoom.value = zoomFactor;
        this.sunMaterial.uniforms.fov.value = currentFov;
    }

    public getRaycastObjects(): THREE.Object3D[] {
        return [this.sunPointMesh];
    }

    public getPointMesh(): THREE.Points | null {
        return this.sunPointMesh;
    }

    public dispose(): void {
        super.dispose();
        this.sunPointMesh.geometry.dispose();
        this.sunMaterial.dispose();
    }
}
