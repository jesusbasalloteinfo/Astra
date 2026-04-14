// src/lib/stores/timeEngine.svelte.ts
import { browser } from '$app/environment';
import { locStore } from './location.svelte';

class TimeEngine {
    targetTime = $state<number>(Date.now());
    playbackRate = $state<number>(1);
    isPlaying = $state<boolean>(false);
    isLive = $state<boolean>(true);

    private lastFrameTime = 0;
    private animationFrameId: number | null = null;

    
    // UTC real time
    current = $derived(new Date(this.targetTime));
    
    // Local time
    local = $derived(new Date(this.targetTime + (locStore.active?.timezone || 0) * 3600000));

    // --- Controls ---
    setLive(val: boolean) {
        this.isLive = val;
        if (val) { 
            this.playbackRate = 1; 
            this.targetTime = Date.now();
            if (!this.isPlaying) this.play(); 
        }
    }

    play() {
        if (this.isPlaying || !browser) return;
        this.isPlaying = true;
        this.lastFrameTime = performance.now();
        this.loop(this.lastFrameTime);
    }

    pause() {
        this.isPlaying = false;
        this.isLive = false;
        if (this.animationFrameId !== null) cancelAnimationFrame(this.animationFrameId!);
    }

    setTime(date: Date | string | number) {
        this.isLive = false;
        this.playbackRate = 1;
        this.targetTime = new Date(date).getTime();
    }

    setRate(speed: number) {
        this.playbackRate = speed;
        if (speed !== 1) {
            this.isLive = false;
        }
        if (!this.isPlaying) {
            this.play();
        }
    }

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

export const timeEngine = new TimeEngine();