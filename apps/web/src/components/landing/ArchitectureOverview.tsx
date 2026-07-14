"use client";

import React from "react";
import { TECH_ITEMS } from "./landing-config";
import * as Icons from "lucide-react";
import { motion } from "framer-motion";

export default function ArchitectureOverview() {
  return (
    <section
      id="tech"
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 border-t border-neutral-200/40 dark:border-neutral-800/40"
      aria-labelledby="tech-heading"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        {/* Left Side Header and Eyebrow */}
        <div className="lg:col-span-5 space-y-5">
          <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            Developer Experience
          </span>
          <h2
            id="tech-heading"
            className="text-3xl font-bold tracking-tight text-neutral-900 dark:text-white font-sans"
          >
            Built for infrastructure-level performance.
          </h2>
          <p className="text-sm sm:text-base text-neutral-500 dark:text-neutral-400 leading-relaxed font-medium">
            Our codebase is engineered with strict separation of concerns—maintaining completely
            isolated client caches and streaming API endpoints to handle document compilation
            safely.
          </p>

          <div className="flex items-center gap-6 pt-4">
            <div className="space-y-0.5">
              <span className="text-2xl font-extrabold text-neutral-900 dark:text-white">
                1.45s
              </span>
              <span className="text-[9px] text-neutral-400 dark:text-neutral-500 font-bold uppercase tracking-wider block">
                Average reasoning latency
              </span>
            </div>
            <div className="w-px h-8 bg-neutral-200 dark:bg-neutral-800" />
            <div className="space-y-0.5">
              <span className="text-2xl font-extrabold text-neutral-900 dark:text-white">
                99.9%
              </span>
              <span className="text-[9px] text-neutral-400 dark:text-neutral-500 font-bold uppercase tracking-wider block">
                Query accuracy attribution
              </span>
            </div>
          </div>
        </div>

        {/* Right Side Tech Cards Grid */}
        <div className="lg:col-span-7 space-y-4">
          {TECH_ITEMS.map((item, index) => {
            const LucideIcon = (Icons as any)[item.iconName] || Icons.Code;

            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, x: 25 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{
                  type: "spring",
                  stiffness: 100,
                  delay: index * 0.1,
                }}
                className="flex items-start gap-4 p-5 bg-white dark:bg-neutral-900/30 border border-neutral-200/60 dark:border-neutral-800/80 rounded-xl shadow-2xs hover:border-indigo-500/10 transition-colors"
              >
                {/* Icon Container */}
                <div className="h-10 w-10 shrink-0 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border border-indigo-100/50 dark:border-indigo-900/30 rounded-xl flex items-center justify-center">
                  <LucideIcon className="h-5 w-5" />
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-sm font-bold text-neutral-900 dark:text-white font-sans">
                      {item.title}
                    </h3>
                    <span className="text-[8px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-950/30 px-1.5 py-0.5 rounded border border-indigo-100/40 dark:border-indigo-900/30 font-mono">
                      {item.badge}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 leading-relaxed font-medium">
                    {item.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
