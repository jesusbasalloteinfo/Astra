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

// src/lib/components/skyMap/entities/AbstractPlanetaryObject.ts

import * as THREE from 'three';
import { DOME_RADIUS } from '../utils/const';
import { altAzToXYZ } from '../utils/coordinates';

/** Label object structure containing sprite and canvas resources */
export interface LabelObject {
    sprite: THREE.Sprite;
    ctx: CanvasRenderingContext2D;
    texture: THREE.CanvasTexture;
    name: string;
}

/**
 * Abstract base class for all solar system celestial objects (Sun, Moon, Planets).
 * Encapsulates common 3D scene node hierarchy, positioning, labels, and lifecycle.
 */
export abstract class AbstractPlanetaryObject {
    /** Unique entity ID (e.g., 'sun', 'moon', 'mars') */
    public readonly id: string;
    /** Human-readable display name */
    public readonly name: string;
    /** Container group for this entity's 3D scene elements */
    public readonly group: THREE.Group = new THREE.Group();
    /** Base visual size for point billboard rendering */
    public readonly baseSize: number;
    /** Base color for the object */
    public readonly color: THREE.Color;
    
    /** Current spherical alt/az coordinates */
    public currentAlt: number = 0;
    public currentAz: number = 0;

    /** Text label sprite and canvas context */
    protected labelObj: LabelObject;
    /** Daylight factor tracker for label color transitions */
    protected lastDayFactor: number = -1;

    /**
     * Creates an instance of AbstractPlanetaryObject.
     * @param id Unique identifier
     * @param name Display name
     * @param baseSize Base render size
     * @param colorHex Primary hex color
     * @param anchorX Label horizontal alignment offset
     * @param anchorY Label vertical alignment offset
     */
    constructor(
        id: string,
        name: string,
        baseSize: number,
        colorHex: number,
        anchorX: number = -0.075,
        anchorY: number = -0.075
    ) {
        this.id = id;
        this.name = name;
        this.baseSize = baseSize;
        this.color = new THREE.Color(colorHex);

        this.labelObj = this.createLabel(name, anchorX, anchorY);
        this.group.add(this.labelObj.sprite);
    }

    /**
     * Creates a text label sprite for this celestial body.
     */
    protected createLabel(name: string, anchorX: number, anchorY: number): LabelObject {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 128;
        const ctx = canvas.getContext('2d')!;
        const texture = new THREE.CanvasTexture(canvas);
        
        const mat = new THREE.SpriteMaterial({
            map: texture,
            transparent: true,
            depthWrite: false,
            depthTest: true
        });
        const sprite = new THREE.Sprite(mat);
        
        sprite.scale.set(32, 8, 1);
        sprite.renderOrder = 3;
        sprite.center.set(anchorX, anchorY);

        const labelObj: LabelObject = { sprite, ctx, texture, name };
        this.updateLabelText(labelObj, 0xffffff);
        
        return labelObj;
    }

    /**
     * Redraws the label text with specified color.
     */
    protected updateLabelText(label: LabelObject, colorHex: number) {
        const { ctx, texture, name } = label;
        ctx.clearRect(0, 0, 512, 128);
        
        ctx.font = '64px Inter, system-ui, sans-serif';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        
        ctx.fillStyle = `#${new THREE.Color(colorHex).getHexString()}`;
        ctx.fillText(name.toUpperCase(), 16, 100);
        texture.needsUpdate = true;
    }

    /**
     * Updates label color based on daylight transition.
     */
    public updateDaylightLabel(quantizedDayFactor: number) {
        if (quantizedDayFactor !== this.lastDayFactor) {
            this.lastDayFactor = quantizedDayFactor;

            const labelC = new THREE.Color(0xffffff);
            if (quantizedDayFactor > 0) {
                const daytimeBlue = new THREE.Color().setHSL(0.64, 1.0, 0.05);
                labelC.lerp(daytimeBlue, quantizedDayFactor);
            }
            this.updateLabelText(this.labelObj, labelC.getHex());
        }
    }

    /**
     * Sets the celestial position from Alt/Az coordinates in degrees.
     */
    public setPosition(alt: number, az: number) {
        this.currentAlt = alt;
        this.currentAz = az;

        const posArray = new Float32Array(3);
        altAzToXYZ(posArray, 0, alt, az);
        
        this.group.position.set(posArray[0], posArray[1], posArray[2]);
    }

    /**
     * Updates object state, animations, materials, and internal child transforms.
     * @param alt Altitude in degrees
     * @param az Azimuth in degrees
     * @param zoomFactor Current camera zoom factor
     * @param daylightFade Daylight opacity factor (1.0 = night, 0.0 = day)
     * @param currentFov Current camera Field of View in degrees
     * @param sunPos Optional Sun Alt/Az position for lighting
     */
    public abstract update(
        alt: number,
        az: number,
        zoomFactor: number,
        daylightFade: number,
        currentFov: number,
        sunPos?: { alt: number, az: number }
    ): void;

    /** Returns all objects relevant for raycast picking */
    public abstract getRaycastObjects(): THREE.Object3D[];

    /** Returns photorealistic 3D model meshes if available */
    public get3DMeshes(): THREE.Mesh[] {
        return [];
    }

    /** Returns 2D point billboard mesh if available */
    public getPointMesh(): THREE.Points | null {
        return null;
    }

    /** Cleans up WebGL textures, geometries, and materials */
    public dispose(): void {
        this.labelObj.texture.dispose();
        this.labelObj.sprite.material.dispose();
    }
}
