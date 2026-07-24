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

// src/lib/components/skyMap/entities/Planet3DModels.ts

import * as THREE from 'three';
import { PLANET_CONFIGS as PLANET_ENTITY_CONFIGS, PlanetConfig } from './PlanetEntity';
export { PLANET_ENTITY_CONFIGS as PLANET_CONFIGS };
export type { PlanetConfig as Planet3DConfig };

/**
 * Planet3DModels (Deprecated)
 * 3D photorealistic planetary model logic has been refactored into entity classes:
 * `MoonEntity` and `PlanetEntity`, managed by `SolarSystemManager`.
 */
export class Planet3DModels {
    public group = new THREE.Group();
    public getMeshes(): THREE.Mesh[] { return []; }
    public update(): void {}
    public dispose(): void {}
}
