// src/lib/components/skyMap/entities/Sidereal.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';
import type { PositionUpdates } from '$lib/stores/skyEngine.svelte';

/**
 * Custom Vertex Shader
 * Adjusts the size of the stars based on the camera zoom and their magnitude.
 * If a star gets too small, it stops shrinking physically
 * and instead reduces its alpha (opacity) to simulate being fainter.
 */
const vertexShader = `
    attribute float size;
    attribute vec3 color;
    varying vec3 vColor;
    varying float vAlphaFactor; 
    uniform float zoom;

    void main() {
        vColor = color;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        
        float actualSize = size * zoom;

        // Minimum size of 2.5 for antialiasing
        gl_PointSize = max(2.5, actualSize);
        
        // Smaller real size than drawn, lower the intensity to compensate size
        vAlphaFactor = min(1.0, actualSize / gl_PointSize);

        gl_Position = projectionMatrix * mvPosition;
    }
`;

/**
 * Custom Fragment Shader
 * Converts the default square point into a smooth, circular dot.
 */
const fragmentShader = `
    varying vec3 vColor;
    varying float vAlphaFactor;
    uniform float opacity;

    void main() {
        // gl_PointCoord from 0.0 to 1.0 inside the point
        float dist = distance(gl_PointCoord, vec2(0.5));
        
        // Create a circle
        float alpha = smoothstep(0.5, 0.1, dist);
        
        // Scale factor for smaller stars
        gl_FragColor = vec4(vColor, alpha * opacity * vAlphaFactor);
    }
`;

/**
 * Sidereal Entity
 * Manages the rendering and updating of the background stars/DSO
 */
export class Sidereal {
    public group = new THREE.Group();
    private points: THREE.Points;
    private starIds: string[];

    constructor(opacity: number) {
        this.starIds = Object.keys(catalogStore.siderealData);
        
        const geo = this.buildGeometry();

        // Use ShaderMaterial to handle the custom scaling and circular rendering
        const mat = new THREE.ShaderMaterial({
            uniforms: { zoom: { value: 1.0 }, opacity: { value: opacity } },
            vertexShader, 
            fragmentShader, 
            transparent: true, 
            blending: THREE.AdditiveBlending, 
            depthWrite: false
        });

        this.points = new THREE.Points(geo, mat);
        this.group.add(this.points);
    }

    /**
     * Constructs the initial geometry buffer for the stars.
     * Calculates base sizes depending on the star's magnitude.
     */
    private buildGeometry(): THREE.BufferGeometry {
        const num = this.starIds.length;
        const positions = new Float32Array(num * 3);
        const sizes = new Float32Array(num);
        const colors = new Float32Array(num * 3);

        for (let i = 0; i < num; i++) {
            const id = this.starIds[i];
            const data = catalogStore.siderealData[id];
            
            const mag = (data && typeof data.mag === 'number') ? data.mag : 6.0;
            sizes[i] = Math.max(0.8, (7.0 - mag) * 0.8);

            // White colour 
            colors[i * 3] = 1.0; 
            colors[i * 3 + 1] = 1.0; 
            colors[i * 3 + 2] = 1.0;
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), DOME_RADIUS);
        
        return geo;
    }

    getPointsMesh() {
        return this.points;
    }

    getIdByIndex(index: number): string | null {
        return this.starIds[index] || null; 
    }
    
    /**
     * Updates the XYZ coordinates of all stars based on their current AltAz values.
     * Called continuously inside the render loop.
     */
    update(positionsMap: PositionUpdates, zoomFactor: number) {
        // Update the shader uniform for zoom scaling
        (this.points.material as THREE.ShaderMaterial).uniforms.zoom.value = zoomFactor;
        const posArray = this.points.geometry.attributes.position.array as Float32Array;

        for (let i = 0; i < this.starIds.length; i++) {
            const id = this.starIds[i];
            const p = positionsMap.get(id);

            if (p) {
                altAzToXYZ(posArray, i, p.alt, p.az);
            }
        }
        this.points.geometry.attributes.position.needsUpdate = true;
    }

    /**
     * Disposes of geometries and materials to prevent memory leaks.
     */
    dispose() {
        this.points.geometry.dispose();
        (this.points.material as THREE.Material).dispose();
    }
}