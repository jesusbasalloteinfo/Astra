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

// src/lib/components/skyMap/entities/PlanetEntity.ts

import * as THREE from 'three';
import { AbstractPlanetaryObject } from './AbstractPlanetaryObject';
import { PLANET_SIZE_BASE, PLANET_VISUAL_SIZES, PLANET_COLORS, FOV_DEFAULT } from '../utils/const';
import { locStore } from '$lib/stores/location.svelte';

/** Configuration interface for individual planetary entities */
export interface PlanetConfig {
    id: string;
    name: string;
    textureUrl?: string;
    hasTexture?: boolean;
    radius: number;
    axialTiltDeg: number;
    rotationSpeed: number;
    roughness: number;
}

/** Pre-configured planetary parameters for solar system planets */
export const PLANET_CONFIGS: Record<string, PlanetConfig> = {
    mercury: {
        id: 'mercury',
        name: 'Mercury',
        textureUrl: '/textures/mercury.jpg',
        hasTexture: true,
        radius: 3.5,
        axialTiltDeg: 0.03,
        rotationSpeed: 0.0002,
        roughness: 0.9
    },
    venus: {
        id: 'venus',
        name: 'Venus',
        textureUrl: '/textures/venus.jpg',
        hasTexture: true,
        radius: 4.8,
        axialTiltDeg: 177.3,
        rotationSpeed: -0.0001,
        roughness: 0.7
    },
    mars: {
        id: 'mars',
        name: 'Mars',
        textureUrl: '/textures/mars.jpg',
        hasTexture: true,
        radius: 4.2,
        axialTiltDeg: 25.19,
        rotationSpeed: 0.0005,
        roughness: 0.85
    },
    jupiter: {
        id: 'jupiter',
        name: 'Jupiter',
        textureUrl: '/textures/jupiter.jpg',
        hasTexture: true,
        radius: 6.5,
        axialTiltDeg: 3.13,
        rotationSpeed: 0.001,
        roughness: 0.6
    },
    saturn: {
        id: 'saturn',
        name: 'Saturn',
        textureUrl: '/textures/saturn.jpg',
        hasTexture: true,
        radius: 5.2,
        axialTiltDeg: 26.73,
        rotationSpeed: 0.0009,
        roughness: 0.65
    },
    uranus: {
        id: 'uranus',
        name: 'Uranus',
        textureUrl: '/textures/uranus.jpg',
        hasTexture: true,
        radius: 4.2,
        axialTiltDeg: 97.77,
        rotationSpeed: -0.0006,
        roughness: 0.6
    },
    neptune: {
        id: 'neptune',
        name: 'Neptune',
        textureUrl: '/textures/neptune.jpg',
        hasTexture: true,
        radius: 4.2,
        axialTiltDeg: 28.32,
        rotationSpeed: 0.0007,
        roughness: 0.6
    },
    pluto: {
        id: 'pluto',
        name: 'Pluto',
        textureUrl: '/textures/pluto.jpg',
        hasTexture: true,
        radius: 3.0,
        axialTiltDeg: 122.5,
        rotationSpeed: 0.0003,
        roughness: 0.85
    }
};

/** Dedicated Vertex Shader for Planet point billboard rendering */
const planetVertexShader = `
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

/** Dedicated Fragment Shader for Planet point billboard rendering with FOV cross-fading */
const planetFragmentShader = `
    varying vec3 vColor;
    varying float vAlphaFactor;
    uniform float opacity;
    uniform float fov;
    uniform float hasTexture;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist = length(coord);
        
        if (dist > 0.5) discard;

        float core = exp(-pow(dist * 12.0, 2.0)) * 1.5; 
        float halo = exp(-dist * 5.0) * 0.8;
        
        vec3 finalColor = mix(vColor, vec3(1.0), min(1.0, core * 1.2));
        float alpha = (core + halo) * smoothstep(0.5, 0.2, dist);

        // Cross-fade factor: Fade out point billboard when zooming in ONLY if 3D texture model exists
        float pointFade = 1.0;
        if (hasTexture > 0.5) {
            float rawFovBlend = clamp((fov - 8.0) / (22.0 - 8.0), 0.0, 1.0);
            pointFade = rawFovBlend * rawFovBlend * (3.0 - 2.0 * rawFovBlend);
        }

        gl_FragColor = vec4(finalColor, alpha * opacity * vAlphaFactor * pointFade);
    }
