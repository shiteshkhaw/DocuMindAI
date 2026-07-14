"use client";

import React from "react";
import { FEATURE_ITEMS } from "./landing-config";
import * as Icons from "lucide-react";
import { motion } from "framer-motion";

export default function FeatureGrid() {
  return (
    <section
      id="features"
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
      aria-labelledby="features-heading"
    >
      <div className="text-center max-w-3xl mx-auto mb-16 sm:mb-20">
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
          Core Capabilities
        </h2>
        <p
          id="features-heading"
          className="mt-3 text-3xl font-bold tracking-tight text-neutral-900 dark:text-white sm:text-4xl font-sans"
        >
          Engineered for strict accuracy.
        </p>
        <p className="mt-4 text-base text-neutral-500 dark:text-neutral-400 font-medium">
          DocuMind AI moves past raw text wrappers, introducing structural intelligence pipelines
          designed to inspect and map compliance bounds in active file directories.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {FEATURE_ITEMS.map((feat, index) => {
          // Dynamic icon loader from Lucide icons package
          const LucideIcon = (Icons as any)[feat.iconName] || Icons.HelpCircle;

          return (
            <motion.div
              key={feat.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{
                type: "spring",
                stiffness: 120,
                delay: index * 0.1,
              }}
              whileHover={{
                y: -6,
                transition: { duration: 0.2, ease: "easeOut" },
              }}
              className="flex flex-col h-full bg-white dark:bg-neutral-900/40 border border-neutral-200/60 dark:border-neutral-800/80 rounded-2xl p-6 sm:p-8 shadow-xs relative overflow-hidden group transition-all duration-300 hover:border-indigo-500/20 hover:shadow-md hover:shadow-indigo-500/[0.01]"
            >
              {/* Decorative gradient corner glow */}
              <div
                className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl ${feat.gradient} rounded-bl-full opacity-60 group-hover:scale-110 transition-transform duration-500`}
              />

              {/* Icon Container */}
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 mb-6 border border-indigo-100/50 dark:border-indigo-900/30">
                <LucideIcon className="h-5 w-5" />
              </div>

              {/* Tag eyebrow */}
              <div className="mb-2">
                <span className="inline-flex items-center text-[9px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-950/20 px-2 py-0.5 rounded-full border border-indigo-100/30 dark:border-indigo-900/20">
                  {feat.tag}
                </span>
              </div>

              {/* Title & Description */}
              <h3 className="text-base font-bold text-neutral-900 dark:text-white mb-2.5 font-sans">
                {feat.title}
              </h3>
              <p className="text-xs sm:text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed font-medium">
                {feat.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
