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

// src/lib/utils/targetDetailsHelper.ts
import { getLocale } from '$lib/paraglide/runtime';
import { m } from '$lib/paraglide/messages';
import { endpoints, siderisEndpoints } from '$lib/api/endpoints';
import type { PlanetaryObjectDetails, SiderealObjectDetails } from '$lib/types/sideris';
import { formatNumber } from '$lib/utils/i18n';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

/**
 * Returns the image URL for an astronomical object.
 * For planets, it returns a local API URL. For sidereal objects, it returns a HiPS2FITS URL.
 * 
 * @param {PlanetaryObjectDetails | SiderealObjectDetails} details - Object details from the catalog
 * @param {boolean} isPlanet - Whether the object is a planet/solar system body
 * @returns {string|null} The image URL or null if not available
 */
export function getImageUrl(details: PlanetaryObjectDetails | SiderealObjectDetails, isPlanet: boolean): string | null {
    if (isPlanet) {
        const planetaryDetails = details as PlanetaryObjectDetails;
        return planetaryDetails.image_url ? `${endpoints.apiBase}${siderisEndpoints.base}${planetaryDetails.image_url}` : null;
    } else {
        const ra = details.ra_j2000 * 15;
        const dec = details.dec_j2000;
        const sizeArcmin = (details as SiderealObjectDetails).size_arcmin || 30;
        let fov = Math.max(0.1, Math.min(10, (sizeArcmin / 60) * 1.5));
        return `https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FDSS2%2Fcolor&width=600&height=375&fov=${fov}&projection=TAN&coordsys=icrs&ra=${ra}&dec=${dec}&format=png`;
    }
}

/**
 * Builds a list of statistics and ephemeris data for the target details panel.
 * 
 * @param {any} details - Static object details from the catalog
 * @param {any} dynamicData - Dynamic data (alt/az) for the current observer
 * @param {boolean} isPlanet - Whether the object is a planet/solar system body
 * @returns {Object} An object containing the formatted stats array and ephemeris object
 */
export function buildDynamicStats(details: any, dynamicData: any, isPlanet: boolean) {
    // 1. Base Stadistics
    let dist = isPlanet ? details.dist : details.distance_ly;
    const distUnit = (isPlanet && dist>0.1) ? 'AU' : isPlanet ? 'KM' : 'LY';
    dist = (isPlanet && dist>0.1) ? dist: dist*150000000;

    let stats = [
        { label: m.obs_targetinfo_alt(), value: `${formatNumber(dynamicData.alt, 1)}°` },
        { label: m.obs_targetinfo_az(), value: `${formatNumber(dynamicData.az, 1)}°` },
        { label: m.obs_targetinfo_mag(), value: details.mag != null ? formatNumber(details.mag, 2) : '—' },
        { 
            label: m.obs_targetinfo_dist(), 
            value: dist ? `${formatNumber(dist, distUnit==="KM" ? 0 : 2)} ${distUnit}` : '—' 
        }
    ];

    // 2. Get Rise/Set/Transit
    let ephemeris = { rise: null, transit: null, set: null };

    // 3. Specific Stadistics

    if (!isPlanet) {
        const sidereal = details as SiderealObjectDetails;
        ephemeris = { rise: sidereal.next_rise, transit: sidereal.next_transit, set: sidereal.next_set };
        
        if (sidereal.constellation) stats.push({ label: m.obs_targetinfo_const(), value: catalogStore.getConstellationName(sidereal.constellation, true) });
        if (sidereal.size_arcmin) stats.push({ label: m.obs_targetinfo_size(), value: `${sidereal.size_arcmin}'` });
        if (sidereal.spectral_type) stats.push({ label: m.obs_targetinfo_sptype(), value: sidereal.spectral_type });
    } else {
        const planetary = details as PlanetaryObjectDetails;
        if (planetary.rise_set_transit) {
             ephemeris = { rise: planetary.rise_set_transit.next_rise, transit: planetary.rise_set_transit.next_transit, set: planetary.rise_set_transit.next_set };
        }
    }

    return { stats, ephemeris };
}

/**
 * Constructs a Wikipedia URL for a given Wikidata QID and the current locale.
 * 
 * @param {string|null|undefined} qid - The Wikidata QID
 * @returns {string|null} The Wikipedia URL or null if QID is not provided
 */
export function getWikipediaUrl(qid: string | null | undefined): string | null {
    if (!qid) return null;
    return `https://www.wikidata.org/wiki/Special:GoToLinkedPage/${getLocale()}wiki/${qid}`;
}