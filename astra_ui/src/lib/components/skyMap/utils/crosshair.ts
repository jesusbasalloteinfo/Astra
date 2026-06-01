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

// src/lib/components/skyMap/utils/crosshair.ts
/**
 * @fileoverview Utility for generating crosshair textures used in the SkyMap.
 */

import * as THREE from 'three';

/**
 * Creates an SVG-based texture for a crosshair.
 * Supports different styles: 'sidereal' (circular target) or 'focus' (corner brackets).
 * 
 * @param {('sidereal' | 'focus')} type - The style of the crosshair.
 * @param {string} color - The CSS color string (e.g., '#ffffff', 'red') for the crosshair.
 * @returns {THREE.Texture} A Three.js texture containing the SVG crosshair.
 */
export function createCrosshairTexture(type: 'sidereal' | 'focus', color: string): THREE.Texture {
    let svg = '';

    if (type === 'sidereal') {
        svg = `
            <svg width="180" height="180" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">
                <g fill="${color}">
                    <path d="M 90,40 A 50,50 0 1 0 90,140 A 50,50 0 1 0 90,40 Z m 0,10 A 40,40 0 1 1 90,130 A 40,40 0 1 1 90,50 Z" />
                    <rect x="85" y="15" width="10" height="50" />
                    <rect x="85" y="115" width="10" height="50" />
                    <rect x="15" y="85" width="50" height="10" />
                    <rect x="115" y="85" width="50" height="10" />
                </g>
            </svg>
        `;
    } else {
        svg = `
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M35 20 H20 V35 M65 20 H80 V35 M35 80 H20 V65 M65 80 H80 V65" fill="none" stroke="${color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }

    const encoded = encodeURIComponent(svg);
    const dataUri = `data:image/svg+xml;utf8,${encoded}`;
    
    return new THREE.TextureLoader().load(dataUri);
}