`;

/**
 * PlanetEntity
 * 
 * Represents a solar system planet (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto).
 * Characteristics:
 * - If `hasTexture` is true, loads 3D surface texture and renders photorealistic 3D model on zoom.
 * - If `hasTexture` is false (or texture missing), remains as a luminous 2D point billboard at all zoom levels.
 * - Topocentric polar orientation aligned with observer latitude and position angle (NCP).
 * - Physical Daytime Shading with smooth geometric terminator and surface whitening.
 * - Axial tilt and continuous Y-axis rotation logic.
 * - Special ring system for Saturn (procedural radial alpha canvas texture).
 */
export class PlanetEntity extends AbstractPlanetaryObject {
    public readonly config: PlanetConfig;
    public readonly hasTexture: boolean;

    /** 2D Point Billboard mesh */
    private pointMesh: THREE.Points;
    /** Point billboard shader material */
    private pointMaterial: THREE.ShaderMaterial;

    /** 3D model root group for lookAt camera tracking */
    private modelRootGroup: THREE.Group | null = null;
    /** 3D model inner tilt group for axial tilt */
    private modelTiltGroup: THREE.Group | null = null;
    /** 3D sphere mesh */
    private planetMesh: THREE.Mesh | null = null;
    /** 3D standard material */
    private planetMaterial: THREE.MeshStandardMaterial | null = null;
    /** Optional ring mesh for Saturn */
    private ringMesh: THREE.Mesh | null = null;
    private ringMaterial: THREE.MeshStandardMaterial | null = null;

    /** Texture loader */
    private textureLoader = new THREE.TextureLoader();

    constructor(config: PlanetConfig, opacity: number = 1.0) {
        const visualMult = PLANET_VISUAL_SIZES[config.id] ?? PLANET_SIZE_BASE;
        const baseSize = visualMult * 2.5;
        const colorHex = PLANET_COLORS[config.id] ?? 0xffffff;

        super(config.id, config.name, baseSize, colorHex, -0.075, -0.075);
        this.config = config;
        this.hasTexture = config.hasTexture !== false && Boolean(config.textureUrl);
        this.hasTexture = false;

        // 1. 2D Point Billboard Setup
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, 0, 0]), 3));
        geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array([this.color.r, this.color.g, this.color.b]), 3));
        geo.setAttribute('size', new THREE.BufferAttribute(new Float32Array([this.baseSize]), 1));

        this.pointMaterial = new THREE.ShaderMaterial({
            uniforms: {
                zoom: { value: 1.0 },
                fov: { value: FOV_DEFAULT },
                opacity: { value: opacity },
                hasTexture: { value: this.hasTexture ? 1.0 : 0.0 }
            },
            vertexShader: planetVertexShader,
            fragmentShader: planetFragmentShader,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            depthTest: true
        });

        this.pointMesh = new THREE.Points(geo, this.pointMaterial);
        this.pointMesh.renderOrder = 2;
        this.pointMesh.userData = { planetId: config.id };
        this.group.add(this.pointMesh);

        // 2. Photorealistic 3D Model Setup (ONLY if texture exists)
        if (this.hasTexture && config.textureUrl) {
            this.modelRootGroup = new THREE.Group();
            this.modelRootGroup.visible = false;

            this.modelTiltGroup = new THREE.Group();
            const tiltRad = config.axialTiltDeg * (Math.PI / 180);
            this.modelTiltGroup.rotation.z = tiltRad;
            this.modelRootGroup.add(this.modelTiltGroup);

            const texture = this.textureLoader.load(config.textureUrl);
            texture.colorSpace = THREE.SRGBColorSpace;

            this.planetMaterial = new THREE.MeshStandardMaterial({
                map: texture,
                roughness: config.roughness,
                metalness: 0.05,
                transparent: true,
                opacity: 1.0,
                depthWrite: false,
                depthTest: true
            });

            this.planetMaterial.userData = {
                uDayFactor: { value: 0.0 },
                uFovBlend: { value: 0.0 }
            };

            this.planetMaterial.onBeforeCompile = (shader) => {
                shader.uniforms.uDayFactor = this.planetMaterial!.userData.uDayFactor;
                shader.uniforms.uFovBlend = this.planetMaterial!.userData.uFovBlend;

                shader.fragmentShader = `
                    uniform float uDayFactor;
                    uniform float uFovBlend;
                    ${shader.fragmentShader}
                `;

                shader.fragmentShader = shader.fragmentShader.replace(
                    '#include <dithering_fragment>',
                    `
                    #include <dithering_fragment>
                    
                    float dotNL = dot(geometryNormal, directLight.direction);
                    float litFactor = smoothstep(0.0, 0.22, dotNL);

                    float luminance = max(gl_FragColor.r, max(gl_FragColor.g, gl_FragColor.b));
                    float highlandMask = smoothstep(0.20, 0.55, luminance);
                    vec3 brightSurface = mix(gl_FragColor.rgb, vec3(0.95, 0.96, 1.0), 0.50 * highlandMask * uDayFactor);
                    gl_FragColor.rgb = mix(gl_FragColor.rgb, brightSurface, uDayFactor * 0.70);

                    float dayAlpha = litFactor * 0.85;
                    float finalAlpha = mix(1.0, dayAlpha, uDayFactor) * uFovBlend;

                    gl_FragColor.a = finalAlpha;
                    `
                );
            };

            const sphereGeo = new THREE.SphereGeometry(config.radius, 64, 64);
            this.planetMesh = new THREE.Mesh(sphereGeo, this.planetMaterial);
            this.planetMesh.userData = { planetId: config.id };
            this.planetMesh.rotation.y = -Math.PI / 2;

            this.modelTiltGroup.add(this.planetMesh);

            // Saturn Rings Special Case
            if (config.id === 'saturn') {
                this.createSaturnRings(config.radius);
            }

            this.group.add(this.modelRootGroup);
        }
    }

    /**
     * Generates Saturn's rings with procedural alpha texture.
     */
    private createSaturnRings(planetRadius: number) {
        if (!this.modelTiltGroup) return;

        const innerRadius = planetRadius * 1.35;
        const outerRadius = planetRadius * 2.45;

        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 1;
        const ctx = canvas.getContext('2d')!;

        const grad = ctx.createLinearGradient(0, 0, 512, 0);
        grad.addColorStop(0.00, 'rgba(0, 0, 0, 0)');
        grad.addColorStop(0.10, 'rgba(120, 110, 90, 0.3)');   // C ring
        grad.addColorStop(0.25, 'rgba(210, 195, 160, 0.85)'); // B ring inner
        grad.addColorStop(0.55, 'rgba(235, 220, 185, 0.95)'); // B ring outer
        grad.addColorStop(0.58, 'rgba(10, 10, 10, 0.1)');     // Cassini division
        grad.addColorStop(0.62, 'rgba(180, 165, 135, 0.75)'); // A ring inner
        grad.addColorStop(0.92, 'rgba(160, 145, 120, 0.6)');  // A ring outer
        grad.addColorStop(0.96, 'rgba(0, 0, 0, 0)');          // Encke gap
        grad.addColorStop(1.00, 'rgba(0, 0, 0, 0)');

        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 512, 1);

        const ringTexture = new THREE.CanvasTexture(canvas);
        ringTexture.wrapS = THREE.ClampToEdgeWrapping;
        ringTexture.wrapT = THREE.ClampToEdgeWrapping;

        const ringGeo = new THREE.RingGeometry(innerRadius, outerRadius, 64);
        
        const pos = ringGeo.attributes.position;
        const uvs = new Float32Array(pos.count * 2);
        for (let i = 0; i < pos.count; i++) {
            const x = pos.getX(i);
            const y = pos.getY(i);
            const r = Math.sqrt(x * x + y * y);
            const u = (r - innerRadius) / (outerRadius - innerRadius);
            uvs[i * 2] = u;
            uvs[i * 2 + 1] = 0.5;
        }
        ringGeo.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));

        this.ringMaterial = new THREE.MeshStandardMaterial({
            map: ringTexture,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.0,
            roughness: 0.6,
            metalness: 0.1,
            depthWrite: false,
            depthTest: true
        });

        this.ringMesh = new THREE.Mesh(ringGeo, this.ringMaterial);
        this.ringMesh.rotation.x = Math.PI / 2;
        this.ringMesh.userData = { planetId: 'saturn', isSaturnRing: true };

        this.modelTiltGroup.add(this.ringMesh);
    }

    /**
     * Updates planet position, rotation, FOV cross-fade opacity, and atmospheric surface sky tinting.
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
        this.pointMaterial.uniforms.zoom.value = zoomFactor;
        this.pointMaterial.uniforms.fov.value = currentFov;

        // 2. If entity has 3D texture model, update 3D model spin, opacity & cross-fade
        if (this.hasTexture && this.modelRootGroup && this.planetMesh && this.planetMaterial) {
            if (this.config.rotationSpeed !== 0) {
                this.planetMesh.rotation.y += this.config.rotationSpeed;
            }

            const fovStart = 22.0;
            const fovEnd = 8.0;
            const rawBlend = (fovStart - currentFov) / (fovStart - fovEnd);
            const blend = Math.max(0.0, Math.min(1.0, rawBlend));
            const smoothBlend = blend * blend * (3 - 2 * blend);

            const latDeg = locStore.active?.lat ?? 40.0;
            const latRad = latDeg * (Math.PI / 180);
            const ncpVector = new THREE.Vector3(0, Math.sin(latRad), -Math.cos(latRad)).normalize();

            this.modelRootGroup.up.copy(ncpVector);
            this.modelRootGroup.lookAt(0, 0, 0);

            // Daytime atmosphere shader uniforms
            const dayFactor = 1.0 - daylightFade;

            this.planetMaterial.userData.uDayFactor.value = dayFactor;
            this.planetMaterial.userData.uFovBlend.value = smoothBlend;

            const isFullyZoomedIn = smoothBlend >= 0.95;
            this.planetMaterial.depthWrite = isFullyZoomedIn;

            if (this.ringMaterial) {
                this.ringMaterial.opacity = smoothBlend * 0.9 * (1.0 - dayFactor * 0.25);
                this.ringMaterial.depthWrite = isFullyZoomedIn;
            }

            this.modelRootGroup.visible = smoothBlend > 0.01;
        }
    }

    public getRaycastObjects(): THREE.Object3D[] {
        const list: THREE.Object3D[] = [this.pointMesh];
        if (this.planetMesh) list.push(this.planetMesh);
        if (this.ringMesh) list.push(this.ringMesh);
        return list;
    }

    public get3DMeshes(): THREE.Mesh[] {
        const list: THREE.Mesh[] = [];
        if (this.planetMesh) list.push(this.planetMesh);
        if (this.ringMesh) list.push(this.ringMesh);
        return list;
    }

    public getPointMesh(): THREE.Points | null {
        return this.pointMesh;
    }

    public dispose(): void {
        super.dispose();
        this.pointMesh.geometry.dispose();
        this.pointMaterial.dispose();
        if (this.planetMesh) {
            this.planetMesh.geometry.dispose();
            if (this.planetMaterial) this.planetMaterial.dispose();
        }
        if (this.ringMesh) {
            this.ringMesh.geometry.dispose();
            if (this.ringMaterial) this.ringMaterial.dispose();
        }
    }
}
