import * as THREE from 'three';

/**
 * Create an svg texture for a crosshair
 */
export function createCrosshairTexture(type: 'sidereal' | 'focus', color: string): THREE.Texture {
    let svg = '';

    if (type === 'sidereal') {
        svg = `
            <svg width="180" height="180" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">
                <g fill="${color}">
                    <path d="M 90,40 A 50,50 0 1 0 90,140 A 50,50 0 1 0 90,40 Z m 0,10 A 40,40 0 1 1 90,130 A 40,40 0 1 1 90,50 Z" />
                    <rect x="85" y="15" width="10" height="50" />
                    <rect x="85" y="115" width="10" height="50" />
                    <rect x="15" y="85" width="50" height="10" />
                    <rect x="115" y="85" width="50" height="10" />
                </g>
            </svg>
        `;
    } else {
        svg = `
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M35 20 H20 V35 M65 20 H80 V35 M35 80 H20 V65 M65 80 H80 V65" fill="none" stroke="${color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }

    const encoded = encodeURIComponent(svg);
    const dataUri = `data:image/svg+xml;utf8,${encoded}`;
    
    return new THREE.TextureLoader().load(dataUri);
}