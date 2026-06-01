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

// src/lib/components/skyMap/utils/const.ts

/**
 * @fileoverview Constants used in the SkyMap component for rendering, 
 * camera settings, and planetary visual properties.
 */

/**
 * Radius of the celestial dome.
 * @type {number}
 */
export const DOME_RADIUS = 500;

/**
 * Radius of the ground plane.
 * @type {number}
 */
export const GROUND_RADIUS = 5000;

/**
 * Standard eye level for the camera (in meters).
 * @type {number}
 */
export const EYE_LEVEL = 1.6;

/**
 * Base size for planetary objects in the scene.
 * @type {number}
 */
export const PLANET_SIZE_BASE = 8.0;

/**
 * Default Field of View for the camera.
 * @type {number}
 */
export const FOV_DEFAULT = 60;

/**
 * Minimum Field of View (max zoom in).
 * @type {number}
 */
export const FOV_MIN = 5;

/**
 * Maximum Field of View (max zoom out).
 * @type {number}
 */
export const FOV_MAX = 100;

/**
 * Speed of camera rotation.
 * @type {number}
 */
export const CAMERA_SPEED = -0.5;

/**
 * Speed of zooming.
 * @type {number}
 */
export const ZOOM_SPEED = 0.03;

/**
 * List of cardinal and ordinal directions with their azimuth angles in degrees.
 * @type {readonly {text: string, az: number}[]}
 */
export const CARDINAL_LABELS = [
    { text: 'N',  az: 0   },
    { text: 'NE', az: 45  },
    { text: 'E',  az: 90  },
    { text: 'SE', az: 135 },
    { text: 'S',  az: 180 },
    { text: 'SW', az: 225 },
    { text: 'W',  az: 270 },
    { text: 'NW', az: 315 }
] as const;


/**
 * Mapping of planet keys to their hex color representation.
 * @type {Record<string, number>}
 */
export const PLANET_COLORS: Record<string, number> = {
    sun:     0xfacc15,
    moon:    0xe2e8f0,
    mercury: 0x64748b,
    venus:   0xfed7aa,
    mars:    0xef4444,
    jupiter: 0xfdba74,
    saturn:  0xfef08a,
    uranus:  0xbae6fd,
    neptune: 0x3b82f6,
    pluto: 0x3b82f6
};

/**
 * Mapping of planet keys to their relative visual sizes in the scene.
 * @type {Record<string, number>}
 */
export const PLANET_VISUAL_SIZES: Record<string, number> = {
    sun:     PLANET_SIZE_BASE*8.0,  
    moon:    PLANET_SIZE_BASE*7.0,  
    jupiter: PLANET_SIZE_BASE*1.6,   
    venus:   PLANET_SIZE_BASE*1.5,   
    saturn:  PLANET_SIZE_BASE*1.4,
    mars:    PLANET_SIZE_BASE*1.2,
    mercury: PLANET_SIZE_BASE*1.2,
    uranus:  PLANET_SIZE_BASE*1.0,
    neptune: PLANET_SIZE_BASE*1.0,
    pluto: PLANET_SIZE_BASE*1.0
};