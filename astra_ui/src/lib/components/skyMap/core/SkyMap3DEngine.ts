// src/lib/components/skyMap/core/SkyMap3DEngine.ts

import * as THREE from 'three';
import { CameraController } from './CameraController';
import { SelectionController } from './SelectionController';
import { Environment } from '../entities/Environment';
import { Planetary } from '../entities/Planetary';
import { Sidereal } from '../entities/Sidereal';
import { Constellations } from '../entities/Constellations';
import { FOV_DEFAULT } from '../utils/const';
import { skyEngine } from '$lib/stores/skyEngine.svelte';
import { TargetReticle } from '../entities/TargetReticle';

/**
 * SkyMap3DEngine
 * 
 * The main orchestrator for the 3D sky map. It initializes the Three.js scene,
 * manages the renderer, sets up the camera controller, and coordinates the 
 * updates for all astronomical entities (stars, planets, constellations, etc.).
 */
export class SkyMap3DEngine {
    // Core Three.js components
    private scene: THREE.Scene;
    private renderer: THREE.WebGLRenderer;
    private resizeObserver: ResizeObserver; 
    private animationId: number = 0;

    // Controllers
    private cameraCtrl: CameraController;
    private selectionCtrl: SelectionController;
    
    // Scene entities
    private environment: Environment;
    private planetary: Planetary;
    private sidereal: Sidereal;
    private constellations: Constellations;
    private targetReticle:TargetReticle;

    constructor(private container: HTMLDivElement, props: any) {
        // Initialize Scene & Renderer
        this.scene = new THREE.Scene();
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

        // Optimize pixel ratio for high-DPI displays
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(this.renderer.domElement);

        // Instantiate Entities
        this.environment = new Environment(props.groundColor, props.cardinalColor);
        this.planetary = new Planetary(props.starOpacity);
        this.sidereal = new Sidereal(props.starOpacity);
        this.constellations = new Constellations(props.constellationColor, props.constellationOpacity);
        this.targetReticle = new TargetReticle();   
        
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

        // Apply initial visual properties
        this.updateProps(props); 

        this.resizeObserver = new ResizeObserver((entries) => {
            for (const entry of entries) {
                // Le pasamos el ancho y alto real del div al hacer resize
                const { width, height } = entry.contentRect;
                if (width > 0 && height > 0) {
                    this.onResize(width, height);
                }
            }
        });
        // Ponemos al observador a vigilar tu div contenedor
        this.resizeObserver.observe(this.container);
        this.animate();
    }
    
    /**
     * Main animation loop.
     * Updates entity positions based on the current time/location store
     * and renders the frame.
     */
    private animate = () => {
        this.animationId = requestAnimationFrame(this.animate);
        
        if (skyEngine.positions && skyEngine.positions.size > 0) {
            // New data update and new zoom

            const zoomFactor = FOV_DEFAULT / this.cameraCtrl.camera.fov;
            
            this.planetary.update(skyEngine.positions, zoomFactor);
            this.sidereal.update(skyEngine.positions, zoomFactor);
            this.constellations.update(skyEngine.positions);
            this.targetReticle.update(skyEngine.positions);
        }

        // Update camera damping/controls and render the scene
        this.cameraCtrl.update();
        this.renderer.render(this.scene, this.cameraCtrl.camera);
    };

    /**
     * Updates the visual properties of the scene entities.
     * Called directly by Svelte when props change.
     */
    updateProps(props: any) {
        if (props.showGround !== undefined) this.environment.setGroundVisible(props.showGround);
        if (props.groundColor !== undefined) this.environment.setGroundColor(props.groundColor);
        
        if (this.constellations && props.showConstellations !== undefined) {
            console.log("show Constellations:", props.showConstellations)
            this.constellations.setProps(
                props.showConstellations, 
                props.constellationColor, 
                props.constellationOpacity
            );
        }
    }
    
    /**
     * Commands the camera controller to fly towards specific celestial coordinates.
     */
    flyTo(alt: number, az: number, setReticle:boolean =false) {
        this.cameraCtrl.flyTo(alt, az);
    }

    /**
     * Programmatically selects an object, turns on the reticle, and flies to it.
     */
    selectObject(id: string) {
        this.selectionCtrl.selectById(id);
    }

    /**
     * Handles browser window resizing to maintain correct aspect ratio.
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

        this.resizeObserver.disconnect();
        

        this.renderer.dispose();
        if (this.container.contains(this.renderer.domElement)) {
            this.container.removeChild(this.renderer.domElement);
        }
    }
}