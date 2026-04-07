// src/lib/components/skyMap/core/SelectionController.ts

import * as THREE from 'three';
import { CameraController } from './CameraController';
import { Planetary } from '../entities/Planetary';
import { Sidereal } from '../entities/Sidereal';
import { TargetReticle } from '../entities/TargetReticle';
import { skyEngine } from '$lib/stores/skyEngine.svelte';
import { selectionStore } from '$lib/stores/activeSelection.svelte'; 

export class SelectionController {
    private raycaster: THREE.Raycaster = new THREE.Raycaster();
    private pointer: THREE.Vector2 = new THREE.Vector2();
    private pointerDownPos = { x: 0, y: 0 }; // Distinguish click from drag
    private isDragging: boolean = false;
    private selectedId: string | null = null;

    constructor(
        private container: HTMLDivElement,
        private cameraCtrl: CameraController,
        private planetary: Planetary,
        private sidereal: Sidereal,
        private targetReticle: TargetReticle
    ) {
        // Ray hitbox
        this.raycaster.params.Points.threshold = 10;

        // Listeners
        this.container.addEventListener('pointerdown', this.onPointerDown);
        this.container.addEventListener('pointermove', this.onPointerMove);
        this.container.addEventListener('pointerup', this.onPointerUp);
    }

    /** Save the initial position for pointer */
    private onPointerDown = (event: PointerEvent) => {
        this.pointerDownPos = { x: event.clientX, y: event.clientY };
        this.isDragging = true;
        this.container.style.cursor = 'grabbing'; 
    };

    /** 
     * Listens everytime for the pointer
     * If is a click, checks if there's an object behind to activate the cursor
     */
    private onPointerMove = (event: PointerEvent) => {
        if (this.isDragging) return;

        const rect = this.container.getBoundingClientRect();
        this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.pointer, this.cameraCtrl.camera);

        const intersects = this.raycaster.intersectObjects([
            this.planetary.getPointsMesh(),
            this.sidereal.getPointsMesh()
        ], false);

        // Activate cursor detection
        this.container.style.cursor = intersects.length > 0 ? 'pointer' : 'default';
    };

    /** 
     * Check if has been a drag. If not, checks the object behind with the raycaster
     */
    private onPointerUp = (event: PointerEvent) => {
        this.isDragging = false;

        // Update for the pointer
        this.onPointerMove(event);

        const deltaX = Math.abs(event.clientX - this.pointerDownPos.x);
        const deltaY = Math.abs(event.clientY - this.pointerDownPos.y);
        
        // Dragging detected, so cancel
        if (deltaX > 5 || deltaY > 5) return;

        const rect = this.container.getBoundingClientRect();
        this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.pointer, this.cameraCtrl.camera);

        // Shoot ray to planetary and sidereal objects
        const intersects = this.raycaster.intersectObjects([
            this.planetary.getPointsMesh(),
            this.sidereal.getPointsMesh()
        ], false);

        if (intersects.length > 0) {
            // Get the nearest hit
            const hit = intersects[0];
            const index = hit.index;
            let isPlanet = false;
            let foundId: string | null = null;

            if (index !== undefined) {
                if (hit.object === this.planetary.getPointsMesh()) {
                    foundId = this.planetary.getIdByIndex(index);
                    isPlanet = true;
                } else if (hit.object === this.sidereal.getPointsMesh()) {
                    foundId = this.sidereal.getIdByIndex(index);
                }
            }

            if (foundId && foundId !== this.selectedId) {
                this.selectedId = foundId;
                
                // Get size and colour of the object
                const geometry = (hit.object as THREE.Points).geometry;
                const baseSize = geometry.attributes.size.getX(index!);
                
                const r = geometry.attributes.color.getX(index!);
                const g = geometry.attributes.color.getY(index!);
                const b = geometry.attributes.color.getZ(index!);
                const hexColor = '#' + new THREE.Color(r, g, b).getHexString();

                // Activate crosshair
                this.targetReticle.lockOn(isPlanet, hexColor, baseSize);
                            
                // Move to selected object
                const pos = skyEngine.positions.get(foundId);
                if(pos) this.cameraCtrl.flyTo(pos.alt, pos.az);
                selectionStore.targetId = foundId;
                console.log("Selected object:", foundId);
            }
        } else {
            // Void click -> clear selection
            this.selectedId = null;
            this.targetReticle.hide();
            selectionStore.clear();
        }
    };

    dispose() {
        this.container.removeEventListener('pointerdown', this.onPointerDown);
        this.container.removeEventListener('pointermove', this.onPointerMove);
        this.container.removeEventListener('pointerup', this.onPointerUp);
    }
}