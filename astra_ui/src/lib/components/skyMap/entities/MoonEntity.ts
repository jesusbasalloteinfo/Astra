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

// src/lib/components/skyMap/entities/MoonEntity.ts

import * as THREE from 'three';
import { AbstractPlanetaryObject } from './AbstractPlanetaryObject';
import { PLANET_SIZE_BASE, PLANET_VISUAL_SIZES, PLANET_COLORS, FOV_DEFAULT } from '../utils/const';
import { locStore } from '$lib/stores/location.svelte';

/** Dedicated Vertex Shader for Moon point billboard rendering */
const moonVertexShader = `
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

/** Dedicated Fragment Shader for Moon point billboard rendering with FOV cross-fading */
const moonFragmentShader = `
    varying vec3 vColor;
    varying float vAlphaFactor;
    uniform float opacity;
    uniform float fov;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist = length(coord);
        
        if (dist > 0.5) discard;

        float core = exp(-pow(dist * 12.0, 2.0)) * 1.5; 
        float halo = exp(-dist * 5.0) * 0.4;
        
        vec3 moonColor = vec3(1.0, 0.98, 0.92); 
        vec3 finalColor = mix(moonColor, vec3(1.0), min(1.0, core * 1.2));
        
        float alpha = (core + halo) * smoothstep(0.5, 0.2, dist);

        // Cross-fade factor: Fade out point billboard when zooming in (FOV < 22°)
        float rawFovBlend = clamp((fov - 8.0) / (22.0 - 8.0), 0.0, 1.0);
        float pointFade = rawFovBlend * rawFovBlend * (3.0 - 2.0 * rawFovBlend);

        gl_FragColor = vec4(finalColor, alpha * opacity * vAlphaFactor * pointFade);
    }
