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
    "unknown": m.data_types_unknown
  };

  // Execute the message function if found, otherwise fallback
  return (lookup[type] || m.data_types_unknown)();
};
