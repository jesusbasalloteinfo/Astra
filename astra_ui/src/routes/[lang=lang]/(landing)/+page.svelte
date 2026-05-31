<script lang="ts">
    import * as m from '$lib/paraglide/messages.js';
    import { page } from '$app/state';
    
    import { Eye, Navigation, Zap, GraduationCap, Globe, Moon, ChevronRight, Menu, Crosshair } from 'lucide-svelte';

    import Stars from '$lib/components/landingComponents/Stars.svelte';
    import FeatureCard from '$lib/components/landingComponents/FeatureCard.svelte';
    import AppLogo from '$lib/components/AppLogo.svelte';
    import LanguageSelector from '$lib/components/LanguageSwitcher.svelte';
    import MobileMenu from '$lib/components/landingComponents/MobileMenu.svelte'; 

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
        { name: m.landing_nav_docs(),       href: 'https://github.com/jesusbasalloteinfo/Astra/tree/main/docs' }
    ]);

    // Tecnology data
    const stats = $derived([
        { label: m.landing_stat_telescopes(),  value: m.landing_stat_indi() },
        { label: m.landing_stat_objects(),     value: "16K+" },
        { label: m.landing_stat_architecture(),value: "Distributed" },
        { label: m.landing_stat_license(),     value: "AGPL v3" }
    ]);

    // Footer Product Links
    const footerProductLinks = $derived([
        { name: m.landing_footer_feat(), href: '#features' },
        { name: m.landing_footer_tele(), href: "https://github.com/jesusbasalloteinfo/Astra/blob/main/docs/EDGE_GUIDE.md" },
        { name: m.landing_footer_docs(), href: "https://github.com/jesusbasalloteinfo/Astra/tree/main/docs" },
        { name: m.landing_footer_log(),  href: "https://github.com/jesusbasalloteinfo/Astra/commits/main" }
    ]);

    // Footer Community Links
    const footerCommunityLinks = $derived([
        { name: m.landing_footer_cont(),   href: "https://github.com/jesusbasalloteinfo/Astra/blob/main/CONTRIBUTING.md" },
        { name: m.landing_footer_contact(),href: "https://github.com/jesusbasalloteinfo/Astra/issues" }
    ]);

    const socialLinks = [
        { name: "GitHub", href: "https://github.com/jesusbasalloteinfo/Astra" }
    ];

    const currentYear = new Date().getFullYear();
</script>

<svelte:head>
    <title>{m.name().toUpperCase()} - {m.name_sign()}</title>
    <meta name="description" content={m.name().toUpperCase() + "-" + m.name_sign()} />
</svelte:head>

