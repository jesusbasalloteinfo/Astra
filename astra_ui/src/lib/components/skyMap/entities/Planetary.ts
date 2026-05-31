// src/lib/components/skyMap/entities/Planetary.ts

import * as THREE from 'three';
import { DOME_RADIUS, PLANET_SIZE_BASE, PLANET_COLORS, PLANET_VISUAL_SIZES } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';
import type { PositionUpdates } from '$lib/stores/skyEngine.svelte';

/**
 * Custom Vertex Shader for Planetary entities.
 * Adjusts the size of the planets based on the camera zoom and their base size.
 */
const vertexShader = `
    attribute float size;
    attribute vec3 color;
    attribute float isSun; // 0.0 planets, 1.0 sun, 2.0 moon
    
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
 * Custom Fragment Shader for Planetary entities.
 * Implements specific halo and diffraction effects for the Sun, Moon, and planets.
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

        if (vIsSun > 0.5 && vIsSun < 1.5) {
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
            
        } else if (vIsSun > 1.5) {
            // === MOON ===
            
            float core = exp(-pow(dist * 12.0, 2.0)) * 1.5; 
            float halo = exp(-dist * 5.0) * 0.4;
            
            vec3 moonColor = vec3(1.0, 0.98, 0.92); 
            finalColor = mix(moonColor, vec3(1.0), min(1.0, core * 1.2));
            
            alpha = (core + halo) * smoothstep(0.5, 0.2, dist);
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
 * 
 * Manages the rendering and updating of solar system objects (Sun, Moon, and Planets).
 * Uses custom shaders for realistic visual representation and handles labels.
 */
export class Planetary {
    /** Container for the planets mesh and their labels. */
    public group = new THREE.Group();
    /** The Points mesh containing all planetary objects. */
    private points: THREE.Points;
    /** Array of label objects for the planets. */
    private labels: { sprite: THREE.Sprite, ctx: CanvasRenderingContext2D, texture: THREE.CanvasTexture, name: string }[] = [];
    /** List of IDs for the planets currently being managed. */
    private planetIds: string[];
    /** Factor used to track daylight changes for optimization. */
    private lastDayFactor: number = -1;

    /**
     * Creates an instance of Planetary.
     * @param {number} opacity - Initial opacity for the planetary objects.
     */
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
            depthTest: true
        });

        this.points = new THREE.Points(geo, mat);
        this.points.renderOrder = 2;
        this.group.add(this.points);
    }

    /**
     * Constructs the initial geometry buffer for the planets.
     * @returns {THREE.BufferGeometry} The generated geometry.
     * @private
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
                isSun = 2.0; 
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

            const labelObj = this.createLabel(displayName);
            this.labels.push(labelObj);
            this.group.add(labelObj.sprite);
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
     * Creates a text label sprite for a planet.
     * @param {string} name - The name of the planet to display.
     * @returns {{ sprite: THREE.Sprite, ctx: CanvasRenderingContext2D, texture: THREE.CanvasTexture, name: string }} Label resources.
     * @private
     */
    private createLabel(name: string): { sprite: THREE.Sprite, ctx: CanvasRenderingContext2D, texture: THREE.CanvasTexture, name: string } {
        const canvas = document.createElement('canvas');
        canvas.width = 512; canvas.height = 128;
        const ctx = canvas.getContext('2d')!;
        const texture = new THREE.CanvasTexture(canvas);
        
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false, depthTest: true });
        const sprite = new THREE.Sprite(mat);
        
        sprite.scale.set(32, 8, 1); 
        sprite.renderOrder = 3;

        const labelObj = { sprite, ctx, texture, name };
        this.updateLabelText(labelObj, 0xffffff); 
        
        return labelObj;
    }

    /**
     * Redraws the text on the label's canvas.
     * @param {{ sprite: THREE.Sprite, ctx: CanvasRenderingContext2D, texture: THREE.CanvasTexture, name: string }} label - Label object.
     * @param {number} color - Hex color for the text.
     * @private
     */
    private updateLabelText(label: { sprite: THREE.Sprite, ctx: CanvasRenderingContext2D, texture: THREE.CanvasTexture, name: string }, color: number) {
        const { ctx, texture, name } = label;
        ctx.clearRect(0, 0, 512, 128);
        
        ctx.font = '64px Inter, system-ui, sans-serif'; 
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        
        ctx.fillStyle = `#${new THREE.Color(color).getHexString()}`;
        
        ctx.fillText(name.toUpperCase(), 16, 100);
        texture.needsUpdate = true;
    }

    /**
     * Returns the Points mesh used for rendering.
     * @returns {THREE.Points}
     */
    getPointsMesh() {
        return this.points;
    }

    /**
     * Gets the planet ID corresponding to a vertex index.
     * @param {number} index - The vertex index in the Points mesh.
     * @returns {string | null} The planet ID or null if not found.
     */
    getIdByIndex(index: number): string | null {
        return this.planetIds[index] || null; 
    }
    
    /**
     * Gets the vertex index for a given planet ID.
     * @param {string} id - The planet ID.
     * @returns {number | undefined} The vertex index or undefined if not found.
     */
    getIndexById(id: string): number | undefined {
        const index = this.planetIds.indexOf(id); 
        return index !== -1 ? index : undefined;
    }

    /**
     * Updates the position and visual state of all planets.
     * @param {PositionUpdates} positionsMap - Map containing the current Alt/Az positions.
     * @param {number} zoomFactor - Current camera zoom factor.
     * @param {number} [daylightFade=1.0] - Fade factor for daytime (1.0 = night, 0.0 = day).
     */
    update(positionsMap: PositionUpdates, zoomFactor: number, daylightFade: number = 1.0) {
        (this.points.material as THREE.ShaderMaterial).uniforms.zoom.value = zoomFactor;
        const posArray = this.points.geometry.attributes.position.array as Float32Array;

        const dayFactor = 1.0 - daylightFade; // 0 (night) to 1 (day)
        const quantizedDayFactor = Math.round(dayFactor * 100) / 100;

        if (quantizedDayFactor !== this.lastDayFactor) {
            this.lastDayFactor = quantizedDayFactor;

            const labelC = new THREE.Color(0xffffff);
            if (quantizedDayFactor > 0) {

                const daytimeBlue = new THREE.Color().setHSL(0.64, 1.0, 0.05);
                labelC.lerp(daytimeBlue, quantizedDayFactor);
            }
            const colorNum = labelC.getHex();
            this.labels.forEach(l => this.updateLabelText(l, colorNum));
        }

        for (let i = 0; i < this.planetIds.length; i++) {
            const pId = this.planetIds[i];
            const p = positionsMap.get(pId);
            if (p) {
                altAzToXYZ(posArray, i, p.alt, p.az);
                
                if (this.labels[i]) {
                    const sprite = this.labels[i].sprite;
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

                    sprite.center.set(anchorX, anchorY);
                    sprite.position.set(posArray[i * 3], posArray[i * 3 + 1], posArray[i * 3 + 2]);
                }
            }
        }
        this.points.geometry.attributes.position.needsUpdate = true;
    }
    

    /**
     * Cleans up Three.js resources used by planetary entities.
     */
    dispose() {
        this.points.geometry.dispose();
        (this.points.material as THREE.Material).dispose();
        this.labels.forEach(l => { 
            l.texture.dispose(); 
            l.sprite.material.dispose(); 
        });
    }
}