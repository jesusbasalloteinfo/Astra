// src/lib/components/skyMap/entities/Constellations.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

/**
 * Constellations Entity
 * 
 * Manages the rendering of constellation lines 
 */
export class Constellations {
    public group = new THREE.Group();
    private lines: THREE.LineSegments;

    // Stores a flattened list of star IDs where every two sequential IDs form a line segment.
    private constellationPairs: string[] = [];

    constructor(color: number, opacity: number) {
        const geo = this.buildGeometry();

        const mat = new THREE.LineBasicMaterial({
            color: color,
            transparent: true,
            opacity: opacity,
            depthWrite: false 
        });

        this.lines = new THREE.LineSegments(geo, mat);
        this.group.add(this.lines);
    }

    /**
     * Parses the constellation catalog data to determine which stars connect to which.
     * Allocates the necessary memory buffer for the vertex positions.
     */
    private buildGeometry(): THREE.BufferGeometry {
        const pairs: string[] = [];

        // Iterate through the catalog to build the connections
        catalogStore.constellations.forEach(constel => {
            constel.lines_indices.forEach(([idxA, idxB]) => {
                const starIdA = constel.stars_ids[idxA];
                const starIdB = constel.stars_ids[idxB];
                
                // Both stars exist in the catalog, add them as a pair
                if (starIdA && starIdB) {
                    pairs.push(starIdA, starIdB);
                }
            });
        });

        this.constellationPairs = pairs; 

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pairs.length * 3), 3));
        geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), DOME_RADIUS);
        
        return geo;
    }

    /**
     * Updates the XYZ coordinates of the line segments based on the current positions of the stars.
     * Called continuously inside the render loop.
     */
    update(positionsMap: Map<string, { alt: number, az: number }>) {
        if (this.constellationPairs.length === 0) return;

        const posArray = this.lines.geometry.attributes.position.array as Float32Array;

        for (let i = 0; i < this.constellationPairs.length; i++) {
            const starId = this.constellationPairs[i];
            const p = positionsMap.get(starId);
            
            if (p) {
                altAzToXYZ(posArray, i, p.alt, p.az);
            } else {
                // If fails, hide the line
                posArray[i * 3] = 0; 
                posArray[i * 3 + 1] = 0; 
                posArray[i * 3 + 2] = 0;
            }
        }
        this.lines.geometry.attributes.position.needsUpdate = true;
    }

    /**
     * Dynamically updates the visual properties (visibility, color, opacity).
     */
    setProps(visible: boolean, color: number, opacity: number) {
        if (visible !== undefined) {
            this.group.visible = visible;
        }

        if (color !== undefined) {
            (this.lines.material as THREE.LineBasicMaterial).color.setHex(color);
        }

        if (opacity !== undefined) {
            (this.lines.material as THREE.LineBasicMaterial).opacity = opacity;
        }
    }

    /**
     * Disposes of geometries and materials to prevent memory leaks.
     */
    dispose() {
        this.lines.geometry.dispose();
        (this.lines.material as THREE.Material).dispose();
    }
}