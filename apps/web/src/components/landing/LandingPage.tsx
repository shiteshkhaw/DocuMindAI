"use client";

import React from "react";
import Navigation from "./Navigation";
import Hero from "./Hero";
import SocialProof from "./SocialProof";
import FeatureGrid from "./FeatureGrid";
import InteractiveDemo from "./InteractiveDemo";
import ArchitectureOverview from "./ArchitectureOverview";
import SecurityGrid from "./SecurityGrid";
import FAQ from "./FAQ";
import CTASection from "./CTASection";
import Footer from "./Footer";
import { DESIGN_TOKENS } from "./landing-config";

export default function LandingPage() {
  return (
    <div
      className={`min-h-screen ${DESIGN_TOKENS.colors.background} ${DESIGN_TOKENS.colors.text} transition-colors duration-300 antialiased`}
    >
      {/* Skip to Main Content Link for accessibility (WCAG AA+) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2.5 focus:bg-indigo-600 focus:text-white focus:rounded-xl focus:font-semibold focus:shadow-lg focus-visible:outline-none"
      >
        Skip to main content
      </a>

      <Navigation />

      <main id="main-content" className="relative focus:outline-none">
        {/* Background Subtle Dot Pattern */}
        <div className="absolute inset-0 dot-grid pointer-events-none -z-20 opacity-50 dark:opacity-20" />

        <Hero />
        <SocialProof />
        <FeatureGrid />
        <InteractiveDemo />
        <ArchitectureOverview />
        <SecurityGrid />
        <FAQ />
        <CTASection />
      </main>

      <Footer />
    </div>
  );
}
