// src/lib/components/skyMap/entities/Planetary.ts

import * as THREE from 'three';
import { DOME_RADIUS, PLANET_SIZE_BASE, PLANET_COLORS, PLANET_VISUAL_SIZES } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';
import type { PositionUpdates } from '$lib/stores/skyEngine.svelte';

/**
 * Custom Vertex Shader
 * Adjusts the size of the planets based on the camera zoom and their normal size.
 */
const vertexShader = `
    attribute float size;
    attribute vec3 color;
    attribute float isSun; // 1.0 Sun, 0.0 others
    
    varying vec3 vColor;
    varying float vAlphaFactor; 
    varying float vIsSun;
    
    uniform float zoom;

    void main() {
        vColor = color;
        vIsSun = isSun;
        
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        float actualSize = size * zoom;

        gl_PointSize = max(2.5, actualSize);
        vAlphaFactor = min(1.0, actualSize / gl_PointSize);
        gl_Position = projectionMatrix * mvPosition;
    }
`;

/**
 * Custom Fragment Shader
 * With halo logic to the sun and planets.
 */
const fragmentShader = `
    varying vec3 vColor;
    varying float vAlphaFactor;
    varying float vIsSun;
    uniform float opacity;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist = length(coord);
        
        if (dist > 0.5) discard;

        float alpha = 0.0;
        vec3 finalColor = vec3(1.0);

        if (vIsSun > 0.5) {
            // === SUN ===
            
            float masterFade = smoothstep(0.5, 0.25, dist); 
            
            // 1. Light circle
            float coreBurn = exp(-pow(dist * 25.0, 2.0)) * 2.5; 
            float innerGlow = exp(-dist * 12.0) * 0.7;
            float outerGlow = exp(-dist * 5.0) * 0.35;
            float radialLight = (coreBurn + innerGlow + outerGlow) * masterFade;
            
            // 2. Diffraction sim
            float spikeX = exp(-abs(coord.x) * 100.0);
            float spikeY = exp(-abs(coord.y) * 100.0);
            float crossShape = max(spikeX, spikeY);
            
            // Start drawing them later
            float spikeStart = smoothstep(0.04, 0.15, dist);
            
            // Apply mask
            float spikes = crossShape * exp(-dist * 4.0) * 0.8 * masterFade * spikeStart;
            
            float totalLight = radialLight + spikes;
            
            vec3 sunTint = vec3(1.0, 0.95, 0.85); 
            finalColor = mix(sunTint, vec3(1.0), smoothstep(0.6, 1.5, totalLight));
            
            alpha = min(1.0, totalLight);
            
        } else {
            // === PLANETS ===
            
            float core = exp(-pow(dist * 12.0, 2.0)) * 1.5; 

            float halo = exp(-dist * 5.0) * 0.8;
            
            finalColor = mix(vColor, vec3(1.0), min(1.0, core * 1.2));
            
            alpha = (core + halo) * smoothstep(0.5, 0.2, dist);
        }

        gl_FragColor = vec4(finalColor, alpha * opacity * vAlphaFactor);
    }
`;
/**
 * Planetary Entity
 * Manages the rendering and updating of the planetary objects.
 */
export class Planetary {
    public group = new THREE.Group();
    private points: THREE.Points;
    private labels: THREE.Sprite[] = [];
    private planetIds: string[];

    constructor(opacity: number) {
        this.planetIds = Object.keys(catalogStore.planetaryData);
        
        // Geometry
        const geo = this.buildGeometry()

        const mat = new THREE.ShaderMaterial({
            uniforms: { zoom: { value: 1.0 }, opacity: { value: opacity } },
            vertexShader, 
            fragmentShader, 
            transparent: true, 
            blending: THREE.AdditiveBlending, 
            depthWrite: false,
            depthTest: false
        });

        this.points = new THREE.Points(geo, mat);
        this.points.renderOrder = 3;
        this.group.add(this.points);
    }

