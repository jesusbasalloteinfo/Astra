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

// src/lib/components/skyMap/entities/SolarSystemManager.ts

import * as THREE from 'three';
import { AbstractPlanetaryObject } from './AbstractPlanetaryObject';
import { SunEntity } from './SunEntity';
import { MoonEntity } from './MoonEntity';
import { PlanetEntity, PLANET_CONFIGS } from './PlanetEntity';
import { FOV_DEFAULT, DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';
import type { PositionUpdates } from '$lib/stores/skyEngine.svelte';

/**
 * SolarSystemManager
 * 
 * Main orchestrator for solar system entities in the sky map.
 * Groups and coordinates the Sun (`SunEntity`), Moon (`MoonEntity`), and planets (`PlanetEntity`).
 * Handles sunlight direction vectors for photorealistic lunar/planetary phase lighting,
 * daylight transitions, and selection raycasting.
 */
export class SolarSystemManager {
    /** Root group node added to the Three.js scene */
    public group: THREE.Group = new THREE.Group();

    /** Dedicated Sun entity */
    public sun: SunEntity;
    /** Dedicated Moon entity */
    public moon: MoonEntity;
    /** Map of planetary entities indexed by lower-case ID */
    public planets: Map<string, PlanetEntity> = new Map();
    /** Map of all solar system entities indexed by lower-case ID */
    public entities: Map<string, AbstractPlanetaryObject> = new Map();

    /** Ordered list of entity IDs for index-based API compatibility */
    private planetIds: string[] = [];

    /** Directional light simulating physical sunlight */
    private sunLight: THREE.DirectionalLight;
    /** Soft ambient fill light for unlit side (earthshine/space background) */
    private ambientLight: THREE.AmbientLight;

    /** Composite Points mesh kept for index-based raycasting backwards compatibility */
    private compositePointsMesh: THREE.Points;

    /** Daylight state tracking */
    private lastDayFactor: number = -1;

    constructor(opacity: number = 1.0) {
        // 1. Lighting Setup
        this.sunLight = new THREE.DirectionalLight(0xffffff, 3.5);
        this.sunLight.castShadow = false;
        this.group.add(this.sunLight);
        this.group.add(this.sunLight.target);

        // Keep ambient fill subtle so shadows stay dark and realistic
        this.ambientLight = new THREE.AmbientLight(0x222834, 0.08);
        this.group.add(this.ambientLight);

        // 2. Determine celestial IDs from catalog or fallback
        const catalogKeys = Object.keys(catalogStore.planetaryData);
        if (catalogKeys.length > 0) {
            this.planetIds = catalogKeys;
        } else {
            this.planetIds = ['sun', 'moon', ...Object.keys(PLANET_CONFIGS)];
        }

        // 3. Instantiate Entities
        this.sun = new SunEntity(opacity);
        this.entities.set('sun', this.sun);
        this.group.add(this.sun.group);

        this.moon = new MoonEntity(opacity);
        this.entities.set('moon', this.moon);
        this.group.add(this.moon.group);

        Object.values(PLANET_CONFIGS).forEach(config => {
            const planet = new PlanetEntity(config, opacity);
            this.planets.set(config.id, planet);
            this.entities.set(config.id, planet);
            this.group.add(planet.group);
        });

        // Ensure all catalog keys are registered
        this.planetIds.forEach(id => {
            const lower = id.toLowerCase();
            if (!this.entities.has(lower) && lower !== 'sun' && lower !== 'moon') {
                const fallbackConfig = PLANET_CONFIGS[lower] ?? {
                    id: lower,
                    name: id,
                    textureUrl: `/textures/${lower}.jpg`,
                    hasTexture: true,
                    radius: 4.0,
                    axialTiltDeg: 0,
                    rotationSpeed: 0.0005,
                    roughness: 0.8
                };
                const planet = new PlanetEntity(fallbackConfig, opacity);
                this.planets.set(lower, planet);
                this.entities.set(lower, planet);
                this.group.add(planet.group);
            }
        });

        // 4. Create composite points geometry for selection compatibility
        const num = this.planetIds.length;
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(num * 3), 3));
        geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(num * 3), 3));
        geo.setAttribute('size', new THREE.BufferAttribute(new Float32Array(num), 1));
        
        const mat = new THREE.PointsMaterial({ size: 1, visible: false });
        this.compositePointsMesh = new THREE.Points(geo, mat);
        this.group.add(this.compositePointsMesh);
        
        this.syncCompositeGeometry();
    }

    /**
     * Synchronizes composite geometry attributes with entity parameters.
     */
    private syncCompositeGeometry() {
        const positions = this.compositePointsMesh.geometry.attributes.position.array as Float32Array;
        const colors = this.compositePointsMesh.geometry.attributes.color.array as Float32Array;
        const sizes = this.compositePointsMesh.geometry.attributes.size.array as Float32Array;

        for (let i = 0; i < this.planetIds.length; i++) {
            const id = this.planetIds[i].toLowerCase();
            const entity = this.entities.get(id);
            if (entity) {
                sizes[i] = entity.baseSize;
                colors[i * 3] = entity.color.r;
                colors[i * 3 + 1] = entity.color.g;
                colors[i * 3 + 2] = entity.color.b;

                const pos = entity.group.position;
                positions[i * 3] = pos.x;
                positions[i * 3 + 1] = pos.y;
                positions[i * 3 + 2] = pos.z;
            }
        }
        this.compositePointsMesh.geometry.attributes.position.needsUpdate = true;
        this.compositePointsMesh.geometry.attributes.color.needsUpdate = true;
        this.compositePointsMesh.geometry.attributes.size.needsUpdate = true;
    }

    /**
     * Updates solar system objects based on new Alt/Az positional data.
     * Receives astronomical updates and orchestrates Sun, Moon, and planet updates.
     */
    public update(
        positionsMap: PositionUpdates,
        zoomFactor: number,
        daylightFade: number = 1.0,
        currentFov: number = FOV_DEFAULT
    ): void {
        const dayFactor = 1.0 - daylightFade;

        // 1. Update Sunlight Direction
        const sunPos = positionsMap.get('sun');
        if (sunPos) {
            const sunVec = new Float32Array(3);
            altAzToXYZ(sunVec, 0, sunPos.alt, sunPos.az);

            this.sunLight.position.set(sunVec[0], sunVec[1], sunVec[2]);
            this.sunLight.target.position.set(0, 1.6, 0);
            this.sunLight.target.updateMatrixWorld();

            this.sun.update(sunPos.alt, sunPos.az, zoomFactor, daylightFade, currentFov);
        }

        // 2. Update Moon
        const moonPos = positionsMap.get('moon');
        if (moonPos) {
            this.moon.update(moonPos.alt, moonPos.az, zoomFactor, daylightFade, currentFov, sunPos);
        }

        // 3. Update Planets
        this.planets.forEach((planet, id) => {
            const pos = positionsMap.get(id);
            if (pos) {
                planet.update(pos.alt, pos.az, zoomFactor, daylightFade, currentFov, sunPos);
            }
        });

        // 4. Update daylight label transitions
        const quantizedDayFactor = Math.round(dayFactor * 100) / 100;
        if (quantizedDayFactor !== this.lastDayFactor) {
            this.lastDayFactor = quantizedDayFactor;
            this.entities.forEach(e => e.updateDaylightLabel(quantizedDayFactor));
        }

        // 5. Sync localized entity names from catalog if loaded
        if (catalogStore.isLoaded) {
            this.entities.forEach((entity, id) => {
                const meta = catalogStore.planetaryData[id];
                if (meta && meta.name) {
                    entity.setName(meta.name);
                }
            });
        }

        // 6. Keep composite geometry positions updated
        this.syncCompositeGeometry();
    }

    /** Gets an entity by ID */
    public getEntityById(id: string): AbstractPlanetaryObject | undefined {
        return this.entities.get(id.toLowerCase());
    }

    /** Returns active 3D planet & moon meshes for raycast selection */
    public get3DMeshes(): THREE.Mesh[] {
        const meshes: THREE.Mesh[] = [];
        this.entities.forEach(entity => {
            meshes.push(...entity.get3DMeshes());
        });
        return meshes;
    }

    /** Returns all pickable raycast objects across all entities */
    public getRaycastObjects(): THREE.Object3D[] {
        const objects: THREE.Object3D[] = [];
        this.entities.forEach(entity => {
            objects.push(...entity.getRaycastObjects());
        });
        return objects;
    }

    /** Returns composite Points mesh for backward compatible selection raycasting */
    public getPointsMesh(): THREE.Points {
        return this.compositePointsMesh;
    }

    /** Gets planet ID by vertex index */
    public getIdByIndex(index: number): string | null {
        return this.planetIds[index] || null;
    }

    /** Gets vertex index by planet ID */
    public getIndexById(id: string): number | undefined {
        const index = this.planetIds.indexOf(id);
        return index !== -1 ? index : undefined;
    }

    /** Cleans up resources */
    public dispose(): void {
        this.entities.forEach(entity => entity.dispose());
        this.compositePointsMesh.geometry.dispose();
        (this.compositePointsMesh.material as THREE.Material).dispose();
        this.sunLight.dispose();
        this.ambientLight.dispose();
    }
}