`;

/**
 * MoonEntity
 * 
 * Represents Earth's Moon in the solar system.
 * Characteristics:
 * - Photorealistic surface texture (`/textures/moon.jpg`).
 * - Tidally locked orientation (0 rotation speed) keeping its near side facing Earth.
 * - Topocentric polar orientation aligned with observer latitude and position angle (NCP).
 * - Physical Daytime Shading:
 *   1. Smooth geometric terminator based purely on N dot L (prevents texture maria from creating transparency "bites").
 *   2. Proportional opacity fade near grazing incidence (eliminates dark line/band artifacts along the terminator).
 *   3. Dynamic depthWrite management during FOV cross-fade (prevents black disc z-buffer masking artifacts).
 *   4. Unlit shadow side is 100% transparent in daytime atmosphere mode (blue sky background passes completely through shadow).
 *   5. Non-maria highlands are brightened and whitened during daytime for realistic daytime lunar rock rendering.
 * - Axial tilt (6.68°) and realistic lunar phase lighting from Directional Sunlight.
 * - Seamless transition between 2D point billboard and 3D textured sphere based on FOV.
 */
export class MoonEntity extends AbstractPlanetaryObject {
    /** 2D Point Billboard mesh */
    private moonPointMesh: THREE.Points;
    /** Point billboard shader material */
    private moonPointMaterial: THREE.ShaderMaterial;

    /** 3D model root group for lookAt camera tracking */
    private modelRootGroup: THREE.Group;
    /** 3D model inner tilt group for axial tilt */
    private modelTiltGroup: THREE.Group;
    /** 3D sphere mesh */
    private moonMesh: THREE.Mesh;
    /** 3D standard material */
    private moonMaterial: THREE.MeshStandardMaterial;

    /** Texture loader */
    private textureLoader = new THREE.TextureLoader();

    constructor(opacity: number = 1.0) {
        const baseSize = (PLANET_VISUAL_SIZES['moon'] ?? (PLANET_SIZE_BASE * 7.0)) * 2.2;
        const colorHex = PLANET_COLORS['moon'] ?? 0xe2e8f0;

        super('moon', 'Moon', baseSize, colorHex, -0.25, -0.45);

        // 1. 2D Point Billboard Setup
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, 0, 0]), 3));
        geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array([this.color.r, this.color.g, this.color.b]), 3));
        geo.setAttribute('size', new THREE.BufferAttribute(new Float32Array([this.baseSize]), 1));

        this.moonPointMaterial = new THREE.ShaderMaterial({
            uniforms: {
                zoom: { value: 1.0 },
                fov: { value: FOV_DEFAULT },
                opacity: { value: opacity }
            },
            vertexShader: moonVertexShader,
            fragmentShader: moonFragmentShader,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            depthTest: true
        });

        this.moonPointMesh = new THREE.Points(geo, this.moonPointMaterial);
        this.moonPointMesh.renderOrder = 2;
        this.moonPointMesh.userData = { planetId: 'moon' };
        this.group.add(this.moonPointMesh);

        // 2. Photorealistic 3D Model Setup
        this.modelRootGroup = new THREE.Group();
        this.modelRootGroup.visible = false;

        this.modelTiltGroup = new THREE.Group();
        const tiltRad = 6.68 * (Math.PI / 180);
        this.modelTiltGroup.rotation.z = tiltRad;
        this.modelRootGroup.add(this.modelTiltGroup);

        const texture = this.textureLoader.load('/textures/moon.jpg');
        texture.colorSpace = THREE.SRGBColorSpace;

        this.moonMaterial = new THREE.MeshStandardMaterial({
            map: texture,
            roughness: 0.95,
            metalness: 0.05,
            transparent: true,
            opacity: 1.0,
            depthWrite: false,
            depthTest: true
        });

        // Store custom shader uniforms for daytime atmosphere transparency & pale rock effect
        this.moonMaterial.userData = {
            uDayFactor: { value: 0.0 },
            uFovBlend: { value: 0.0 }
        };

        this.moonMaterial.onBeforeCompile = (shader) => {
            shader.uniforms.uDayFactor = this.moonMaterial.userData.uDayFactor;
            shader.uniforms.uFovBlend = this.moonMaterial.userData.uFovBlend;

            shader.fragmentShader = `
                uniform float uDayFactor;
                uniform float uFovBlend;
                ${shader.fragmentShader}
            `;

            shader.fragmentShader = shader.fragmentShader.replace(
                '#include <dithering_fragment>',
                `
                #include <dithering_fragment>
                
                // 1. Pure geometric incidence angle (independent of texture color)
                float dotNL = dot(geometryNormal, directLight.direction);
                
                // Smooth lit factor: fades to 0 smoothly as direct sunlight reaches the terminator (dotNL <= 0),
                // eliminating any dark line or band artifact at grazing incidence
                float litFactor = smoothstep(0.0, 0.22, dotNL);

                // 2. Brighten non-maria highlands (parts that are not dark seas) during daytime
                float luminance = max(gl_FragColor.r, max(gl_FragColor.g, gl_FragColor.b));
                float highlandMask = smoothstep(0.20, 0.55, luminance);
                vec3 brightHighlands = mix(gl_FragColor.rgb, vec3(0.98, 0.99, 1.0), 0.60 * highlandMask * uDayFactor);
                gl_FragColor.rgb = mix(gl_FragColor.rgb, brightHighlands, uDayFactor * 0.75);

                // 3. Daytime shadow transparency:
                // At night (uDayFactor = 0): opacity is 1.0 across full sphere.
                // At day (uDayFactor = 1): shadow side (litFactor = 0) is 100% TRANSPARENT (blue sky passes through),
                // lit side fades out smoothly to 0 at the terminator line.
                float dayAlpha = litFactor * 0.85;
                float finalAlpha = mix(1.0, dayAlpha, uDayFactor) * uFovBlend;

                gl_FragColor.a = finalAlpha;
                `
            );
        };

        const sphereGeo = new THREE.SphereGeometry(8.0, 64, 64);
        this.moonMesh = new THREE.Mesh(sphereGeo, this.moonMaterial);
        this.moonMesh.userData = { planetId: 'moon' };

        // CRITICAL for Moon near-side orientation: Rotate mesh by -90° on Y-axis
        // so texture center (Oceanus Procellarum / Tycho) faces Earth/observer!
        this.moonMesh.rotation.y = -Math.PI / 2;
        this.modelTiltGroup.add(this.moonMesh);

        this.group.add(this.modelRootGroup);
    }

    /**
     * Updates Moon position, FOV blend opacity, topocentric orientation, and daytime atmospheric transparency.
     */
    public update(
        alt: number,
        az: number,
        zoomFactor: number,
        daylightFade: number = 1.0,
        currentFov: number = FOV_DEFAULT
    ): void {
        this.setPosition(alt, az);
        
        // 1. Update 2D Point Shader
        this.moonPointMaterial.uniforms.zoom.value = zoomFactor;
        this.moonPointMaterial.uniforms.fov.value = currentFov;

        // 2. Calculate FOV Cross-Fade Blend Factor
        const fovStart = 22.0;
        const fovEnd = 8.0;
        const rawBlend = (fovStart - currentFov) / (fovStart - fovEnd);
        const blend = Math.max(0.0, Math.min(1.0, rawBlend));
        const smoothBlend = blend * blend * (3 - 2 * blend);

        // 3. Topocentric polar orientation (align Moon polar axis with North Celestial Pole from observer latitude)
        const latDeg = locStore.active?.lat ?? 40.0;
        const latRad = latDeg * (Math.PI / 180);
        const ncpVector = new THREE.Vector3(0, Math.sin(latRad), -Math.cos(latRad)).normalize();

        this.modelRootGroup.up.copy(ncpVector);
        this.modelRootGroup.lookAt(0, 0, 0);

        // 4. Daytime Atmosphere Shader Uniforms & Depth Write Control
        const dayFactor = 1.0 - daylightFade; // 0.0 at night, 1.0 at full day

        this.moonMaterial.userData.uDayFactor.value = dayFactor;
        this.moonMaterial.userData.uFovBlend.value = smoothBlend;

        // CRITICAL FIX FOR BLACK DISC ARTIFCAT:
        // Disable depthWrite during FOV cross-fade (smoothBlend < 0.95) so semi-transparent 3D mesh
        // does not write z-depth and mask out background point billboard or sky!
        this.moonMaterial.depthWrite = smoothBlend >= 0.95;

        this.modelRootGroup.visible = smoothBlend > 0.01;
    }

    public getRaycastObjects(): THREE.Object3D[] {
        return [this.moonMesh, this.moonPointMesh];
    }

    public get3DMeshes(): THREE.Mesh[] {
        return [this.moonMesh];
    }

    public getPointMesh(): THREE.Points | null {
        return this.moonPointMesh;
    }

    public dispose(): void {
        super.dispose();
        this.moonPointMesh.geometry.dispose();
        this.moonPointMaterial.dispose();
        this.moonMesh.geometry.dispose();
        this.moonMaterial.dispose();
    }
}
