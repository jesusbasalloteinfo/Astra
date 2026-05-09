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
    attribute float shapeType; // 0.0: star 1.0: Fuzz (Cluster/Neb), 2.0: Elipse (Galaxy)
    attribute float angle;     // Rotation in radians for galaxies

    varying vec3 vColor;
    varying float vAlphaFactor; 
    varying float vShapeType;
    varying float vAngle;

    uniform float zoom;

    void main() {
        vColor = color;
        vShapeType = shapeType;
        vAngle = angle;

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
    varying float vShapeType;
    varying float vAngle;
    uniform float opacity;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);

        if (vShapeType > 1.5) {
            float s = sin(vAngle);
            float c = cos(vAngle);
            mat2 rot = mat2(c, -s, s, c);
            coord = rot * coord;
            
            coord.y *= 1.5; 
        }

        float dist = length(coord);
        float alpha = 0.0;
        
        if (vShapeType > 0.5) {
            // Gaussian center
            alpha = exp(-pow(dist * 3.5, 2.0));
            
            alpha *= smoothstep(0.5, 0.3, dist);
            
        } else {
            alpha = smoothstep(0.5, 0.1, dist);
            if (dist > 0.5) discard;
        }
        
        float dsoDimmer = vShapeType > 0.5 ? 0.8 : 1.0;
        
        gl_FragColor = vec4(vColor, alpha * opacity * vAlphaFactor * dsoDimmer);
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
        
        const shapeTypes = new Float32Array(num);
        const angles = new Float32Array(num);

        const starTags = ['star', 'double_star', 'star_system', 'asterism'];

        for (let i = 0; i < num; i++) {
            const id = this.starIds[i];
            const data = catalogStore.siderealData[id];
            
            const mag = (data && typeof data.mag === 'number') ? data.mag : 6.0;
            const category = data?.category || 'unknown';
            
            let finalColor = new THREE.Color(0xffffff);
            let finalSize = 1.0;
            let shape = 0.0;
            let angle = 0.0;

            if (starTags.includes(category)) {
                // 1. Stars
                shape = 0.0;
                finalSize = Math.max(0.8, (7.0 - mag) * 0.8);
                if (typeof data.b_v === 'number') finalColor = bvToRGB(data.b_v);

            } else if (category !== 'unknown') {
                // 2. DSOs
                const arcmin = data.size_arcmin || 1.0; 
                
                // Bigger size
                finalSize = Math.min(12.0, Math.max(1.5, Math.sqrt(arcmin) * 1.2));

                if (mag > 6.0) {
                    finalSize *= 0.6;
                }

                // Slight tints over white to give some variety
                if (['galaxy'].includes(category)) {
                    shape = 2.0; 
                    angle = (i * 0.384) % Math.PI; 
                    finalColor.setHex(0xf0f4ff); // Blue tints
                } else {
                    shape = 1.0; 
                    if (['nebula', 'planetary_nebula', 'molecular_cloud', 'supernova_remnant'].includes(category)) {
                        finalColor.setHex(0xfff0f5); // Magenta tints
                    } else if (['open_cluster', 'globular_cluster', 'galactic_cluster'].includes(category)) {
                        finalColor.setHex(0xfffbee); // Warm tints
                    }
                }
            }

            sizes[i] = finalSize;
            shapeTypes[i] = shape;
            angles[i] = angle;

            colors[i * 3] = finalColor.r; 
            colors[i * 3 + 1] = finalColor.g; 
            colors[i * 3 + 2] = finalColor.b;
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geo.setAttribute('shapeType', new THREE.BufferAttribute(shapeTypes, 1));
        geo.setAttribute('angle', new THREE.BufferAttribute(angles, 1));
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