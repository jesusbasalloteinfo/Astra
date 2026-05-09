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
    public isTracking: boolean = false; // Maintain always centered

    private initialPinchDistance: number | null = null;
    private container: HTMLElement;

    // ── Navigation State ──
    private isFlying: boolean = false;
    private flightTarget: THREE.Vector3 = new THREE.Vector3();

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

        // Abort fly motion
        this.container.addEventListener('pointerdown', this.onPointerDown);

    }

    /**
     * Caslculate the selected object's position
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
     * Starts a smooth movement to the coordinates.
     */
    flyTo(alt: number, az: number) {
        this.calculateFlightTarget(alt, az);
        this.isFlying = true;
    }

    /**
     * Stops the flying momement if user takes control.
     */
    private cancelFlight = () => {
        this.isFlying = false;
        this.isTracking = false;
    };

    /**
     * Follow a selected object
     */
    track(alt: number, az: number) {
        this.calculateFlightTarget(alt, az);
        
        if (!this.isFlying) {
            this.camera.position.copy(this.flightTarget);
        }
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
        } else {
            this.cancelFlight();
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
     * Stop tracking if user makes a click
     */
    private onPointerDown = (e: PointerEvent) => {
        if (e.pointerType !== 'touch') {
            this.cancelFlight(); 
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
     */
    resize(width: number, height: number) {
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
    }

    /**
     * Cleans up event listeners and controls when destroyed.
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