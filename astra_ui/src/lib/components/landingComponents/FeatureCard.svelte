<script lang="ts">
	let { 
        /** Icon component to display in the card */
        icon: Icon, 
        /** Primary title of the feature */
        title, 
        /** Detailed description of the feature */
        description 
    } = $props();
</script>

<div class="group relative p-8 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl hover:bg-white/10 transition-all duration-300 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10">
    <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    <div class="relative z-10">
        <div class="mb-6 p-4 bg-blue-500/10 rounded-xl w-fit group-hover:bg-blue-500/20 transition-colors">
            <Icon class="w-8 h-8 text-blue-300 group-hover:text-blue-200" />
        </div>
        <h3 class="text-xl font-semibold text-white mb-3">{title}</h3>
        <p class="text-slate-400 leading-relaxed">{description}</p>
    </div>
</div>