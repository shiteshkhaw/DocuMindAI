"use client";

import React, { useState } from "react";
import { FAQ_ITEMS } from "./landing-config";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleIndex = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section
      id="faq"
      className="py-20 sm:py-28 mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 border-t border-neutral-200/40 dark:border-neutral-800/40"
      aria-labelledby="faq-heading"
    >
      <div className="text-center mb-16">
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
          Got Questions?
        </h2>
        <p
          id="faq-heading"
          className="mt-3 text-3xl font-bold tracking-tight text-neutral-900 dark:text-white font-sans"
        >
          Frequently Answered Queries
        </p>
      </div>

      <div className="space-y-4">
        {FAQ_ITEMS.map((item, index) => {
          const isOpen = openIndex === index;

          return (
            <div
              key={index}
              className="border border-neutral-200/60 bg-white dark:border-neutral-800/80 dark:bg-neutral-900/20 rounded-xl overflow-hidden transition-colors"
            >
              {/* Accordion Trigger Header */}
              <button
                type="button"
                onClick={() => toggleIndex(index)}
                aria-expanded={isOpen}
                aria-controls={`faq-answer-${index}`}
                id={`faq-btn-${index}`}
                className="w-full flex items-center justify-between p-5 text-left text-neutral-850 hover:text-neutral-950 dark:text-neutral-200 dark:hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20 font-semibold text-xs sm:text-sm font-sans"
              >
                <span>{item.question}</span>
                <ChevronDown
                  className={`h-4.5 w-4.5 text-neutral-400 dark:text-neutral-500 shrink-0 transition-transform duration-300 ${
                    isOpen ? "rotate-180 text-indigo-500 dark:text-indigo-400" : ""
                  }`}
                />
              </button>

              {/* Accordion Answer Content */}
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    id={`faq-answer-${index}`}
                    role="region"
                    aria-labelledby={`faq-btn-${index}`}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: "easeInOut" }}
                  >
                    <div className="px-5 pb-5 pt-0 text-xs sm:text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed font-medium">
                      {item.answer}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}
