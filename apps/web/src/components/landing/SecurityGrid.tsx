"use client";

import React from "react";
import { SECURITY_CARDS } from "./landing-config";
import * as Icons from "lucide-react";
import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";

const EXTENDED_SECURITY = [
  ...SECURITY_CARDS,
  {
    title: "SHA-256 Token Hashing",
    description:
      "Access tokens are never stored in plain text. Only SHA-256 digests hit the database, meaning a full DB leak cannot be used to forge authenticated sessions.",
    iconName: "KeyRound",
  },
  {
    title: "Rate Limiting & Throttling",
    description:
      "Upstash Redis-backed rate limiting protects auth endpoints and API routes from brute force, credential stuffing, and DDoS attacks at the edge.",
    iconName: "Gauge",
  },
  {
    title: "Security Headers",
    description:
      "Every response includes HSTS, CSP, X-Frame-Options, X-Content-Type-Options, and Permissions-Policy headers — meeting enterprise hardening baselines.",
    iconName: "ShieldAlert",
  },
];

const LIGHT_ACCENTS = [
  { icon: "#0d9488", bg: "#f0fdf4", border: "#bbf7d0" },
  { icon: "#4f46e5", bg: "#eef2ff", border: "#c7d2fe" },
  { icon: "#0284c7", bg: "#f0f9ff", border: "#bae6fd" },
  { icon: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe" },
  { icon: "#059669", bg: "#ecfdf5", border: "#a7f3d0" },
  { icon: "#0284c7", bg: "#f0f9ff", border: "#bae6fd" },
];

export default function SecurityGrid() {
  return (
    <section
      id="security"
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
      aria-labelledby="security-heading"
    >
      {/* Separator */}
      <div className="h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent mb-20" />

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ type: "spring", stiffness: 200, damping: 24 }}
        className="text-center max-w-3xl mx-auto mb-16"
      >
        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="relative flex h-12 w-12 items-center justify-center rounded-xl border border-teal-200 bg-teal-50 shadow-sm overflow-hidden">
            <ShieldCheck className="h-6 w-6 text-teal-600 relative z-10" />
          </div>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50 py-1.5 px-4 text-xs font-bold text-teal-700 shadow-xs">
          Governance & Isolation
        </span>
        <h2
          id="security-heading"
          className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight mt-4"
        >
          Enterprise-grade security,{" "}
          <span className="bg-gradient-to-r from-teal-600 to-indigo-600 bg-clip-text text-transparent">
            zero compromises
          </span>
          .
        </h2>
        <p className="mt-4 text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl mx-auto font-normal">
          DocuMind AI enforces complete isolation boundaries on every document vector shard and
          maintains verifiable logs of all administrative transactions.
        </p>
      </motion.div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {EXTENDED_SECURITY.map((card, index) => {
          const LucideIcon = (Icons as any)[card.iconName] || Icons.Shield;
          const style = LIGHT_ACCENTS[index % LIGHT_ACCENTS.length];

          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ type: "spring", stiffness: 200, damping: 22, delay: index * 0.07 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className="group relative flex flex-col justify-between gap-4 p-7 rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-xl hover:border-indigo-300 transition-all duration-300 cursor-default min-h-[230px]"
            >
              <div className="space-y-4">
                {/* Icon */}
                <div
                  className="relative flex h-12 w-12 items-center justify-center rounded-xl overflow-hidden shadow-xs"
                  style={{
                    background: style.bg,
                    border: `1px solid ${style.border}`,
                  }}
                >
                  <LucideIcon className="h-6 w-6 relative z-10" style={{ color: style.icon }} />
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900 mb-2 leading-snug">
                    {card.title}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                    {card.description}
                  </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
