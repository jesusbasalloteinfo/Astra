// src/lib/utils/i18n.ts
import { getLocale } from "$lib/paraglide/runtime";

export const toInlangBool = (val: boolean): "true" | "false" => val ? "true" : "false";

export const formatNumber = (value, decimals = 1) => {
  return value.toLocaleString(getLocale(), {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};
