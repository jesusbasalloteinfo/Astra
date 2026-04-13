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

export type SiderealCatalogResponse = MetadataCatalogPayload<Record<string, SiderealObjectMetadata>>;
export type PlanetaryCatalogResponse = MetadataCatalogPayload<Record<string, PlanetaryObjectMetadata>>;
export type ConstellationCatalogResponse = MetadataCatalogPayload<ConstellationMetadata[]>;