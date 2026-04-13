// src/lib/components/skyMap/entities/Constellations.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

interface ConstellationLabel {
    sprite: THREE.Sprite;
    starsIds: string[];
    name: string;
    latin: string;
    texture: THREE.CanvasTexture;
    ctx: CanvasRenderingContext2D;
}

/**
 * Constellations Entity
 * * Manages the rendering of constellation lines and their dynamic labels
 */
export class Constellations {
    public group = new THREE.Group();
    private lines: THREE.LineSegments;

    private constellationPairs: string[] = [];
    private labels: ConstellationLabel[] = [];
    
    private showLabels: boolean = true;
    private useLatin: boolean = false;
    private currentColor: number = 0xffffff;
    private currentLabelColor: number = 0xffffff;

    constructor(color: number, labelColor:number, opacity: number, showLabels: boolean, useLatin: boolean) {
        this.currentColor = color;
        this.currentLabelColor = labelColor;
        this.showLabels = showLabels ?? true; 
        this.useLatin = useLatin ?? true;

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
     * Parses the constellation catalog to build connection lines and prepare labels.
     */
    private buildGeometry(): THREE.BufferGeometry {
        const pairs: string[] = [];

        catalogStore.constellations.forEach(constel => {
            // 1. Build Lines
            constel.lines_indices.forEach(([idxA, idxB]) => {
                const starIdA = constel.stars_ids[idxA];
                const starIdB = constel.stars_ids[idxB];
                
                if (starIdA && starIdB) {
                    pairs.push(starIdA, starIdB);
                }
            });

            // 2. Prepare Labels (if it has stars to calculate a center)
            if (constel.stars_ids.length > 0) {
                const labelData = this.createLabelCanvas();
                const labelObj: ConstellationLabel = {
                    sprite: labelData.sprite,
                    starsIds: constel.stars_ids,
                    name: constel.name,
                    latin: constel.latin,
                    texture: labelData.texture,
                    ctx: labelData.ctx
                };
                
                this.updateLabelText(labelObj);
                this.labels.push(labelObj);
                this.group.add(labelData.sprite);
            }
        });

        this.constellationPairs = pairs; 

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pairs.length * 3), 3));
        geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), DOME_RADIUS);
        
        return geo;
    }

    /**
     * Creates an empty Sprite and Canvas for a label, ready to be painted.
     */
    private createLabelCanvas() {
        const canvas = document.createElement('canvas');
        canvas.width = 1024; canvas.height = 128;
        const ctx = canvas.getContext('2d')!;
        
        const texture = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
        const sprite = new THREE.Sprite(mat);
        
        
        sprite.scale.set(80, 10, 1); 

        return { sprite, texture, ctx };
    }

    /**
     * Redraws the text on the Canvas (used for init and when switching languages)
     */
    private updateLabelText(label: ConstellationLabel) {
        const text = this.useLatin ? label.latin : label.name;
        
        label.ctx.clearRect(0, 0, 1024, 128);
        label.ctx.font = 'bold 56px Inter, system-ui, sans-serif';
        label.ctx.letterSpacing = '3px';
        label.ctx.textAlign = 'center';
        label.ctx.textBaseline = 'middle';


        label.ctx.fillStyle = `#${new THREE.Color(this.currentLabelColor).getHexString()}`;
        label.ctx.fillText(text.toUpperCase(), 512, 64);
        
        label.texture.needsUpdate = true;
    }

    /**
     * Updates lines and calculates the centroid for each label.
     */
    update(positionsMap: Map<string, { alt: number, az: number }>) {
        if (this.constellationPairs.length === 0) return;

        // --- UPDATE LINES ---
        const posArray = this.lines.geometry.attributes.position.array as Float32Array;
        for (let i = 0; i < this.constellationPairs.length; i++) {
            const starId = this.constellationPairs[i];
            const p = positionsMap.get(starId);
            
            if (p) {
                altAzToXYZ(posArray, i, p.alt, p.az);
            } else {
                posArray[i * 3] = 0; posArray[i * 3 + 1] = 0; posArray[i * 3 + 2] = 0;
            }
        }
        this.lines.geometry.attributes.position.needsUpdate = true;

        // --- UPDATE LABELS ---
        const tempVec = new THREE.Vector3();
        const starPos = new Float32Array(3);

        for (const label of this.labels) {
            tempVec.set(0, 0, 0);
            let validStars = 0;

            // Add up all star coordinates
            for (const starId of label.starsIds) {
                const p = positionsMap.get(starId);
                if (p) {
                    altAzToXYZ(starPos, 0, p.alt, p.az);
                    tempVec.x += starPos[0];
                    tempVec.y += starPos[1];
                    tempVec.z += starPos[2];
                    validStars++;
                }
            }

            if (validStars > 0) {
                // Get mean
                tempVec.divideScalar(validStars);
                
                // Normalise and multiply by the dome radius
                tempVec.normalize().multiplyScalar(DOME_RADIUS);
                
                label.sprite.position.copy(tempVec);
                label.sprite.visible = this.showLabels;
            } else {
                label.sprite.visible = false;
            }
        }
    }

    /**
     * Dynamically updates the visual properties and text settings.
     */
    setProps(visible: boolean, color: number, labelColor: number, opacity: number, showLabels?: boolean, useLatin?: boolean) {
        if (visible !== undefined) this.group.visible = visible;
        
        // Line color
        if (color !== undefined && color !== this.currentColor) {
            this.currentColor = color;
            (this.lines.material as THREE.LineBasicMaterial).color.setHex(color);
        }

        // Opacity
        if (opacity !== undefined) {
            (this.lines.material as THREE.LineBasicMaterial).opacity = opacity;
        }

        // Label control
        if (showLabels !== undefined && showLabels !== this.showLabels) {
            this.showLabels = showLabels;
            this.labels.forEach(l => l.sprite.visible = this.showLabels); 
        }

        // Language or color change
        let needsRedraw = false;
        
        if (useLatin !== undefined && useLatin !== this.useLatin) {
            this.useLatin = useLatin;
            needsRedraw = true;
        }

        if (labelColor !== undefined && labelColor !== this.currentLabelColor) {
            this.currentLabelColor = labelColor;
            needsRedraw = true;
        }

        if (needsRedraw) {
            this.labels.forEach(l => this.updateLabelText(l));
        }
    }

    dispose() {
        this.lines.geometry.dispose();
        (this.lines.material as THREE.Material).dispose();
        this.labels.forEach(l => {
            l.texture.dispose();
            l.sprite.material.dispose();
        });
    }
}