<div class="min-h-screen bg-astralanding-dark text-slate-200 selection:bg-blue-500/30 selection:text-white">
    
    <Stars />

    <!-- Navigation Bar -->
    <nav class="fixed top-0 left-0 right-0 px-6 lg:px-8 z-50 transition-all duration-500 border-b border-white/10 {scrolled ? 'bg-astralanding-dark/80 backdrop-blur-lg py-3' : 'bg-transparent py-4 lg:py-6 backdrop-blur-md'}">
        <div class="flex items-center justify-between">

            <a href="/{page.params.lang ?? ''}" class="flex items-center gap-3 lg:gap-4 group transition-opacity hover:opacity-70">
                <AppLogo class="w-8 h-8 lg:w-10 lg:h-10 shrink-0" />
                <div class="flex flex-col justify-center">
                    <h1 class="text-lg lg:text-xl font-bold text-white leading-none">{m.name().toUpperCase()}</h1>
                    <p class="hidden lg:block text-[9px] tracking-widest text-blue-300 font-medium leading-tight mt-1 max-w-62.5">
                        {m.name_sign().toUpperCase()}
                    </p>
                </div>
            </a>

            <div class="hidden lg:flex items-center gap-6 xl:gap-8">
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
                    class="px-6 py-2.5 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-sm font-bold transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/30 whitespace-nowrap">
                    {m.landing_cta()}
                </a>
            </div>

            <button class="lg:hidden text-white p-2 hover:bg-white/5 rounded-lg transition-colors" onclick={() => isMenuOpen = true}>
                <Menu />
            </button>
        </div>
    </nav>

    <MobileMenu bind:isOpen={isMenuOpen} {navLinks} />

    <main>
        <!-- Landing Section -->
        <section class="relative min-h-svh flex flex-col items-center justify-center pt-28 md:pt-40 landscape:pt-24 pb-16 md:pb-20 overflow-hidden">
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[150vw] max-w-250 aspect-video bg-blue-600/10 rounded-full blur-[100px] md:blur-[240px] animate-pulse pointer-events-none z-0"></div>
            
            <div class="container mx-auto px-6 relative z-10 text-center">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-medium mb-8 md:mb-10 landscape:mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping"></span>
                    {m.landing_badge()}
                </div>

                <h1 class="text-4xl sm:text-6xl md:text-8xl landscape:text-5xl font-bold text-white mb-6 md:mb-8 tracking-tight leading-[1.1]">
                    {m.landing_hero_prefix()}<br />
                    <span class="inline-block pr-2 pb-1 text-transparent bg-clip-text bg-linear-to-r from-blue-400 via-indigo-400 to-purple-500">
                        {m.name().toUpperCase()}
                    </span>
                </h1>

                <p class="text-base sm:text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 md:mb-12 landscape:mb-8 leading-relaxed px-4">
                    {m.landing_hero_subtitle()}
                </p>

                <div class="flex flex-col sm:flex-row landscape:flex-row gap-4 justify-center">
                    <a href="/dashboard" class="w-full sm:w-auto px-8 md:px-10 py-4 bg-white text-astralanding-dark font-bold rounded-xl hover:bg-blue-200 transition-colors flex items-center justify-center gap-2 group">
                        {m.landing_cta()}
                        <ChevronRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </a>
                    <a href="https://github.com/jesusbasalloteinfo/Astra/tree/main/docs" class="w-full sm:w-auto px-8 md:px-10 py-4 bg-white/5 border border-white/10 text-white font-bold rounded-xl hover:bg-white/10 transition-all backdrop-blur-md flex items-center justify-center">
                        {m.landing_cta_docs()}
                    </a>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section id="features" class="py-16 md:py-32 landscape:py-16 container mx-auto px-6">
            <div class="text-center mb-12 md:mb-20 landscape:mb-10">
                <h2 class="text-3xl md:text-5xl font-bold text-white mb-4">{m.landing_features_title()}</h2>
                <p class="text-sm md:text-base text-slate-400 max-w-xl mx-auto">{m.landing_features_subtitle()}</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each features as feature}
                    <FeatureCard {...feature} />
                {/each}
            </div>
        </section>

        <!-- Technology Section -->
        <section id="technology" class="py-16 md:py-32 landscape:py-16 relative overflow-hidden">            
            <div class="container mx-auto px-6">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
                    
                    <div class="relative max-w-lg mx-auto lg:max-w-none lg:mx-0">
                        <div class="absolute inset-0 bg-linear-to-r from-blue-500 to-indigo-500 rounded-2xl transform opacity-20 blur-lg"></div>
                        
                        <div class="relative bg-astralanding-panel rounded-2xl p-4 md:p-8 border border-white/10">
                            <div class="rounded-xl overflow-hidden bg-linear-to-br from-blue-900/20 to-indigo-900/20 flex items-center justify-center aspect-5/4 sm:aspect-video px-5 sm:p-8">
                                <div class="text-center max-w-sm mx-auto">
                                    <div class="w-16 h-16 md:w-24 md:h-24 mx-auto mb-5 md:mb-6 bg-linear-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/30">
                                        <Crosshair class="w-8 h-8 md:w-14 md:h-14 text-white"/>
                                    </div>
                                    <h3 class="text-lg md:text-2xl font-bold text-white mb-2 md:mb-3">{m.landing_tech_card_title()}</h3>
                                    <p class="text-sm md:text-base text-slate-400 leading-relaxed">{m.landing_tech_card_desc()}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h2 class="text-3xl md:text-5xl font-bold text-white mb-6 md:mb-8 leading-tight">
                            {m.landing_tech_title_1()} <br />
                            <span class="text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-indigo-400">
                                {m.landing_tech_title_2()}
                            </span>
                        </h2>
                        <div class="space-y-4 md:space-y-6 text-sm md:text-base text-slate-400 mb-8 max-w-2xl">
                            <p>{m.landing_tech_desc_1()}</p>
                            <p>{m.landing_tech_desc_2()}</p>
                        </div>
                        
                        <div class="grid grid-cols-2 gap-4 md:gap-6">
                            {#each stats as stat}
                                <div class="p-4 md:p-6 bg-white/5 rounded-xl border border-white/10">
                                    <div class="text-2xl md:text-3xl font-bold text-white mb-1">{stat.value}</div>
                                    <div class="text-xs md:text-sm text-slate-400">{stat.label}</div>
                                </div>
                            {/each}
                        </div>
                    </div>

                </div>
            </div>
        </section>

        <!-- Download Section -->
        <section id="download" class="py-16 md:py-32 landscape:py-16 relative">            
            <div class="container mx-auto px-6 relative z-10">
                <div class="max-w-4xl mx-auto bg-linear-to-br from-blue-600/10 to-indigo-600/10 rounded-3xl p-8 md:p-12 border border-white/10 backdrop-blur-sm text-center">
                    <h2 class="text-3xl md:text-5xl font-bold text-white mb-4 md:mb-6">
                        {m.landing_end_cta_title()}
                    </h2>
                    <p class="text-base md:text-lg text-slate-300 mb-8 md:mb-10 max-w-2xl mx-auto">
                        {m.landing_end_cta_desc()}
                    </p>
                    
                    <div class="flex flex-col sm:flex-row landscape:flex-row items-center justify-center gap-4">
                        <a href="/dashboard" class="w-full sm:w-auto px-8 py-4 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/30">
                            {m.landing_cta()}
                        </a>
                        <a href="https://github.com/jesusbasalloteinfo/Astra" class="w-full sm:w-auto px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-semibold transition-all duration-300 backdrop-blur-sm flex items-center justify-center">
                            {m.landing_cta_gallery()}
                        </a>
                    </div>
                    
                    <p class="mt-6 text-xs md:text-sm text-slate-400">
                        {m.landing_end_cta_disclaimer()}
                    </p>
                </div>
            </div>
        </section>
    </main>

    <footer class="py-10 md:py-12 bg-astralanding-darker border-t border-white/5 relative">
        <div class="container mx-auto px-6 md:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-10 md:gap-8 mb-10 md:mb-12">
                
                <!-- Logo and info -->
                <div class="col-span-1 md:col-span-2">
                    <div class="flex items-center space-x-3 mb-4 md:mb-6">
                        <AppLogo class="w-10 h-10 md:w-12 md:h-12" />
                        <div>
                            <h3 class="text-xl md:text-2xl font-bold text-white">{m.name().toUpperCase()}</h3>
                            <p class="text-xs md:text-sm text-blue-300">{m.name_sign()}</p>
                        </div>
                    </div>
                    <p class="text-sm md:text-base text-slate-400 max-w-md leading-relaxed">
                        {m.landing_footer_desc()}
                    </p>
                </div>
                
                <!-- Links -->
                <div class="col-span-1 md:col-span-2 flex flex-col sm:flex-row md:justify-end gap-10 sm:gap-16 md:gap-24 lg:gap-48 px-0 md:px-16">
                    <!-- Product links -->
                    <div>
                        <h4 class="text-white font-semibold mb-4 md:mb-6">{m.landing_footer_product_title()}</h4>
                        <ul class="space-y-3 md:space-y-4">
                            {#each footerProductLinks as link}
                                <li>
                                    <a href={link.href} class="text-sm md:text-base text-slate-400 hover:text-blue-300 transition-colors">{link.name}</a>
                                </li>
                            {/each}
                        </ul>
                    </div>
                    
                    <!-- Community links -->
                    <div>
                        <h4 class="text-white font-semibold mb-4 md:mb-6">{m.landing_footer_community_title()}</h4>
                        <ul class="space-y-3 md:space-y-4">
                            {#each footerCommunityLinks as link}
                                <li>
                                    <a href={link.href} class="text-sm md:text-base text-slate-400 hover:text-blue-300 transition-colors">{link.name}</a>
                                </li>
                            {/each}
                        </ul>
                    </div>
                </div> 
            </div>
            
            <!-- Info footer -->
            <div class="border-t border-white/5 pt-6 md:pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
                <p class="text-slate-500 text-xs md:text-sm text-center md:text-left">
                    © {currentYear} {m.landing_footer_copyright()}
                </p>
                <div class="flex flex-wrap justify-center space-x-4 md:space-x-6">
                    {#each socialLinks as social}
                        <a href={social.href} class="text-slate-500 hover:text-blue-300 transition-colors text-xs md:text-sm">
                            {social.name}
                        </a>
                    {/each}
                </div>
            </div>
        </div>
    </footer>
</div>