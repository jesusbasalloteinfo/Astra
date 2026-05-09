// src/lib/components/skyMap/entities/Environment.ts

import * as THREE from 'three';
import { DOME_RADIUS, GROUND_RADIUS, EYE_LEVEL, CARDINAL_LABELS } from '../utils/const';


/**
 * Environment Entity
 * Responsible for rendering non-celestial static elements, such as the 
 * ground sphere and the cardinal direction markers on the horizon.
 */
export class Environment {
    public group = new THREE.Group(); // Acts as a container for multiple meshes/sprites that can be added to the main Scene together.
    private groundMesh: THREE.Mesh;

    constructor(groundColor: number, cardinalColor: string) {
        // Create the Ground
        const geo = new THREE.SphereGeometry(GROUND_RADIUS, 128, 128);
        const mat = new THREE.MeshBasicMaterial({
            color: groundColor, 
            side: THREE.FrontSide, 
            depthWrite: true, 
            depthTest: true });
        this.groundMesh = new THREE.Mesh(geo, mat);

        // Position is exactly below the camera eye level by its radius amount
        this.groundMesh.position.set(0, -GROUND_RADIUS, 0);
        this.groundMesh.renderOrder = 10;
        this.group.add(this.groundMesh);

        this.setGroundMode(false);

        // Create Cardinal Labels
        CARDINAL_LABELS.forEach(({ text, az }) => {
            const sprite = this.createCardinalSprite(text, cardinalColor)            
            const azRad = (180 - az) * (Math.PI / 180);
            sprite.position.set(
                (DOME_RADIUS - 20) * Math.sin(azRad),
                EYE_LEVEL,
                (DOME_RADIUS - 20) * Math.cos(azRad)
            );
            this.group.add(sprite);
        });
    }
    /**
     * Switches betweeen solid and translucid ground
     */
    setGroundMode(isSolid: boolean) {
        const mat = this.groundMesh.material as THREE.MeshBasicMaterial;
        
        if (isSolid) {
            mat.opacity = 1.0;
            mat.transparent = false;
            mat.depthWrite = true; 
            this.groundMesh.renderOrder = 10; 
        } else {
            mat.opacity = 0.6; 
            mat.transparent = true;
            mat.depthWrite = false;
            this.groundMesh.renderOrder = 10; 
        }
        
        mat.needsUpdate = true;
    }

    /**
     * Generates a 2D Canvas-based text sprite for the cardinal directions.
     */
    createCardinalSprite(text: string, cardinalColor: string): THREE.Sprite {
        const canvas = document.createElement('canvas');
        canvas.width  = 128; canvas.height = 128;
        const ctx = canvas.getContext('2d')!;
        ctx.fillStyle    = cardinalColor;
        ctx.font         = 'bold 80px Inter, system-ui, sans-serif';
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 64, 64);

        const mat    = new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas), transparent: true, depthWrite: false});
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(20, 20, 1);
        return sprite;
    }

    /**
     * Toggles the visibility of the ground plane.
     */
    setGroundVisible(visible: boolean) {
        this.groundMesh.visible = visible;
    }

    /**
     * Dynamically updates the ground color
     */
    setGroundColor(color: number) {
        (this.groundMesh.material as THREE.MeshBasicMaterial).color.setHex(color);
    }

    /**
     * Iterates through the group and safely disposes of geometries, 
     * materials, and canvas textures to prevent memory leaks.
     */
    dispose() {
        this.group.children.forEach(child => {
            if (child instanceof THREE.Sprite) {
                child.material.map?.dispose();
                child.material.dispose();
            } else if (child instanceof THREE.Mesh) {
                child.geometry.dispose();
                (child.material as THREE.Material).dispose();
            }
        });
    }
}