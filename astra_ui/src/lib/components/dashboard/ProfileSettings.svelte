<script lang="ts">
    import { authStore } from '$lib/stores/auth.svelte';
    import { authAPI } from '$lib/api/auth';
    import * as m from '$lib/paraglide/messages.js';
    import { User as UserIcon, Camera, LoaderCircle, CircleCheck, Save } from 'lucide-svelte';

    let uploading = $state(false);
    let saving = $state(false);
    let successMessage = $state('');
    let errorMessage = $state('');

    let fullName = $state(authStore.user?.full_name ?? '');
    let bio = $state(authStore.user?.bio ?? '');

    async function handleFileChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;

        const file = input.files[0];
        if (!file.type.startsWith('image/')) {
            errorMessage = m.profile_settings_image_validation();
            return;
        }

        uploading = true;
        errorMessage = '';
        successMessage = '';

        try {
            await authAPI.uploadProfilePicture(file);
            await authStore.refreshProfile();
            successMessage = m.profile_settings_photo_success();
        } catch (e) {
            errorMessage = m.profile_settings_photo_error();
            console.error(e);
        } finally {
            uploading = false;
        }
    }

    async function handleSaveProfile() {
        saving = true;
        errorMessage = '';
        successMessage = '';

        try {
            await authAPI.updateProfile({
                full_name: fullName,
                bio: bio
            });
            await authStore.refreshProfile();
            successMessage = m.profile_settings_details_success();
        } catch (e) {
            errorMessage = m.profile_settings_details_error();
            console.error(e);
        } finally {
            saving = false;
        }
    }
</script>

<div class="flex flex-col gap-6 p-1">
    <!-- Profile Picture Section -->
    <div class="flex flex-col items-center gap-4">
        <div class="relative group">
            <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-border bg-surface flex items-center justify-center relative">
                {#if authStore.user?.profile_picture_url}
                    <img src={authStore.user.profile_picture_url} alt="Profile" class="w-full h-full object-cover" />
                {:else}
                    <UserIcon size={48} class="text-copy-secondary" />
                {/if}
                
                {#if uploading}
                    <div class="absolute inset-0 bg-black/50 flex items-center justify-center">
                        <LoaderCircle class="animate-spin text-white" />
                    </div>
                {/if}
            </div>
            
            <label 
                for="photo-upload" 
                class="absolute bottom-0 right-0 p-2 bg-accent hover:bg-accent-hover text-white rounded-full cursor-pointer transition-colors shadow-lg shadow-accent/20"
                title={m.profile_settings_change_photo()}
            >
                <Camera size={16} />
                <input 
                    id="photo-upload" 
                    type="file" 
                    accept="image/*" 
                    class="hidden" 
                    onchange={handleFileChange} 
                    disabled={uploading || saving}
                />
            </label>
        </div>
        
        <div class="text-center">
            <p class="font-bold text-copy-primary">{authStore.user?.username}</p>
            <p class="text-sm text-copy-secondary">{authStore.user?.email}</p>
        </div>
    </div>

    <!-- User Details Section -->
    <div class="flex flex-col gap-4 pt-4 border-t border-border">
        <h3 class="text-sm font-semibold text-copy-primary uppercase tracking-wider">{m.profile_settings_title()}</h3>
        
        <div class="grid grid-cols-1 gap-4">
            <div class="flex flex-col gap-1.5">
                <label for="full_name" class="text-xs text-copy-secondary">{m.profile_settings_full_name()}</label>
                <input
                    id="full_name"
                    type="text"
                    bind:value={fullName}
                    placeholder={m.profile_settings_full_name_placeholder()}
                    class="text-sm font-medium py-2 px-3 bg-surface rounded-lg border border-border focus:border-accent focus:outline-none transition-colors"
                />
            </div>
            
            <div class="flex flex-col gap-1.5">
                <label for="bio" class="text-xs text-copy-secondary">{m.profile_settings_bio()}</label>
                <textarea
                    id="bio"
                    bind:value={bio}
                    placeholder={m.profile_settings_bio_placeholder()}
                    rows="3"
                    class="text-sm font-medium py-2 px-3 bg-surface rounded-lg border border-border focus:border-accent focus:outline-none transition-colors resize-none"
                ></textarea>
            </div>

            <button
                onclick={handleSaveProfile}
                disabled={saving || uploading}
                class="flex items-center justify-center gap-2 w-full py-2.5 bg-accent hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-colors"
            >
                {#if saving}
                    <LoaderCircle size={16} class="animate-spin" />
                {:else}
                    <Save size={16} />
                {/if}
                {m.profile_settings_save()}
            </button>
        </div>
    </div>

    <!-- Read-only Details -->
    <div class="flex flex-col gap-4 pt-4 border-t border-border">
        <h3 class="text-sm font-semibold text-copy-primary uppercase tracking-wider">{m.profile_settings_account_info()}</h3>
        <div class="flex flex-col gap-2">
            <div class="flex justify-between items-center text-sm">
                <span class="text-copy-secondary">{m.profile_settings_member_since()}</span>
                <span class="text-copy-primary font-medium">{new Date(authStore.user?.creation ?? '').toLocaleDateString()}</span>
            </div>
        </div>
    </div>

    {#if errorMessage}
        <div class="p-3 bg-danger-surface text-danger text-sm rounded-lg animate-in fade-in slide-in-from-top-1">
            {errorMessage}
        </div>
    {/if}

    {#if successMessage}
        <div class="p-3 bg-green-500/10 text-green-500 text-sm rounded-lg flex items-center gap-2 animate-in fade-in slide-in-from-top-1">
            <CircleCheck size={16} />
            {successMessage}
        </div>
    {/if}
</div>
