// src/lib/components/skyMap/entities/Planetary.ts

import * as THREE from 'three';
import { DOME_RADIUS, PLANET_SIZE_BASE, PLANET_COLORS, PLANET_VISUAL_SIZES } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

/**
 * Custom Vertex Shader
 * Adjusts the size of the planets based on the camera zoom and their normal size.
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
 * Converts the default square point into a smooth, circular dot using gl_PointCoord.
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
            vertexShader, fragmentShader, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
        });

        this.points = new THREE.Points(geo, mat);
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
        const tmp = new THREE.Color();

        for (let i = 0; i < num; i++) {
            const id = this.planetIds[i].toLowerCase();
        
            
            sizes[i] = PLANET_VISUAL_SIZES[id] ?? PLANET_SIZE_BASE;

            tmp.setHex(PLANET_COLORS[id] ?? 0xffffff);
            colors[i * 3]     = tmp.r;
            colors[i * 3 + 1] = tmp.g;
            colors[i * 3 + 2] = tmp.b;

            const sprite = this.createLabel(id, tmp.getHex());
            this.labels.push(sprite);
            this.group.add(sprite);
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3));
        geo.setAttribute('size',     new THREE.BufferAttribute(sizes, 1));
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
        ctx.font = 'bold 64px Inter, system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = 'black';
        ctx.shadowBlur = 8;
        ctx.fillStyle = `#ffffff`;//`#${new THREE.Color(color).getHexString()}`;
        const labelText = name.charAt(0).toUpperCase() + name.slice(1);
        ctx.fillText(labelText, 256, 64);

        const texture = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
        const sprite = new THREE.Sprite(mat);
        
        sprite.scale.set(32,8,1); 
        return sprite;
    }

    /**
     * Updates the XYZ coordinates of all planets based on their current AltAz values.
     * Called continuously inside the render loop.
     */
    update(positionsMap: Map<string, { alt: number, az: number }>, zoomFactor: number) {
        (this.points.material as THREE.ShaderMaterial).uniforms.zoom.value = zoomFactor;
        const posArray = this.points.geometry.attributes.position.array as Float32Array;

        for (let i = 0; i < this.planetIds.length; i++) {
            const pId = this.planetIds[i];
            const p = positionsMap.get(pId);
            if (p) {
                altAzToXYZ(posArray, i, p.alt, p.az);
                if (this.labels[i]) {
                    const size = PLANET_VISUAL_SIZES[pId.toLowerCase()] ?? PLANET_SIZE_BASE;
                    const offsetY = -3 - (size * 0.45);
                    this.labels[i].position.set(posArray[i * 3], posArray[i * 3 + 1] + offsetY, posArray[i * 3 + 2]);
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