"use client";

import React from "react";
import * as Icons from "lucide-react";
import { motion } from "framer-motion";
import { FEATURE_ITEMS } from "./landing-config";

const GRADIENT_PAIRS = [
  { from: "#4f46e5", to: "#0d9488", glow: "rgba(79,70,229,0.06)" },
  { from: "#0d9488", to: "#0284c7", glow: "rgba(13,148,136,0.06)" },
  { from: "#0284c7", to: "#4f46e5", glow: "rgba(2,132,199,0.06)" },
  { from: "#7c3aed", to: "#0d9488", glow: "rgba(124,58,237,0.06)" },
  { from: "#059669", to: "#4f46e5", glow: "rgba(5,150,105,0.06)" },
  { from: "#4f46e5", to: "#3b82f6", glow: "rgba(79,70,229,0.06)" },
];

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 200, damping: 24 },
  },
};

export default function FeatureGrid() {
  const extendedFeatures = [
    ...FEATURE_ITEMS,
    {
      id: "trust",
      title: "Trust Score Engine",
      description:
        "Every document receives a granular trust score across 5 dimensions: completeness, consistency, temporal alignment, numerical integrity, and structural clarity.",
      iconName: "ShieldCheck",
      tag: "Trust",
      gradient: "from-emerald-500/10 to-teal-500/10",
    },
    {
      id: "copilot",
      title: "AI Review Copilot",
      description:
        "Automated compliance checklists generated per document. Every reviewer item is tracked with evidence, pass/fail status, and open risk questions.",
      iconName: "ClipboardCheck",
      tag: "Copilot",
      gradient: "from-indigo-500/10 to-teal-500/10",
    },
    {
      id: "requirements",
      title: "Requirements Tracker",
      description:
        "Auto-extracts REQ-IDs, links them to source pages, and flags orphaned or contradicting requirements across the repository.",
      iconName: "ListChecks",
      tag: "Compliance",
      gradient: "from-sky-500/10 to-indigo-500/10",
    },
  ];

  return (
    <section
      id="features"
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
      aria-labelledby="features-heading"
    >
      {/* Section header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ type: "spring", stiffness: 200, damping: 24 }}
        className="text-center max-w-3xl mx-auto mb-16"
      >
        <span className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 py-1.5 px-4 text-xs font-bold text-indigo-700 mb-5 shadow-xs">
          Core Capabilities
        </span>
        <h2
          id="features-heading"
          className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight"
        >
          Engineered for{" "}
          <span className="bg-gradient-to-r from-indigo-600 via-teal-600 to-sky-600 bg-clip-text text-transparent">
            strict accuracy
          </span>
          .
        </h2>
        <p className="mt-4 text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl mx-auto font-normal">
          DocuMind goes beyond raw text wrappers — introducing structural intelligence pipelines
          designed to inspect compliance bounds inside active document repositories.
        </p>
      </motion.div>

      {/* Bento grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {extendedFeatures.map((feat, index) => {
          const LucideIcon = (Icons as any)[feat.iconName] || Icons.HelpCircle;
          const grad = GRADIENT_PAIRS[index % GRADIENT_PAIRS.length];

          return (
            <motion.div
              key={feat.id}
              variants={cardVariants}
              whileHover={{ y: -6, transition: { duration: 0.2 } }}
              className="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 shadow-sm hover:shadow-xl hover:border-indigo-300 transition-all duration-300 cursor-default min-h-[270px]"
            >
              {/* Corner glow */}
              <div
                className="absolute -top-8 -right-8 w-36 h-36 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                style={{ background: grad.glow }}
              />

              <div className="space-y-4">
                {/* Icon */}
                <div
                  className="relative flex h-12 w-12 items-center justify-center rounded-xl overflow-hidden shadow-xs"
                  style={{
                    background: `linear-gradient(135deg, ${grad.from}15, ${grad.to}20)`,
                    border: `1px solid ${grad.from}30`,
                  }}
                >
                  <LucideIcon className="h-6 w-6" style={{ color: grad.from }} />
                </div>

                {/* Tag */}
                <span
                  className="inline-flex items-center text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full w-fit"
                  style={{
                    color: grad.from,
                    background: `${grad.from}12`,
                    border: `1px solid ${grad.from}25`,
                  }}
                >
                  {feat.tag}
                </span>

                {/* Content */}
                <div>
                  <h3 className="text-base font-bold text-slate-900 mb-2 leading-snug">
                    {feat.title}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                    {feat.description}
                  </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>
    </section>
  );
}
