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

// src/lib/components/skyMap/entities/Constellations.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

/**
 * Interface representing a constellation label's data.
 * @interface
 */
interface ConstellationLabel {
    /** The Three.js sprite object for the label. */
    sprite: THREE.Sprite;
    /** IDs of the stars that form the constellation. */
    starsIds: string[];
    /** Localized name of the constellation. */
    name: string;
    /** Latin name of the constellation. */
    latin: string;
    /** Texture containing the rendered text. */
    texture: THREE.CanvasTexture;
    /** Canvas 2D context used for drawing the text. */
    ctx: CanvasRenderingContext2D;
}

/**
 * Constellations Entity
 * 
 * Manages the rendering of constellation lines and their dynamic labels.
 * Handles language switching, visibility, and daytime contrast adjustments.
 */
export class Constellations {
    /** Group containing all constellation lines and labels. */
    public group = new THREE.Group();
    /** The line segments mesh for constellation boundaries/patterns. */
    private lines: THREE.LineSegments;

    /** Array of star ID pairs representing the start and end of each line segment. */
    private constellationPairs: string[] = [];
    /** List of label objects for each constellation. */
    private labels: ConstellationLabel[] = [];
    
    /** Whether constellation labels are visible. */
    private showLabels: boolean = true;
    /** Whether to use Latin names instead of localized names. */
    private useLatin: boolean = false;
    /** Current color of the constellation lines. */
    private currentColor: number = 0xffffff;
    /** Current color of the constellation labels. */
    private currentLabelColor: number = 0xffffff;
    /** Current opacity of the lines. */
    private currentOpacity: number = 0.4;
    /** Factor used to track changes in daylight for performance. */
    private lastDayFactor: number = -1; // For tracking color changes

    /**
     * Creates an instance of Constellations.
     * @param {number} color - Initial line color.
     * @param {number} labelColor - Initial label text color.
     * @param {number} opacity - Initial line opacity.
     * @param {boolean} showLabels - Initial label visibility.
     * @param {boolean} useLatin - Whether to use Latin names.
     */
    constructor(color: number, labelColor:number, opacity: number, showLabels: boolean, useLatin: boolean) {
        this.currentColor = color;
        this.currentLabelColor = labelColor;
        this.currentOpacity = opacity ?? 0.4;
        this.showLabels = showLabels ?? true; 
        this.useLatin = useLatin ?? true;

        const geo = this.buildGeometry();

        const mat = new THREE.LineBasicMaterial({
            color: color,
            transparent: true,
            opacity: this.currentOpacity,
            depthWrite: false 
        });

        this.lines = new THREE.LineSegments(geo, mat);
        this.lines.renderOrder = 0;
        this.group.add(this.lines);
    }

    /**
     * Parses the constellation catalog to build connection lines and prepare labels.
     * @returns {THREE.BufferGeometry} The generated geometry for constellation lines.
     * @private
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
     * @returns {{ sprite: THREE.Sprite, texture: THREE.CanvasTexture, ctx: CanvasRenderingContext2D }} Label resources.
     * @private
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
     * Redraws the text on the Canvas (used for init and when switching languages/daytime).
     * @param {ConstellationLabel} label - The label object to update.
     * @param {number} [colorOverride] - Optional color override for the text.
     * @private
     */
    private updateLabelText(label: ConstellationLabel, colorOverride?: number) {
        const text = this.useLatin ? label.latin : label.name;
        
        label.ctx.clearRect(0, 0, 1024, 128);
        label.ctx.font = 'bold 56px Inter, system-ui, sans-serif';
        label.ctx.letterSpacing = '3px';
        label.ctx.textAlign = 'center';
        label.ctx.textBaseline = 'middle';

        const color = colorOverride ?? this.currentLabelColor;
        label.ctx.fillStyle = `#${new THREE.Color(color).getHexString()}`;
        label.ctx.fillText(text.toUpperCase(), 512, 64);
        
        label.texture.needsUpdate = true;
    }

