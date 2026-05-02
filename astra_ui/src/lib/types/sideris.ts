// src/lib/types/sideris.ts

// --- METADATA ---

export interface ConstellationMetadata {
    abbr: string;
    name: string;
    latin: string;
    stars_ids: string[];
    lines_indices: [number, number][];
}

export interface SiderealObjectMetadata {
    id: string;
    name: string;
    type: string;
    common_names: string[];
    catalog_names: string[];
    constellation: string;
    ra_j2000: number;
    dec_j2000: number;
    mag: number | null;
    abs_mag?: number | null;
    b_v?: number | null;
    luminosity?: number | null;
    distance_ly?: number | null;
    spectral_type?: string | null;
    size_arcmin?: number | null;
}

export interface PlanetaryObjectMetadata {
    id: string;
    name: string;
    common_names: string[];
    dist: number; // AU
    mag: number | null;
}

export interface MetadataCatalogPayload<T> {
    version: string;
    total: number;
    data: T;
}

// --- DETAILS & EPHEMERIS ---

export interface EphemerisData {
    alt: number;
    az: number;
    next_transit: string | null;
    next_rise: string | null;
    next_set: string | null;
    is_circumpolar?: boolean;
    never_rises?: boolean;
}

export interface SiderealObjectDetails extends SiderealObjectMetadata, EphemerisData {
    description?: string;
    fun_fact?: string;
    visual_tip?: string;
    wikipedia_qid?: string;
}

export interface RiseSetTransit {
    is_visible: boolean;
    next_rise: string | null;
    next_transit: string | null;
    next_set: string | null;
    rise_az: number | null;
    set_az: number | null;
    transit_alt: number | null;
    transit_visible: boolean;
}

export interface PlanetaryObjectDetails {
    id: string;
    name: string;
    common_names: string[];
    description?: string;
    fun_fact?: string;
    visual_tip?: string;
    wikipedia_qid?: string;
    image_url?: string;
    dist: number; // AU
    mag: number | null;
    ang_diameter?: number | null;
    alt: number;
    az: number;
    ra_j2000: number;
    dec_j2000: number;
    rise_set_transit: RiseSetTransit;
    extra_details?: any;
}

// --- PAYLOADS ---

export type SiderealCatalogResponse = MetadataCatalogPayload<Record<string, SiderealObjectMetadata>>;
export type PlanetaryCatalogResponse = MetadataCatalogPayload<Record<string, PlanetaryObjectMetadata>>;
export type ConstellationCatalogResponse = MetadataCatalogPayload<ConstellationMetadata[]>;