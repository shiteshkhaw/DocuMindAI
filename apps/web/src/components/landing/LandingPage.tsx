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

      {/* ── High-performance ambient mesh with GPU compositing ── */}
      <div className="fixed inset-0 -z-20 pointer-events-none overflow-hidden transform-gpu">
        <div
          className="absolute -top-20 left-1/4 w-[70vw] h-[70vw] rounded-full opacity-70"
          style={{
            background:
              "radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, rgba(99, 102, 241, 0) 70%)",
            willChange: "transform",
          }}
        />
        <div
          className="absolute top-1/3 right-0 w-[55vw] h-[55vw] rounded-full opacity-60"
          style={{
            background:
              "radial-gradient(circle, rgba(13, 148, 136, 0.10) 0%, rgba(13, 148, 136, 0) 70%)",
            willChange: "transform",
          }}
        />
        <div
          className="absolute bottom-10 left-10 w-[50vw] h-[50vw] rounded-full opacity-50"
          style={{
            background:
              "radial-gradient(circle, rgba(2, 132, 199, 0.08) 0%, rgba(2, 132, 199, 0) 70%)",
            willChange: "transform",
          }}
        />
      </div>

      {/* ── High-performance subtle dot grid overlay ── */}
      <div className="fixed inset-0 -z-10 pointer-events-none dot-grid opacity-[0.10]" />

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
