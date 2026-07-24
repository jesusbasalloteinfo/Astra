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

// src/lib/components/skyMap/core/SkyMap3DEngine.ts

import * as THREE from 'three';
import { CameraController } from './CameraController';
import { SelectionController } from './SelectionController';
import { Environment } from '../entities/Environment';
import { Planetary } from '../entities/Planetary';
import { Sidereal } from '../entities/Sidereal';
import { Constellations } from '../entities/Constellations';
import { FOV_DEFAULT, DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { skyEngine } from '$lib/stores/skyEngine.svelte';
import { TargetReticle } from '../entities/TargetReticle';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';
import { TelescopePointer } from '../entities/TelescopePointer';

/**
 * SkyMap3DEngine
 * 
 * The main orchestrator for the 3D sky map. It initializes the Three.js scene,
 * manages the renderer, sets up the camera controller, and coordinates the 
 * updates for all astronomical entities (stars, planets, constellations, etc.).
 */
export class SkyMap3DEngine {
    /** The main Three.js scene. */
    private scene: THREE.Scene;
    /** The WebGL renderer. */
    private renderer: THREE.WebGLRenderer;
    /** Observer to handle container resizing. */
    private resizeObserver: ResizeObserver; 
    /** ID of the current requestAnimationFrame. */
    private animationId: number = 0;

    /** Controller for camera movement and zooming. */
    private cameraCtrl: CameraController;
    /** Controller for object selection and raycasting. */
    private selectionCtrl: SelectionController;
    
    /** Ground, horizon, and atmospheric effects. */
    private environment: Environment;
    /** Planetary objects (Sun, Moon, Planets). */
    private planetary: Planetary;
    /** Sidereal objects (Stars, Deep Sky Objects). */
    private sidereal: Sidereal;
    /** Constellation lines and labels. */
    private constellations: Constellations;
    /** Visual reticle for the selected object. */
    private targetReticle:TargetReticle;
    /** Visual pointer for the telescope's current position. */
    private telescopePointer: TelescopePointer;
    /** Current color used for cardinal direction labels. */
    private currentCardinalColor: string;

    /**
     * Creates an instance of SkyMap3DEngine.
     * @param {HTMLDivElement} container - The HTML element to mount the renderer.
     * @param {any} props - Initial configuration properties.
     */
    constructor(private container: HTMLDivElement, props: any) {
        this.currentCardinalColor = props.cardinalColor;
        // Initialize Scene & Renderer
        this.scene = new THREE.Scene();
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

        // Optimize pixel ratio for high-DPI displays
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(this.renderer.domElement);

        // Instantiate Entities
        this.environment = new Environment(props.groundColor, props.cardinalColor, props.cardinalLabels);
        this.planetary = new Planetary(props.starOpacity);
        this.sidereal = new Sidereal(props.starOpacity);
        this.constellations = new Constellations(
            props.constellationColor, 
            props.constellationLabelColor,
            props.constellationOpacity,
            props.showConstellationLabels,
            props.useLatinConstellations
        );
        this.targetReticle = new TargetReticle();  
        this.telescopePointer = new TelescopePointer(); 
        
        // Initialize Controllers
        this.cameraCtrl = new CameraController(container);
        this.selectionCtrl = new SelectionController(
            this.container, 
            this.cameraCtrl, 
            this.planetary, 
            this.sidereal, 
            this.targetReticle
        );

        // Add entities to the scene
        this.scene.add(this.environment.group);
        this.scene.add(this.sidereal.group);
        this.scene.add(this.planetary.group);
        this.scene.add(this.constellations.group);
        this.scene.add(this.targetReticle.sprite);
        this.scene.add(this.telescopePointer.sprite);

        this.targetReticle.sprite.renderOrder = 5;
        this.telescopePointer.sprite.renderOrder = 6;

        // Apply initial visual properties
        this.updateProps(props); 

        this.resizeObserver = new ResizeObserver((entries) => {
            for (const entry of entries) {
                const { width, height } = entry.contentRect;
                if (width > 0 && height > 0) {
                    this.onResize(width, height);
                }
            }
        });
        this.resizeObserver.observe(this.container);
        this.animate();
    }
    
    /**
     * Main animation loop.
     * Updates entity positions based on the current time/location store
     * and renders the frame.
     * @private
     */
    private animate = () => {
        this.animationId = requestAnimationFrame(this.animate);
        
        if (skyEngine.positions && skyEngine.positions.size > 0) {
            // New data update and new zoom

            const zoomFactor = FOV_DEFAULT / this.cameraCtrl.camera.fov;

            let daylightFade = 1.0; // Night time as default

            const sunPos = skyEngine.positions.get('sun');
            const moonPos = skyEngine.positions.get('moon');

            if (sunPos) {
                // 1. Update sky
                this.environment.updateSunPosition(sunPos.alt, sunPos.az);
                
                // 2. Calculate star visibility
                const tmp = new Float32Array(3);
                altAzToXYZ(tmp, 0, sunPos.alt, sunPos.az);
                const sunYNorm = tmp[1] / DOME_RADIUS; 
                
                // Smooth transition
                let fade = (sunYNorm + 0.05) / 0.15; 
                fade = Math.max(0.0, Math.min(1.0, fade)); 
                
                // Hide in daytime
                daylightFade = this.environment.isAtmosphereEnabled() ? (1.0 - fade) : 1.0;
            }
            
            this.planetary.update(skyEngine.positions, zoomFactor, daylightFade, this.cameraCtrl.camera.fov);
            this.sidereal.update(skyEngine.positions, zoomFactor, daylightFade);
            this.environment.updateDaylight(daylightFade);
            this.constellations.update(skyEngine.positions, daylightFade);
            this.targetReticle.update(skyEngine.positions);
            this.telescopePointer.update();

            if (this.cameraCtrl.isTracking && this.selectionCtrl.selectedId) {
                const pos = skyEngine.positions.get(this.selectionCtrl.selectedId);
                if (pos) {
                    this.cameraCtrl.track(pos.alt, pos.az);
                }
            }
        }

        // Update camera damping/controls and render the scene
        this.cameraCtrl.update();
        this.renderer.render(this.scene, this.cameraCtrl.camera);
    };

    /**
     * Updates the visual properties of the scene entities.
     * Called directly by Svelte when props change.
     * @param {any} props - Updated configuration properties.
     */
    updateProps(props: any) {
        if (props.showGround !== undefined) this.environment.setGroundVisible(props.showGround);
        if (props.solidGround !== undefined) this.environment.setGroundMode(props.solidGround);
        if (props.groundColor !== undefined) this.environment.setGroundColor(props.groundColor);
        
        if (props.cardinalColor !== undefined) {
            this.currentCardinalColor = props.cardinalColor;
        }

        if (props.cardinalColor !== undefined || props.cardinalLabels !== undefined) {
            this.environment.updateCardinalLabels(
                this.currentCardinalColor, 
                props.cardinalLabels
            );
        }
        
        if (props.showAtmosphere !== undefined) this.environment.setAtmosphereEnabled(props.showAtmosphere);
        
        if (this.constellations && props.showConstellations !== undefined) {
            this.constellations.setProps(
                props.showConstellations, 
                props.constellationColor, 
                props.constellationLabelColor, 
                props.constellationOpacity,
                props.showConstellationLabels, 
                props.useLatinConstellations   
            );
        }
    }
    
    /**
     * Commands the camera controller to fly towards specific celestial coordinates.
     * @param {number} alt - Target altitude in degrees.
     * @param {number} az - Target azimuth in degrees.
     * @param {boolean} [setReticle=false] - Whether to show the reticle.
     */
    flyTo(alt: number, az: number, setReticle:boolean =false) {
        this.cameraCtrl.flyTo(alt, az);
    }
    
    /**
     * Calculates a constellation centroid and flies the camera to that constellation.
     * @param {string} abbr - The abbreviation of the constellation (e.g., 'Ori').
     */
    flyToConstellation(abbr: string) {
        const constel = catalogStore.constellations.find(c => c.abbr === abbr);
        if (!constel || constel.stars_ids.length === 0) return;

        let sumX = 0, sumY = 0, sumAlt = 0;
        let count = 0;

        let isDegrees = false;

        for (const starId of constel.stars_ids) {
            const p = skyEngine.positions.get(starId);
            if (p) {
                if (Math.abs(p.az) > Math.PI * 2) isDegrees = true;

                // To radians
                const azRad = isDegrees ? p.az * (Math.PI / 180) : p.az;
                
                sumX += Math.cos(azRad);
                sumY += Math.sin(azRad);
                
                sumAlt += p.alt;
                count++;
            }
        }

        if (count > 0) {
            // Altitude mean
            const avgAlt = sumAlt / count;
            
            // Azimut circular mean
            let avgAzRad = Math.atan2(sumY, sumX);
            if (avgAzRad < 0) avgAzRad += Math.PI * 2;

            // In degrees
            const finalAz = isDegrees ? avgAzRad * (180 / Math.PI) : avgAzRad;
            
            this.clearSelection();
            
            this.cameraCtrl.flyTo(avgAlt, finalAz);
        }
    }
    
    /**
     * Recenters the camera on the currently selected object.
     */
    recenterSelected() {
        if (this.selectionCtrl.selectedId) {
            this.selectionCtrl.selectById(this.selectionCtrl.selectedId);
        }
    }

    /**
     * Sets the telescope pointer inside the sky map.
     * @param {number | null} alt - Telescope altitude.
     * @param {number | null} az - Telescope azimuth.
     */
    setTelescopePosition(alt: number | null, az: number | null) {
        if (alt !== null && az !== null) {
            this.telescopePointer.updatePosition(alt, az);
        } else {
            this.telescopePointer.hide();
        }
    }

    /**
     * Programmatically selects an object, turns on the reticle, and flies to it.
     * @param {string} id - The ID of the object to select.
     */
    selectObject(id: string) {
        this.selectionCtrl.selectById(id);
    }

    /**
     * Clears the current selection and hides the reticle.
     */
    clearSelection() {
        this.selectionCtrl.clearSelection();
    }

    /**
     * Handles browser window resizing to maintain correct aspect ratio.
     * @param {number} width - New container width.
     * @param {number} height - New container height.
     * @private
     */
    private onResize = (width: number, height: number) => {
        this.cameraCtrl.resize(width, height);
        this.renderer.setSize(width, height);
    };

    /**
     * Cleans up all Three.js resources to prevent memory leaks when the component is destroyed.
     */
    dispose() {
        cancelAnimationFrame(this.animationId);
        this.cameraCtrl.dispose();
        this.selectionCtrl.dispose()
        this.environment.dispose();
        this.planetary.dispose();
        this.sidereal.dispose();
        this.constellations.dispose();
        this.targetReticle.dispose();
        this.telescopePointer.dispose();

        this.resizeObserver.disconnect();
        

        this.renderer.dispose();
        if (this.container.contains(this.renderer.domElement)) {
            this.container.removeChild(this.renderer.domElement);
        }
    }
}