    /**
     * Updates lines and calculates the centroid for each label based on current star positions.
     * Adjusts visibility and contrast based on the daylight factor.
     * @param {Map<string, { alt: number, az: number }>} positionsMap - Map of object IDs to Alt/Az positions.
     * @param {number} [daylightFade=1.0] - Fade factor for daytime (1.0 = night, 0.0 = day).
     */
    update(positionsMap: Map<string, { alt: number, az: number }>, daylightFade: number = 1.0) {
        if (!this.group.visible || this.constellationPairs.length === 0) return;

        // --- DYNAMIC CONTRAST FOR DAYTIME ---
        const dayFactor = 1.0 - daylightFade; // 0 (night) to 1 (day)
        const mat = this.lines.material as THREE.LineBasicMaterial;

        // Quantize dayFactor to update in 100 steps
        const quantizedDayFactor = Math.round(dayFactor * 100) / 100;

        if (quantizedDayFactor !== this.lastDayFactor) {
            this.lastDayFactor = quantizedDayFactor;

            // 1. Update Lines
            const lineC = new THREE.Color(this.currentColor);
            if (quantizedDayFactor > 0) {
                const hsl = { h: 0, s: 0, l: 0 };
                lineC.getHSL(hsl);
                // Add slightly more saturation, slightly less darkness
                hsl.s = Math.min(1.0, hsl.s + quantizedDayFactor * 0.15);
                hsl.l = Math.max(0.05, hsl.l - quantizedDayFactor * 0.1);
                lineC.setHSL(hsl.h, hsl.s, hsl.l);
                // Moderate opacity increase
                mat.opacity = this.currentOpacity + (quantizedDayFactor * 0.3);
            } else {
                mat.opacity = this.currentOpacity;
            }
            mat.color.copy(lineC);

            // 2. Update Labels
            const labelC = new THREE.Color(this.currentLabelColor);
            if (quantizedDayFactor > 0) {
                const hsl = { h: 0, s: 0, l: 0 };
                labelC.getHSL(hsl);
                hsl.s = Math.min(1.0, hsl.s + quantizedDayFactor * 0.15);
                hsl.l = Math.max(0.05, hsl.l - quantizedDayFactor * 0.15);
                labelC.setHSL(hsl.h, hsl.s, hsl.l);
            }
            const labelColorNum = labelC.getHex();
            this.labels.forEach(l => this.updateLabelText(l, labelColorNum));
        }

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
     * @param {boolean} visible - Whether constellation lines are visible.
     * @param {number} color - Line color hex value.
     * @param {number} labelColor - Label color hex value.
     * @param {number} opacity - Line opacity (0-1).
     * @param {boolean} [showLabels] - Whether to show text labels.
     * @param {boolean} [useLatin] - Whether to use Latin names.
     */
    setProps(visible: boolean, color: number, labelColor: number, opacity: number, showLabels?: boolean, useLatin?: boolean) {
        if (visible !== undefined) this.group.visible = visible;
        
        let needsRedraw = false;

        // Line color
        if (color !== undefined && color !== this.currentColor) {
            this.currentColor = color;
            (this.lines.material as THREE.LineBasicMaterial).color.setHex(color);
            this.lastDayFactor = -1; // Force color recalculation in update()
        }

        // Opacity
        if (opacity !== undefined && opacity !== this.currentOpacity) {
            this.currentOpacity = opacity;
            (this.lines.material as THREE.LineBasicMaterial).opacity = opacity;
        }

        // Label control
        if (showLabels !== undefined && showLabels !== this.showLabels) {
            this.showLabels = showLabels;
            this.labels.forEach(l => l.sprite.visible = this.showLabels); 
        }

        // Language or color change
        if (useLatin !== undefined && useLatin !== this.useLatin) {
            this.useLatin = useLatin;
            needsRedraw = true;
        }

        if (labelColor !== undefined && labelColor !== this.currentLabelColor) {
            this.currentLabelColor = labelColor;
            needsRedraw = true;
        }

        if (needsRedraw) {
            this.lastDayFactor = -1; // Force label redraw in update()
            this.labels.forEach(l => this.updateLabelText(l));
        }
    }

    /**
     * Cleans up Three.js resources used by constellations.
     */
    dispose() {
        this.lines.geometry.dispose();
        (this.lines.material as THREE.Material).dispose();
        this.labels.forEach(l => {
            l.texture.dispose();
            l.sprite.material.dispose();
        });
    }
}