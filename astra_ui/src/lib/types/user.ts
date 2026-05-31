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
