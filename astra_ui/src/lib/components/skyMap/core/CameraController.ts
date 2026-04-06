// src/lib/components/skyMap/core/CameraController.ts

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { FOV_DEFAULT, FOV_MIN, FOV_MAX, ZOOM_SPEED, EYE_LEVEL, CAMERA_SPEED } from '../utils/const';

/**
 * CameraController
 * 
 * Manages the Three.js PerspectiveCamera and OrbitControls,
 * with a custom FOV-based zooming to simulate optical zoom.
 */
export class CameraController {
    public camera: THREE.PerspectiveCamera;
    public controls: OrbitControls;

    private initialPinchDistance: number | null = null;
    private container: HTMLElement;

    constructor(container: HTMLElement) {
        this.container = container;
        // Initialize camera with a wide default Field of View
        this.camera = new THREE.PerspectiveCamera(FOV_DEFAULT, container.clientWidth / container.clientHeight, 0.1, 2000);

        // Set camera at human eye level
        this.camera.position.set(0, EYE_LEVEL, 0);

        // Initialize OrbitControls for looking around
        this.controls = new OrbitControls(this.camera, container);
        this.controls.enableDamping = true; // Smooth deceleration to camera movements
        this.controls.dampingFactor = 0.05;
        this.controls.enablePan = false; // Disable panning (user at centre)
        this.controls.enableZoom = false; // Disable physical zoom (handled via FOV)
        this.controls.rotateSpeed = CAMERA_SPEED;

        // Point the camera initially towards the North horizon
        this.controls.target.set(0, EYE_LEVEL, -1);
        this.controls.update();

        // ── Event Listeners ──
        // Desktop (Mouse Wheel)
        this.container.addEventListener('wheel', this.onWheel, { passive: false });
        
        // Mobile (Touch Pinch)
        this.container.addEventListener('touchstart', this.onTouchStart, { passive: false });
        this.container.addEventListener('touchmove', this.onTouchMove, { passive: false });
        this.container.addEventListener('touchend', this.onTouchEnd);
    }

    /**
     * Custom zoom handler using the mouse wheel (Desktop).
     */
    private onWheel = (e: WheelEvent) => {
        e.preventDefault();
        this.applyZoom(e.deltaY * ZOOM_SPEED);
    };

    /**
     * Initializes pinch distance when two fingers touch the screen (Mobile).
     */
    private onTouchStart = (e: TouchEvent) => {
        if (e.touches.length === 2) {
            e.preventDefault(); // Prevent accidental page scrolling
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            this.initialPinchDistance = Math.hypot(dx, dy);
        }
    };

    /**
     * Calculates the change in pinch distance and applies zoom (Mobile).
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
     */
    private onTouchEnd = (e: TouchEvent) => {
        if (e.touches.length < 2) {
            this.initialPinchDistance = null;
        }
    };

    /**
     * Modifies the camera's Field of View (FOV) instead of moving its Z position.
     * Shared logic for both Mouse Wheel and Touch Pinch.
     */
    private applyZoom(delta: number) {
        // Calculate new FOV within the allowed min/max boundaries
        this.camera.fov = Math.max(FOV_MIN, Math.min(FOV_MAX, this.camera.fov + delta));
        this.camera.updateProjectionMatrix();
        
        // Dynamically adjust rotation sensitivity based on zoom level.
        this.controls.rotateSpeed = CAMERA_SPEED * (this.camera.fov / FOV_DEFAULT);
    }

    /**
     * Should be called in the main animation loop to update damping physics.
     */
    update() {
        this.controls.update();
    }

    /**
     * Adjusts the camera projection when the viewport size changes.
     */
    resize(width: number, height: number) {
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
    }

    /**
     * Cleans up event listeners and controls when destroyed.
     */
    dispose() {
        this.container.removeEventListener('wheel', this.onWheel);
        this.container.removeEventListener('touchstart', this.onTouchStart);
        this.container.removeEventListener('touchmove', this.onTouchMove);
        this.container.removeEventListener('touchend', this.onTouchEnd);
        this.controls.dispose();
    }
}