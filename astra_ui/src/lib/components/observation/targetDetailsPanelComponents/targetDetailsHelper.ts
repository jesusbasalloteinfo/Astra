// src/lib/utils/targetDetailsHelper.ts
import { getLocale } from '$lib/paraglide/runtime';
import { m } from '$lib/paraglide/messages';
import { endpoints, siderisEndpoints } from '$lib/api/endpoints';
import type { PlanetaryObjectDetails, SiderealObjectDetails } from '$lib/types/sideris';
import { formatNumber } from '$lib/utils/i18n';
import { catalogStore } from '$lib/stores/skyCatalog.svelte';

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

export function getWikipediaUrl(qid: string | null | undefined): string | null {
    if (!qid) return null;
    return `https://www.wikidata.org/wiki/Special:GoToLinkedPage/${getLocale()}wiki/${qid}`;
}