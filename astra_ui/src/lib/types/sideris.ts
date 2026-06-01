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

// src/lib/types/sideris.ts

// --- METADATA ---

/**
 * Metadata for an astronomical constellation.
 */
export interface ConstellationMetadata {
    /** Abbreviated name of the constellation (e.g., 'Ori'). */
    abbr: string;
    /** Common name of the constellation. */
    name: string;
    /** Latin name of the constellation. */
    latin: string;
    /** List of star IDs that belong to the constellation. */
    stars_ids: string[];
    /** Indices of star pairs that form the constellation lines. */
    lines_indices: [number, number][];
}

/**
 * Metadata for a sidereal object (star, galaxy, nebula, etc.).
 */
export interface SiderealObjectMetadata {
    /** Unique identifier for the object. */
    id: string;
    /** Primary name of the object. */
    name: string;
    /** Type of the object. */
    type: "sidereal" | "constellation";
    /** Object category (e.g., 'Star', 'Galaxy'). */
    category: string;
    /** List of alternative common names. */
    common_names: string[];
    /** List of names in various catalogs (e.g., Messier, NGC). */
    catalog_names: string[];
    /** The constellation the object belongs to. */
    constellation: string;
    /** Right Ascension in J2000 epoch (degrees). */
    ra_j2000: number;
    /** Declination in J2000 epoch (degrees). */
    dec_j2000: number;
    /** Apparent magnitude. */
    mag: number | null;
    /** Absolute magnitude (optional). */
    abs_mag?: number | null;
    /** B-V color index (optional). */
    b_v?: number | null;
    /** Luminosity relative to the Sun (optional). */
    luminosity?: number | null;
    /** Distance from Earth in light years (optional). */
    distance_ly?: number | null;
    /** Spectral classification (optional). */
    spectral_type?: string | null;
    /** Apparent size in arcminutes (optional). */
    size_arcmin?: number | null;
}

/**
 * Metadata for a planetary object (Planet, Moon, Sun, etc.).
 */
export interface PlanetaryObjectMetadata {
    /** Unique identifier for the object. */
    id: string;
    /** Primary name of the object. */
    name: string;
    /** List of common names. */
    common_names: string[];
    /** Type of the object. */
    type: "planetary";
    /** Object category. */
    category: string;
    /** Distance from Earth in Astronomical Units (AU). */
    dist: number; 
    /** Apparent magnitude. */
    mag: number | null;
}

/**
 * Generic wrapper for catalog data responses.
 */
export interface MetadataCatalogPayload<T> {
    /** Version of the catalog data. */
    version: string;
    /** Total number of items in the catalog. */
    total: number;
    /** The actual catalog data. */
    data: T;
}

// --- DETAILS & EPHEMERIS ---

/**
 * Ephemeris data for an astronomical object at a specific time and location.
 */
export interface EphemerisData {
    /** Altitude above the horizon (degrees). */
    alt: number;
    /** Azimuth from North (degrees). */
    az: number;
    /** Timestamp of the next transit (meridian crossing). */
    next_transit: string | null;
    /** Timestamp of the next rise. */
    next_rise: string | null;
    /** Timestamp of the next set. */
    next_set: string | null;
    /** Whether the object is circumpolar (never sets). */
    is_circumpolar?: boolean;
    /** Whether the object never rises at this location. */
    never_rises?: boolean;
}

/**
 * Detailed information for a sidereal object, including ephemeris and educational content.
 */
export interface SiderealObjectDetails extends SiderealObjectMetadata, EphemerisData {
    /** Long-form description of the object. */
    description?: string;
    /** Interesting fact about the object. */
    fun_fact?: string;
    /** Tip for observing the object. */
    visual_tip?: string;
    /** Wikidata QID for the object. */
    wikipedia_qid?: string;
}

/**
 * Detailed information about rise, set, and transit events.
 */
export interface RiseSetTransit {
    /** Whether the object is currently above the horizon. */
    is_visible: boolean;
    /** Timestamp of the next rise. */
    next_rise: string | null;
    /** Timestamp of the next transit. */
    next_transit: string | null;
    /** Timestamp of the next set. */
    next_set: string | null;
    /** Azimuth at rise (degrees). */
    rise_az: number | null;
    /** Azimuth at set (degrees). */
    set_az: number | null;
    /** Altitude at transit (degrees). */
    transit_alt: number | null;
    /** Whether the transit happens while the object is above the horizon. */
    transit_visible: boolean;
}

/**
 * Detailed information for a planetary object.
 */
export interface PlanetaryObjectDetails {
    /** Unique identifier. */
    id: string;
    /** Primary name. */
    name: string;
    /** Common names. */
    common_names: string[];
    /** Type of the object. */
    type: string;
    /** Educational description. */
    description?: string;
    /** Interesting fact. */
    fun_fact?: string;
    /** Observing tip. */
    visual_tip?: string;
    /** Wikidata QID. */
    wikipedia_qid?: string;
    /** URL to an image of the object. */
    image_url?: string;
    /** Distance from Earth in AU. */
    dist: number;
    /** Apparent magnitude. */
    mag: number | null;
    /** Apparent angular diameter in arcseconds. */
    ang_diameter?: number | null;
    /** Current altitude. */
    alt: number;
    /** Current azimuth. */
    az: number;
    /** Current Right Ascension J2000. */
    ra_j2000: number;
    /** Current Declination J2000. */
    dec_j2000: number;
    /** Calculated rise, set, and transit data. */
    rise_set_transit: RiseSetTransit;
    /** Any additional object-specific details. */
    extra_details?: any;
}

// --- PAYLOADS ---

/** Response containing a map of sidereal objects. */
export type SiderealCatalogResponse = MetadataCatalogPayload<Record<string, SiderealObjectMetadata>>;
/** Response containing a map of planetary objects. */
export type PlanetaryCatalogResponse = MetadataCatalogPayload<Record<string, PlanetaryObjectMetadata>>;
/** Response containing an array of constellations. */
export type ConstellationCatalogResponse = MetadataCatalogPayload<ConstellationMetadata[]>;
