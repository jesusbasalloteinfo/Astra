// src/lib/components/skyMap/utils/coordinates.ts

import { DOME_RADIUS } from "./const";

/**
 * Transforms AltAz coordinates to a cartesian space.
 */
export function altAzToXYZ(positionsArray: Float32Array, index: number, alt: number, az: number) {
    const altRad = alt * (Math.PI / 180);
    const azRad  = (180 - az) * (Math.PI / 180);
    positionsArray[index * 3]     = DOME_RADIUS * Math.cos(altRad) * Math.sin(azRad);
    positionsArray[index * 3 + 1] = DOME_RADIUS * Math.sin(altRad);
    positionsArray[index * 3 + 2] = DOME_RADIUS * Math.cos(altRad) * Math.cos(azRad);
}