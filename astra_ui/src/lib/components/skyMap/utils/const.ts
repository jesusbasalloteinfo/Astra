// src/lib/components/skyMap/utils/const.ts

export const DOME_RADIUS = 500;
export const GROUND_RADIUS = 5000;
export const EYE_LEVEL = 1.6;
export const PLANET_SIZE_BASE = 8.0;

export const FOV_DEFAULT = 60;
export const FOV_MIN = 5;
export const FOV_MAX = 100;
export const CAMERA_SPEED = -0.5;
export const ZOOM_SPEED = 0.03;

export const CARDINAL_LABELS = [
    { text: 'N',  az: 0   },
    { text: 'NE', az: 45  },
    { text: 'E',  az: 90  },
    { text: 'SE', az: 135 },
    { text: 'S',  az: 180 },
    { text: 'SO', az: 225 },
    { text: 'O',  az: 270 },
    { text: 'NO', az: 315 }
] as const;


export const PLANET_COLORS: Record<string, number> = {
    sun:     0xfacc15,
    moon:    0xe2e8f0,
    mercury: 0x64748b,
    venus:   0xfed7aa,
    mars:    0xef4444,
    jupiter: 0xfdba74,
    saturn:  0xfef08a,
    uranus:  0xbae6fd,
    neptune: 0x3b82f6,
    pluto: 0x3b82f6
};

export const PLANET_VISUAL_SIZES: Record<string, number> = {
    sun:     PLANET_SIZE_BASE*8.0,  
    moon:    PLANET_SIZE_BASE*7.0,  
    jupiter: PLANET_SIZE_BASE*1.6,   
    venus:   PLANET_SIZE_BASE*1.5,   
    saturn:  PLANET_SIZE_BASE*1.4,
    mars:    PLANET_SIZE_BASE*1.2,
    mercury: PLANET_SIZE_BASE*1.2,
    uranus:  PLANET_SIZE_BASE*1.0,
    neptune: PLANET_SIZE_BASE*1.0,
    pluto: PLANET_SIZE_BASE*1.0
};