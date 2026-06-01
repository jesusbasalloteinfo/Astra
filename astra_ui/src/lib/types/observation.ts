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

/**
 * Represents an observation session in the system.
 */
export interface Observation {
    /** Unique identifier for the observation. */
    id: string;
    /** Human-readable name of the observation. */
    name: string;
    /** Optional detailed description of the observation goals or results. */
    description?: string;
    /** The ID of the user who owns this observation. */
    owner: string;
    /** ISO 8601 timestamp of when the observation was created. */
    creation: string;
    /** ISO 8601 timestamp of when the observation was last accessed. */
    last_used: string;
}

/**
 * Data required to create a new observation session.
 */
export interface ObservationCreate {
    /** Human-readable name for the new observation. */
    name: string;
    /** Optional detailed description for the new observation. */
    description?: string;
}

/**
 * Data structure for updating an existing observation session.
 */
export interface ObservationUpdate {
    /** Updated name for the observation (optional). */
    name?: string;
    /** Updated description for the observation (optional). */
    description?: string;
}
