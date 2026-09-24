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

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#faf9f6] text-slate-900 antialiased relative overflow-x-hidden">
      {/* ── Skip to main content (WCAG AA) ── */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2.5 focus:bg-indigo-600 focus:text-white focus:rounded-xl focus:font-semibold focus:shadow-lg focus-visible:outline-none"
      >
        Skip to main content
      </a>

      {/* ── Global ambient mesh — covers entire page ── */}
      <div className="fixed inset-0 -z-20 pointer-events-none overflow-hidden">
        <div className="absolute -top-20 left-1/4 w-[70vw] h-[70vw] rounded-full bg-indigo-500/10 blur-[140px] aurora-orb" />
        <div
          className="absolute top-1/3 right-0 w-[55vw] h-[55vw] rounded-full bg-teal-500/10 blur-[130px]"
          style={{ animation: "aurora-pulse 12s ease-in-out 2s infinite" }}
        />
        <div
          className="absolute bottom-10 left-10 w-[50vw] h-[50vw] rounded-full bg-sky-500/8 blur-[120px]"
          style={{ animation: "aurora-pulse 15s ease-in-out 4s infinite" }}
        />
      </div>

      {/* ── Global grid dot overlay ── */}
      <div className="fixed inset-0 -z-10 pointer-events-none dot-grid opacity-[0.15]" />

      {/* ── Noise grain ── */}
      <div className="fixed inset-0 -z-10 noise-overlay" />

      <Navigation />

      <main id="main-content" className="relative focus:outline-none">
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
