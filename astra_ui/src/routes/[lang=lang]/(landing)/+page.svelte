<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { page } from '$app/state';
    

    import { Eye, Navigation, Zap, GraduationCap, Globe, Moon, ChevronRight, Menu, X, Crosshair } from 'lucide-svelte';

    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import FeatureCard from '$lib/components/landingComponents/FeatureCard.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import LanguageSelector from '$lib/components/LanguageSwitcher.svelte'

    let isMenuOpen = $state(false);
    let scrolled = $state(false);

    $effect(() => {
        const handleScroll = () => (scrolled = window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    });

    // Feature data
    const features = $derived([
        { icon: Eye,            title: m.landing_feature_obs_title(),       description: m.landing_feature_obs_desc() },
        { icon: Navigation,     title: m.landing_feature_telescope_title(), description: m.landing_feature_telescope_desc() },
        { icon: Zap,            title: m.landing_feature_ai_title(),        description: m.landing_feature_ai_desc() },
        { icon: GraduationCap,  title: m.landing_feature_learn_title(),     description: m.landing_feature_learn_desc() },
        { icon: Globe,          title: m.landing_feature_global_title(),    description: m.landing_feature_global_desc() },
        { icon: Moon,           title: m.landing_feature_night_title(),     description: m.landing_feature_night_desc() }
    ]);

    // Navigation links
    const navLinks = $derived([
        { name: m.landing_nav_features(),   href: '#features' },
        { name: m.landing_nav_technology(), href: '#technology' },
        { name: m.landing_nav_docs(),   href: '#' }
    ]);


	// Tecnology data
    const stats = $derived([
        { label: m.landing_stat_telescopes(),  value: m.landing_stat_indi() },
        { label: m.landing_stat_objects(),     value: "18K+" },
        { label: m.landing_stat_guiding(),   value: "99.9%" },
        { label: m.landing_stat_satisfaction(),value: "4.9/5" }
    ]);

    // Footer Product Links
    const footerProductLinks = $derived([
        { name: m.landing_footer_feat(), href: '#features' },
        { name: m.landing_footer_tele(), href: "#" },
        { name: m.landing_footer_docs(), href: "#" },
        { name: m.landing_footer_log(),  href: "#" }
    ]);

    // Footer Community Links
    const footerCommunityLinks = $derived([
        { name: m.landing_footer_cont(),  href: "#" },
        { name: m.landing_footer_contact(),href: "#" }
    ]);

    const socialLinks = ["GitHub", "Twitter", "Discord", "Instagram"];
    const currentYear = new Date().getFullYear();
</script>

<svelte:head>
    <title>{m.name().toUpperCase()} - {m.name_sign()}</title>
    <meta name="description" content={m.name().toUpperCase() + "-" + m.name_sign()} />
</svelte:head>

<div class="min-h-screen bg-astralanding-dark text-slate-200 selection:bg-blue-500/30 selection:text-white">
    
    <Stars />

    <!-- Navigation Bar -->
    <nav class="fixed top-0 left-0 right-0 px-8 z-50 transition-all duration-500 border-b border-white/10 {scrolled ? 'bg-astralanding-dark/80 backdrop-blur-lg py-4' : 'bg-transparent py-8 backdrop-blur-md'}">
        <div class="flex items-center justify-between">

            <a href="/{page.params.lang ?? ''}"  class="flex items-center gap-4 group transition-opacity hover:opacity-70">
                <AppLogo class="w-10 h-10" />
                <div class="hidden sm:block">
                    <h1 class="text-xl font-bold text-white">{m.name().toUpperCase()}</h1>
                    <p class="text-[10px] tracking-widest text-blue-300 font-medium">{m.name_sign().toUpperCase()}</p>
                </div>
            </a>

            <!-- Desktop menu: md and forward -->
            <div class="hidden md:flex items-center gap-6 xl:gap-8">
                {#each navLinks as link}
                    <a href={link.href} class="text-sm font-medium text-slate-400 hover:text-white transition-colors">
                        {link.name}
                    </a>
                {/each}
                <div class="w-px h-6 bg-white/10"></div>
                <LanguageSelector
                    classButton="text-white bg-white/5 border-white/10 rounded-full hover:bg-white/10 backdrop-blur-sm"
                    classDropdown="bg-astralanding-dark/95 border-white/10 rounded-xl"
                    classActive="bg-blue-500/10 text-blue-400 font-semibold"
                    classInactive="text-slate-300 hover:bg-white/10 hover:text-white" />
                <a href="/dashboard" 
                    // class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-sm font-bold transition-all hover:shadow-[0_0_20px_rgba(37,99,235,0.4)] whitespace-nowrap">
                    class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-sm font-bold transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/30 whitespace-nowrap">
                    {m.landing_cta()}
                </a>
            </div>

            <!-- Hamburger for mobile view -->
            <button class="md:hidden text-white p-2" onclick={() => isMenuOpen = !isMenuOpen}>
                {#if isMenuOpen}<X />{:else}<Menu />{/if}
            </button>
        </div>

        <!-- Mobile menu panel -->
        {#if isMenuOpen}
            <div class="md:hidden mt-4 pb-4 flex flex-col gap-4 border-t border-white/10 pt-4">
                {#each navLinks as link}
                    <a href={link.href} onclick={() => isMenuOpen = false}
                    class="text-sm font-medium text-slate-300 hover:text-white transition-colors py-1">
                        {link.name}
                    </a>
                {/each}
                <div class="h-px bg-white/10"></div>
                <LanguageSelector
                    classButton="text-white bg-white/5 border-white/10 rounded-full hover:bg-white/10 backdrop-blur-sm"
                    classDropdown="bg-astralanding-dark/95 border-white/10 rounded-xl"
                    classActive="bg-blue-500/10 text-blue-400 font-semibold"
                    classInactive="text-slate-300 hover:bg-white/10 hover:text-white" />
                <a href="/dashboard" class="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-sm font-bold text-center transition-all">
                    {m.landing_cta()}
                </a>
            </div>
        {/if}
    </nav>

    <main>
        <!-- Landing Section -->
        <section class="relative min-h-screen flex flex-col items-center justify-center pt-32 md:pt-40 pb-20 overflow-hidden">
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[150vw] max-w-[1000px] aspect-video bg-blue-600/10 rounded-full blur-[100px] md:blur-[240px] animate-pulse pointer-events-none z-0"></div>
            
            <div class="container mx-auto px-6 relative z-10 text-center">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-medium mb-10">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping"></span>
                    {m.landing_badge()}
                </div>

                <h1 class="text-6xl md:text-8xl font-bold text-white mb-8 tracking-tight leading-[1.1]">
                    {m.landing_hero_prefix()}<br />
                    <span class="inline-block pr-2 pb-1 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500">
                        {m.name().toUpperCase()}
                    </span>
                </h1>

                <p class="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed">
                    {m.landing_hero_subtitle()}
                </p>

                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="/dashboard" class="px-10 py-4 bg-white text-astralanding-dark font-bold rounded-xl hover:bg-blue-200 transition-colors flex items-center justify-center gap-2 group">
                        {m.landing_cta()}
                        <ChevronRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </a>
                    <button class="cursor-pointer px-10 py-4 bg-white/5 border border-white/10 text-white font-bold rounded-xl hover:bg-white/10 transition-all backdrop-blur-md">
                        {m.landing_cta_docs()}
                    </button>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section id="features" class="py-32 container mx-auto px-6">
            <div class="text-center mb-20">
                <h2 class="text-4xl md:text-5xl font-bold text-white mb-4">{m.landing_features_title()}</h2>
                <p class="text-slate-400 max-w-xl mx-auto">{m.landing_features_subtitle()}</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each features as feature}
                    <FeatureCard {...feature} />
                {/each}
            </div>
        </section>

		<section id="technology" class="py-32 relative overflow-hidden jidden">            
            <div class="container mx-auto px-6">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    <div class="relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl transform opacity-20 blur-lg"></div>
                        <div class="relative bg-astralanding-panel rounded-2xl p-8 border border-white/10">
                            <div class="aspect-video rounded-xl overflow-hidden bg-gradient-to-br from-blue-900/20 to-indigo-900/20 flex items-center justify-center">
                                <div class="text-center">
                                    <div class="w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                                        <Crosshair size={56}/>
                                    </div>
                                    <h3 class="text-2xl font-bold text-white mb-2">{m.landing_tech_card_title()}</h3>
                                    <p class="text-slate-400">{m.landing_tech_card_desc()}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h2 class="text-4xl md:text-5xl font-bold text-white mb-8 leading-tight">
                            {m.landing_tech_title_1()} <br />
                            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                                {m.landing_tech_title_2()}
                            </span>
                        </h2>
                        <div class="space-y-6 text-slate-400 mb-8">
                            <p>{m.landing_tech_desc_1()}</p>
                            <p>{m.landing_tech_desc_2()}</p>
                        </div>
                        
                        <div class="grid grid-cols-2 gap-6">
                            {#each stats as stat}
                                <div class="p-6 bg-white/5 rounded-xl border border-white/10">
                                    <div class="text-3xl font-bold text-white mb-1">{stat.value}</div>
                                    <div class="text-sm text-slate-400">{stat.label}</div>
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="download" class="py-32 relative">            
            <div class="container mx-auto px-6 relative z-10">
                <div class="max-w-4xl mx-auto bg-gradient-to-br from-blue-600/10 to-indigo-600/10 rounded-3xl p-12 border border-white/10 backdrop-blur-sm text-center">
                    <!-- <div class="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl transform opacity-15 blur-lg"></div> -->
                    <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
                        {m.landing_end_cta_title()}
                    </h2>
                    <p class="text-lg text-slate-300 mb-10 max-w-2xl mx-auto">
                        {m.landing_end_cta_desc()}
                    </p>
                    
                    <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <a href="/dashboard"  class="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/30">
                            {m.landing_cta()}
                        </a>
                        <button class="w-full sm:w-auto px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-semibold transition-all duration-300 backdrop-blur-sm">
                            {m.landing_cta_gallery()}
                        </button>
                    </div>
                    
                    <p class="mt-6 text-sm text-slate-400">
                        {m.landing_end_cta_disclaimer()}
                    </p>
                </div>
            </div>
        </section>
    </main>

    <footer class="py-12 bg-astralanding-darker border-t border-white/5 relative">
        <div class="px-8">
        
            <div class="grid grid-cols-1 md:grid-cols-4 mb-12">
                
                <!-- Logo and info -->
                <div class="col-span-1 md:col-span-2">
                    <div class="flex items-center space-x-3 mb-6">
                        <AppLogo class="w-12 h-12" />
                        <div>
                            <h3 class="text-2xl font-bold text-white">{m.name().toUpperCase()}</h3>
                            <p class="text-sm text-blue-300">{m.name_sign()}</p>
                        </div>
                    </div>
                    <p class="text-slate-400 max-w-md leading-relaxed">
                        {m.landing_footer_desc()}
                    </p>
                </div>
                
                
                <!-- <div>
                    <h4 class="text-white font-semibold mb-6">{m.landing_footer_product_title()}</h4>
                    <ul class="space-y-4">
                        {#each footerProductLinks as link}
                            <li>
                                <a href={link.href} class="text-slate-400 hover:text-blue-300 transition-colors">{link.name}</a>
                            </li>
                        {/each}
                    </ul>
                </div> -->
                <!-- <div>
                    <h4 class="text-white font-semibold mb-6">{m.landing_footer_community_title()}</h4>
                    <ul class="space-y-4">
                        {#each footerCommunityLinks as link}
                            <li>
                                <a href={link.href} class="text-slate-400 hover:text-blue-300 transition-colors">{link.name}</a>
                            </li>
                        {/each}
                    </ul>
                </div> -->
                
                <div class="col-span-1 md:col-span-2 flex flex-col md:flex-row md:justify-end gap-12 md:gap-48 px-16">
        
                    <!-- Product links -->
                    <div>
                        <h4 class="text-white font-semibold mb-6">{m.landing_footer_product_title()}</h4>
                        <ul class="space-y-4">
                            {#each footerProductLinks as link}
                                <li>
                                    <a href={link.href} class="text-slate-400 hover:text-blue-300 transition-colors">{link.name}</a>
                                </li>
                            {/each}
                        </ul>
                    </div>
                    
                    <!-- Community links -->
                    <div>
                        <h4 class="text-white font-semibold mb-6">{m.landing_footer_community_title()}</h4>
                        <ul class="space-y-4">
                            {#each footerCommunityLinks as link}
                                <li>
                                    <a href={link.href} class="text-slate-400 hover:text-blue-300 transition-colors">{link.name}</a>
                                </li>
                            {/each}
                        </ul>
                    </div>

                </div> 
            </div>
            
            <!-- Info footer -->
            <div class="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between">
                <p class="text-slate-500 text-sm mb-4 md:mb-0">
                    © {currentYear} {m.landing_footer_copyright()}
                </p>
                <div class="flex space-x-6">
                    {#each socialLinks as social}
                        <a href="#" class="text-slate-500 hover:text-blue-300 transition-colors text-sm">
                            {social}
                        </a>
                    {/each}
                </div>
            </div>
        </div>
    </footer>
    </div>
