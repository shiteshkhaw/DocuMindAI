"use client";

import React from "react";
import { SECURITY_CARDS } from "./landing-config";
import * as Icons from "lucide-react";
import { motion } from "framer-motion";

export default function SecurityGrid() {
  return (
    <section
      id="security"
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 border-t border-neutral-200/40 dark:border-neutral-800/40"
      aria-labelledby="security-heading"
    >
      <div className="text-center max-w-3xl mx-auto mb-16 sm:mb-20">
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
          Governance & Isolation
        </h2>
        <p
          id="security-heading"
          className="mt-3 text-3xl font-bold tracking-tight text-neutral-900 dark:text-white sm:text-4xl font-sans"
        >
          Zero-retention data privacy.
        </p>
        <p className="mt-4 text-base text-neutral-500 dark:text-neutral-400 font-medium">
          DocuMind AI enforces complete isolation boundaries on every document vector shard and
          maintains verifiable logs of administrative and member transactions.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {SECURITY_CARDS.map((card, index) => {
          const LucideIcon = (Icons as any)[card.iconName] || Icons.Shield;

          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                type: "spring",
                stiffness: 100,
                delay: index * 0.1,
              }}
              className="flex flex-col bg-white dark:bg-neutral-900/30 border border-neutral-200/60 dark:border-neutral-800/80 rounded-2xl p-6 sm:p-8 shadow-2xs hover:border-indigo-500/10 transition-colors duration-300"
            >
              {/* Icon */}
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 mb-6 border border-indigo-100/50 dark:border-indigo-900/30">
                <LucideIcon className="h-5 w-5" />
              </div>

              {/* Title & Body */}
              <h3 className="text-base font-bold text-neutral-900 dark:text-white mb-2.5 font-sans">
                {card.title}
              </h3>
              <p className="text-xs sm:text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed font-medium">
                {card.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