    /**
     * Constructs the initial geometry buffer for the planets.
     */
    private buildGeometry(): THREE.BufferGeometry {
        const num = this.planetIds.length;
        const positions = new Float32Array(num * 3);
        const colors = new Float32Array(num * 3);
        const sizes = new Float32Array(num);
        const isSunArray = new Float32Array(num); 
        const tmp = new THREE.Color();

        for (let i = 0; i < num; i++) {
            const id = this.planetIds[i];
            const lowerId = id.toLowerCase();
            
            let baseSize = PLANET_VISUAL_SIZES[lowerId] ?? PLANET_SIZE_BASE;
            let finalColorHex = PLANET_COLORS[lowerId] ?? 0xffffff;
            let isSun = 0.0;

            if (lowerId === 'sun') {
                isSun = 1.0;
                baseSize *= 3.8; 

                finalColorHex = 0xfffae6; 
            } else if (lowerId === 'moon') {
                baseSize *= 2.2;
            } else {
                baseSize *= 2.5; 
            }

            sizes[i] = baseSize;
            isSunArray[i] = isSun;

            tmp.setHex(finalColorHex);
            colors[i * 3]     = tmp.r;
            colors[i * 3 + 1] = tmp.g;
            colors[i * 3 + 2] = tmp.b;

            const planetData = catalogStore.planetaryData[id];
            const displayName = planetData?.name || lowerId;

            const sprite = this.createLabel(displayName, tmp.getHex());
            this.labels.push(sprite);
            this.group.add(sprite);
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3));
        geo.setAttribute('size',     new THREE.BufferAttribute(sizes, 1));
        geo.setAttribute('isSun',    new THREE.BufferAttribute(isSunArray, 1)); 
        geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), DOME_RADIUS);
        
        return geo;
    }

    /**
     * Creates a label for the planets.
     */
    private createLabel(name: string, color: number): THREE.Sprite {
        const canvas = document.createElement('canvas');
        canvas.width = 512; canvas.height = 128;
        const ctx = canvas.getContext('2d')!;
        
        ctx.font = '52px Inter, system-ui, sans-serif'; 
        
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        
        ctx.shadowColor = 'black';
        ctx.shadowBlur = 6;
        ctx.fillStyle = '#ffffff'; 
        
        ctx.fillText(name, 16, 100);

        const texture = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false, depthTest: false });
        const sprite = new THREE.Sprite(mat);
        
        sprite.scale.set(32, 8, 1); 
        sprite.renderOrder = 4
        return sprite;
    }

    getPointsMesh() {
        return this.points;
    }

    getIdByIndex(index: number): string | null {
        return this.planetIds[index] || null; 
    }
    
    getIndexById(id: string): number | undefined {
        const index = this.planetIds.indexOf(id); 
        return index !== -1 ? index : undefined;
    }

    /**
     * Updates the XYZ coordinates of all planets based on their current AltAz values.
     */
    update(positionsMap: PositionUpdates, zoomFactor: number) {
        (this.points.material as THREE.ShaderMaterial).uniforms.zoom.value = zoomFactor;
        const posArray = this.points.geometry.attributes.position.array as Float32Array;

        for (let i = 0; i < this.planetIds.length; i++) {
            const pId = this.planetIds[i];
            const p = positionsMap.get(pId);
            if (p) {
                altAzToXYZ(posArray, i, p.alt, p.az);
                
                if (this.labels[i]) {
                    const lowerId = pId.toLowerCase();
                    
                    // Anchor to control the position
                    let anchorX = 0.0;
                    let anchorY = 0.0;

                    if (lowerId === 'sun') {
                        anchorX = -0.65; // Right
                        anchorY = -1.55; // Up
                    } else if (lowerId === 'moon') {
                        anchorX = -0.25;
                        anchorY = -0.45;
                    } else {
                        anchorX = -0.075;
                        anchorY = -0.075;
                    }

                    this.labels[i].center.set(anchorX, anchorY);
                    
                    this.labels[i].position.set(posArray[i * 3], posArray[i * 3 + 1], posArray[i * 3 + 2]);
                }
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
        this.labels.forEach(l => { l.material.map?.dispose(); l.material.dispose(); });
    }
}