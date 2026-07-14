"use client";

import React from "react";
import { SOCIAL_PROOF_LOGOS } from "./landing-config";
import { motion } from "framer-motion";

export default function SocialProof() {
  return (
    <section
      className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 border-t border-b border-neutral-200/40 dark:border-neutral-800/40"
      aria-label="Social Proof"
    >
      <div className="text-center">
        <p className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
          Trusted by operators at compliance, finance, and engineering companies
        </p>

        <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-6 items-center justify-center opacity-70">
          {SOCIAL_PROOF_LOGOS.map((company, index) => (
            <motion.div
              key={company.name}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                type: "spring",
                stiffness: 100,
                delay: index * 0.08,
              }}
              className="flex flex-col items-center justify-center p-2 text-center"
            >
              <span className="text-sm font-bold text-neutral-800 dark:text-neutral-200 tracking-tight font-sans">
                {company.name}
              </span>
              <span className="text-[9px] text-neutral-400 dark:text-neutral-500 font-mono mt-0.5 uppercase tracking-wide">
                {company.role}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
