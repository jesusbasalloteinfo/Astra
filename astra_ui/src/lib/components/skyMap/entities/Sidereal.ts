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
    attribute float isDso; // 0.0 - stars, 1.0 - DSO

    varying vec3 vColor;
    varying float vAlphaFactor; 
    varying float vIsDso;

    uniform float zoom;

    void main() {
        vColor = color;
        vIsDso = isDso;

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
    varying float vIsDso;
    uniform float opacity;

    void main() {
        // gl_PointCoord from 0.0 to 1.0 inside the point
        float dist = distance(gl_PointCoord, vec2(0.5));
        float alpha = 0.0;

        // Create a circle
        if (vIsDso > 0.5) {
            // DSOs  -> Smoother border
            alpha = smoothstep(0.5, 0.0, dist);
        } else {
            // Stars -> Solid center with a smoothed border
            alpha = smoothstep(0.5, 0.1, dist);
        }
        
        // Scale factor for smaller stars
        gl_FragColor = vec4(vColor, alpha * opacity * vAlphaFactor);
    }
`;


/**
 * Convert B-V temperature index to an RGB color
 */
function bvToRGB(bv: number): THREE.Color {
    if (bv < -0.4) return new THREE.Color(0xcddcff); // Light blue
    if (bv < 0.0) return new THREE.Color(0xe2ebff);  // Pale bluish white
    if (bv < 0.4) return new THREE.Color(0xffffff);  // White
    if (bv < 0.8) return new THREE.Color(0xfffaed);  // Pale yellowish white
    if (bv < 1.2) return new THREE.Color(0xffe6cc);  // Pale orange
    return new THREE.Color(0xffd2a8);                // Pale red
}

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
        const isDsoArray = new Float32Array(num); 
        const starTags = ['star', 'double_star', 'star_system', 'asterism'];

        for (let i = 0; i < num; i++) {
            const id = this.starIds[i];
            const data = catalogStore.siderealData[id];
            
            const mag = (data && typeof data.mag === 'number') ? data.mag : 6.0;
            const category = data?.category || 'unknown';
            
            let finalColor = new THREE.Color(0xffffff);
            let sizeMultiplier = 1.0;
            let isDsoFlag = 0.0;

            if (starTags.includes(category)) {
                // Stars: B-V color if we have it
                if (typeof data.b_v === 'number') {
                    finalColor = bvToRGB(data.b_v);
                }
            } else if (category !== 'unknown') {
                // DSOs: Smoother and bigger
                isDsoFlag = 1.0;
                sizeMultiplier = 2.0; 

                // Slight tints over white to give some variety
                if (['galaxy', 'galactic_cluster'].includes(category)) {
                    finalColor.setHex(0xf0f4ff); // Blue tints
                } else if (['nebula', 'planetary_nebula', 'molecular_cloud', 'supernova_remnant'].includes(category)) {
                    finalColor.setHex(0xfff0f5); // Magenta tints
                } else if (['open_cluster', 'globular_cluster'].includes(category)) {
                    finalColor.setHex(0xfffbee); // Warm tints
                }
            }

            // Size to be applied
            sizes[i] = Math.max(0.8, (7.0 - mag) * 0.8) * sizeMultiplier;

            colors[i * 3] = finalColor.r; 
            colors[i * 3 + 1] = finalColor.g; 
            colors[i * 3 + 2] = finalColor.b;
            
            isDsoArray[i] = isDsoFlag;
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geo.setAttribute('isDso', new THREE.BufferAttribute(isDsoArray, 1));
        geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), DOME_RADIUS);
        
        return geo;
    }

    getPointsMesh() {
        return this.points;
    }

    getIdByIndex(index: number): string | null {
        return this.starIds[index] || null; 
    }
    
    getIndexById(id: string): number | undefined {
        const index = this.starIds.indexOf(id); 
        return index !== -1 ? index : undefined;
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