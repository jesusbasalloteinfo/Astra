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

// src/lib/components/skyMap/utils/coordinates.ts

/**
 * @fileoverview Utility functions for coordinate transformations in the SkyMap.
 */

import { DOME_RADIUS } from "./const";

/**
 * Transforms horizontal coordinates (Altitude/Azimuth) to 3D Cartesian space (X, Y, Z).
 * The resulting coordinates are scaled by DOME_RADIUS and stored in a Float32Array.
 * 
 * @param {Float32Array} positionsArray - The array where the resulting X, Y, Z coordinates will be stored.
 * @param {number} index - The index in the positionsArray where the first coordinate (X) should be placed.
 * @param {number} alt - The altitude angle in degrees.
 * @param {number} az - The azimuth angle in degrees.
 */
export function altAzToXYZ(positionsArray: Float32Array, index: number, alt: number, az: number) {
    const altRad = alt * (Math.PI / 180);
    const azRad  = (180 - az) * (Math.PI / 180);
    positionsArray[index * 3]     = DOME_RADIUS * Math.cos(altRad) * Math.sin(azRad);
    positionsArray[index * 3 + 1] = DOME_RADIUS * Math.sin(altRad);
    positionsArray[index * 3 + 2] = DOME_RADIUS * Math.cos(altRad) * Math.cos(azRad);
}