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
 * Represents a geographic location associated with a user.
 */
export interface UserLocation {
    /** Unique identifier for the location. */
    id: string;
    /** Display label for the location. */
    label: string;
    /** Latitude in decimal degrees. */
    lat: number;     
    /** Longitude in decimal degrees. */
    lng: number;     
    /** Elevation in meters above sea level. */
    elevation: number;
    /** Timezone offset from UTC in hours. */
    timezone: number; 
    /** Whether this is the user's default location. */
    is_default: boolean;
}

/**
 * Data required to create a new user location.
 */
export interface LocationCreate {
    /** Display label for the location. */
    label: string;
    /** Latitude in decimal degrees. */
    lat: number;     
    /** Longitude in decimal degrees. */
    lng: number;     
    /** Elevation in meters above sea level. */
    elevation: number;
    /** Timezone offset from UTC in hours. */
    timezone: number; 
    /** Whether this should be set as the default location. */
    is_default: boolean;
}

/**
 * Represents user-specific application settings.
 */
export interface UserSettings {
    /** UI theme preference (e.g., 'light', 'dark'). */
    theme: string;
    /** Preferred language code (e.g., 'en', 'es'). */
    language: string;
}

/**
 * Represents a user profile in the system.
 */
export interface User {
    /** Unique username. */
    username: string;
    /** User's email address. */
    email: string;
    /** User's full name (optional). */
    full_name?: string;
    /** User's biography (optional). */
    bio?: string;
    /** URL to the user's profile picture (optional). */
    profile_picture_url?: string;
    /** User's application settings. */
    settings: UserSettings;
    /** List of locations associated with the user. */
    locations: UserLocation[];
    /** ISO 8601 timestamp of user creation. */
    creation: string;
}
