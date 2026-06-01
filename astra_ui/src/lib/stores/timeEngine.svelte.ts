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

// src/lib/stores/timeEngine.svelte.ts
import { browser } from '$app/environment';
import { locStore } from './location.svelte';

/**
 * TimeEngine manages the simulation time of the application.
 * It supports real-time playback, custom playback rates, and seeking to specific dates.
 */
class TimeEngine {
    /** The current simulation time in milliseconds (Unix timestamp). */
    targetTime = $state<number>(Date.now());
    /** The multiplier for time progression (e.g., 2 for double speed, -1 for reverse). */
    playbackRate = $state<number>(1);
    /** Whether the time clock is currently running. */
    isPlaying = $state<boolean>(false);
    /** Whether the clock is synchronized with the actual system time. */
    isLive = $state<boolean>(true);

    /** The real-world timestamp (ms) of the last animation frame. */
    private lastFrameTime = 0;
    /** The ID of the current requestAnimationFrame, used for cancellation. */
    private animationFrameId: number | null = null;

    
    /** 
     * The current simulation time as a Date object in UTC.
     */
    current = $derived(new Date(this.targetTime));
    
    /** 
     * The current simulation time adjusted to the active location's local timezone.
     */
    local = $derived(new Date(this.targetTime + (locStore.active?.timezone || 0) * 3600000));

    // --- Controls ---
    /**
     * Toggles live mode. If true, synchronizes the simulation time with system time.
     * @param val True to enable live mode, false to disable.
     */
    setLive(val: boolean) {
        this.isLive = val;
        if (val) { 
            this.playbackRate = 1; 
            this.targetTime = Date.now();
            if (!this.isPlaying) this.play(); 
        }
    }

    /**
     * Starts the time progression loop.
     */
    play() {
        if (this.isPlaying || !browser) return;
        this.isPlaying = true;
        this.lastFrameTime = performance.now();
        this.loop(this.lastFrameTime);
    }

    /**
     * Stops the time progression loop and disables live mode.
     */
    pause() {
        this.isPlaying = false;
        this.isLive = false;
        if (this.animationFrameId !== null) cancelAnimationFrame(this.animationFrameId!);
    }

    /**
     * Sets the simulation time to a specific date and disables live mode.
     * @param date The date to set (Date object, ISO string, or timestamp).
     */
    setTime(date: Date | string | number) {
        this.isLive = false;
        this.playbackRate = 1;
        this.targetTime = new Date(date).getTime();
    }

    /**
     * Sets the playback rate and starts progression if not already playing.
     * Disables live mode if the rate is not 1.
     * @param speed The new playback rate.
     */
    setRate(speed: number) {
        this.playbackRate = speed;
        if (speed !== 1) {
            this.isLive = false;
        }
        if (!this.isPlaying) {
            this.play();
        }
    }

    /**
     * The main animation loop that updates targetTime based on the playback rate and elapsed real time.
     * @param currentRealTime The high-resolution timestamp from requestAnimationFrame.
     */
    private loop(currentRealTime: number) {
        if (!this.isPlaying) return;
        if (this.isLive) {
            this.targetTime = Date.now();
        } else {
            const deltaMs = currentRealTime - this.lastFrameTime;
            this.targetTime += deltaMs * this.playbackRate;
        }
        this.lastFrameTime = currentRealTime;
        this.animationFrameId = requestAnimationFrame((t) => this.loop(t));
    }
}

/**
 * Singleton instance of the TimeEngine.
 */
export const timeEngine = new TimeEngine();