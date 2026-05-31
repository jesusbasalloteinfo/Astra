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