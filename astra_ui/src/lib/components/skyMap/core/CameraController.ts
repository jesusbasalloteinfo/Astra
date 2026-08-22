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

// src/lib/components/skyMap/core/CameraController.ts

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { FOV_DEFAULT, FOV_MIN, FOV_MAX, ZOOM_SPEED, CAMERA_SPEED } from '../utils/const';

/**
 * CameraController
 * 
 * Manages the Three.js PerspectiveCamera and OrbitControls,
 * with a custom FOV-based zooming to simulate optical zoom.
 */
export class CameraController {
    /** The Three.js perspective camera. */
    public camera: THREE.PerspectiveCamera;
    /** The orbit controls for camera interaction. */
    public controls: OrbitControls;
    /** Whether the camera is currently tracking a target. */
    public isTracking: boolean = false; // Maintain always centered

    /** Initial distance for pinch-to-zoom on mobile. */
    private initialPinchDistance: number | null = null;
    /** The HTML container element for the renderer. */
    private container: HTMLElement;

    // ── Navigation State ──
    /** Whether the camera is currently in a "fly-to" animation. */
    private isFlying: boolean = false;
    /** The target position for the "fly-to" animation. */
    private flightTarget: THREE.Vector3 = new THREE.Vector3();

    /**
     * Creates an instance of CameraController.
     * @param {HTMLElement} container - The HTML element that contains the SkyMap.
     */
    constructor(container: HTMLElement) {
        this.container = container;
        // Initialize camera with a wide default Field of View
        this.camera = new THREE.PerspectiveCamera(FOV_DEFAULT, container.clientWidth / container.clientHeight, 0.1, 2000);

        // Set camera at origin looking at center
        this.camera.position.set(0, 0, 0.1);

        // Initialize OrbitControls for looking around
        this.controls = new OrbitControls(this.camera, container);
        this.controls.enableDamping = true; // Smooth deceleration to camera movements
        this.controls.dampingFactor = 0.05;
        this.controls.enablePan = false; // Disable panning (user at centre)
        this.controls.enableZoom = false; // Disable physical zoom (handled via FOV)
        this.controls.rotateSpeed = CAMERA_SPEED;

        // Point the camera initially towards the North horizon (target at origin, camera at +Z)
        this.controls.target.set(0, 0, 0);
        this.controls.update();

        // ── Event Listeners ──
        // Desktop (Mouse Wheel)
        this.container.addEventListener('wheel', this.onWheel, { passive: false });
        
        // Mobile (Touch Pinch)
        this.container.addEventListener('touchstart', this.onTouchStart, { passive: false });
        this.container.addEventListener('touchmove', this.onTouchMove, { passive: false });
        this.container.addEventListener('touchend', this.onTouchEnd);

        // Abort fly motion
        this.container.addEventListener('pointerdown', this.onPointerDown);

    }

    /**
     * Calculates the flight target position based on altitude and azimuth.
     * Uses a spherical-to-Cartesian transformation where:
     * - Altitude (alt) is the angle above the horizon.
     * - Azimuth (az) is the angle from North (0°) clockwise.
     * @param {number} alt - Altitude in degrees.
     * @param {number} az - Azimuth in degrees.
     * @private
     */
    private calculateFlightTarget(alt: number, az: number) {
        const altRad = alt * (Math.PI / 180);
        const azRad  = (180 - az) * (Math.PI / 180);

        const dirX = Math.cos(altRad) * Math.sin(azRad);
        const dirY = Math.sin(altRad);
        const dirZ = Math.cos(altRad) * Math.cos(azRad);

        this.flightTarget.set(
            this.controls.target.x - (dirX * 0.1),
            this.controls.target.y - (dirY * 0.1),
            this.controls.target.z - (dirZ * 0.1)
        );
    }

    /**
     * Starts a smooth "fly-to" movement to the specified celestial coordinates.
     * @param {number} alt - Altitude in degrees.
     * @param {number} az - Azimuth in degrees.
     */
    flyTo(alt: number, az: number) {
        this.calculateFlightTarget(alt, az);
        this.isFlying = true;
    }

    /**
     * Stops the flying movement and tracking if the user takes control.
     * @private
     */
    private cancelFlight = () => {
        this.isFlying = false;
        this.isTracking = false;
    };

