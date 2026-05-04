// src/lib/utils/i18n.ts
import { m } from "$lib/paraglide/messages";
import { getLocale } from "$lib/paraglide/runtime";

export const toInlangBool = (val: boolean): "true" | "false" => val ? "true" : "false";

export const formatNumber = (value, decimals = 1) => {
  return value.toLocaleString(getLocale(), {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

export const translateObjectType = (type: string): string => {
  const lookup: Record<string, () => string> = {
    "planetary": m.data_types_planetary,
    "moon": m.data_types_moon,
    "galaxy": m.data_types_galaxy,
    "open_cluster": m.data_types_open_cluster,
    "globular_cluster": m.data_types_globular_cluster,
    "galactic_cluster": m.data_types_galactic_cluster,
    "nebula": m.data_types_nebula,
    "molecular_cloud": m.data_types_molecular_cloud,
    "planetary_nebula": m.data_types_planetary_nebula,
    "supernova_remnant": m.data_types_supernova_remnant,
    "asterism": m.data_types_asterism,
    "double_star": m.data_types_double_star,
    "star_system": m.data_types_star_system,
    "star": m.data_types_star,
    "constellation": m.data_types_constellation,
    "unknown": m.data_types_unknown
  };
  console.log(type)
  // Execute the message function if found, otherwise fallback
  return (lookup[type] || m.data_types_unknown)();
};

export const getMoonPhaseName = (
    isNewMoon: boolean, 
    isFullMoon: boolean, 
    isWaxing: boolean, 
    isCrescent: boolean, 
    illuminationPct: number
): string => {
    if (isNewMoon) return m.data_moon_phase_new();
    if (isFullMoon) return m.data_moon_phase_full();
    
    if (isWaxing) {
        if (illuminationPct > 47 && illuminationPct < 53) return m.data_moon_phase_first_quarter();
        return isCrescent ? m.data_moon_phase_waxing_crescent() : m.data_moon_phase_waxing_gibbous();
    } else {
        if (illuminationPct > 47 && illuminationPct < 53) return m.data_moon_phase_last_quarter();
        return isCrescent ? m.data_moon_phase_waning_crescent() : m.data_moon_phase_waning_gibbous();
    }
};