    /**
     * Smoothly follows a selected object based on its altitude and azimuth.
     * @param {number} alt - Altitude in degrees.
     * @param {number} az - Azimuth in degrees.
     */
    track(alt: number, az: number) {
        this.calculateFlightTarget(alt, az);
        
        if (!this.isFlying) {
            this.camera.position.copy(this.flightTarget);
        }
    }


    /**
     * Custom zoom handler using the mouse wheel (Desktop).
     * Modifies the FOV to simulate zooming.
     * @param {WheelEvent} e - The wheel event.
     * @private
     */
    private onWheel = (e: WheelEvent) => {
        e.preventDefault();
        this.applyZoom(e.deltaY * ZOOM_SPEED);
    };

    /**
     * Initializes pinch distance when two fingers touch the screen (Mobile).
     * @param {TouchEvent} e - The touch event.
     * @private
     */
    private onTouchStart = (e: TouchEvent) => {
        if (e.touches.length === 2) {
            e.preventDefault(); // Prevent accidental page scrolling
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            this.initialPinchDistance = Math.hypot(dx, dy);
        } else {
            this.cancelFlight();
        }
    };

    /**
     * Calculates the change in pinch distance and applies zoom (Mobile).
     * @param {TouchEvent} e - The touch event.
     * @private
     */
    private onTouchMove = (e: TouchEvent) => {
        if (e.touches.length === 2 && this.initialPinchDistance !== null) {
            e.preventDefault(); // Prevent native browser zoom/scroll
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            const currentPinchDistance = Math.hypot(dx, dy);

            // The difference between initial and current distance
            const delta = this.initialPinchDistance - currentPinchDistance;
            
            // Adjust sensitivity for touch
            const touchZoomSpeed = 0.15; 
            this.applyZoom(delta * touchZoomSpeed);

            // Update initial distance for the next frame of the movement
            this.initialPinchDistance = currentPinchDistance;
        }
    };

    /**
     * Resets pinch state when fingers are lifted.
     * @param {TouchEvent} e - The touch event.
     * @private
     */
    private onTouchEnd = (e: TouchEvent) => {
        if (e.touches.length < 2) {
            this.initialPinchDistance = null;
        }
    };

    /**
     * Stops tracking and flight animation if the user clicks or interacts.
     * @param {PointerEvent} e - The pointer event.
     * @private
     */
    private onPointerDown = (e: PointerEvent) => {
        if (e.pointerType !== 'touch') {
            this.cancelFlight(); 
        }
    };

    /**
     * Modifies the camera's Field of View (FOV) instead of moving its Z position.
     * Shared logic for both Mouse Wheel and Touch Pinch.
     * @param {number} delta - The amount to change the zoom by.
     * @private
     */
    private applyZoom(delta: number) {
        // Calculate new FOV within the allowed min/max boundaries
        this.camera.fov = Math.max(FOV_MIN, Math.min(FOV_MAX, this.camera.fov + delta));
        this.camera.updateProjectionMatrix();
        
        // Dynamically adjust rotation sensitivity based on zoom level.
        this.controls.rotateSpeed = CAMERA_SPEED * (this.camera.fov / FOV_DEFAULT);
    }

    /**
     * Updates the camera state, including damping physics and flight animations.
     * Should be called in the main animation loop.
     */
    update() {
        if (this.isFlying) {
            // Get the relative offsets
            const currentOffset = this.camera.position.clone().sub(this.controls.target);
            const targetOffset = this.flightTarget.clone().sub(this.controls.target);
            
            if (currentOffset.distanceTo(targetOffset) < 0.001) {
                this.isFlying = false;
                this.camera.position.copy(this.flightTarget);
            } else {
                currentOffset.lerp(targetOffset, 0.05).setLength(0.1);
                this.camera.position.copy(this.controls.target).add(currentOffset);
            }
        }
        this.controls.update();
    }

    /**
     * Adjusts the camera projection when the viewport size changes.
     * @param {number} width - New viewport width.
     * @param {number} height - New viewport height.
     */
    resize(width: number, height: number) {
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
    }

    /**
     * Cleans up event listeners and controls when the controller is destroyed.
     */
    dispose() {
        this.container.removeEventListener('pointerdown', this.cancelFlight);
        this.container.removeEventListener('wheel', this.onWheel);
        this.container.removeEventListener('touchstart', this.onTouchStart);
        this.container.removeEventListener('touchmove', this.onTouchMove);
        this.container.removeEventListener('touchend', this.onTouchEnd);
        this.controls.dispose();
    }
}