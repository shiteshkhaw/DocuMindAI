"use client";

import React, { useState } from "react";
import { FAQ_ITEMS } from "./landing-config";
import { ChevronDown, MessageCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleIndex = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section
      id="faq"
      className="py-20 sm:py-28 mx-auto max-w-3xl px-4 sm:px-6 lg:px-8"
      aria-labelledby="faq-heading"
    >
      {/* Separator */}
      <div className="h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent mb-20" />

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ type: "spring", stiffness: 200, damping: 24 }}
        className="text-center mb-14"
      >
        <div className="flex justify-center mb-4">
          <div className="h-10 w-10 rounded-xl border border-indigo-200 bg-indigo-50 flex items-center justify-center shadow-xs">
            <MessageCircle className="h-5 w-5 text-indigo-600" />
          </div>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 py-1 px-3.5 text-[11px] font-bold text-indigo-700 shadow-sm mb-3">
          Got Questions?
        </span>
        <h2
          id="faq-heading"
          className="mt-2 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 leading-tight"
        >
          Frequently asked
        </h2>
      </motion.div>

      {/* Accordion */}
      <div className="space-y-3.5">
        {FAQ_ITEMS.map((item, index) => {
          const isOpen = openIndex === index;

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ type: "spring", stiffness: 200, damping: 24, delay: index * 0.06 }}
              className={`rounded-2xl border transition-all duration-300 overflow-hidden ${
                isOpen
                  ? "border-indigo-300 bg-indigo-50/50 shadow-md"
                  : "border-slate-200/90 bg-white/95 shadow-sm hover:border-indigo-200 hover:shadow-md"
              } backdrop-blur-md`}
            >
              {/* Trigger */}
              <button
                type="button"
                onClick={() => toggleIndex(index)}
                aria-expanded={isOpen}
                aria-controls={`faq-answer-${index}`}
                id={`faq-btn-${index}`}
                className="w-full flex items-center justify-between p-5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/30 group"
              >
                <span
                  className={`text-sm font-semibold transition-colors ${isOpen ? "text-indigo-950 font-bold" : "text-slate-800 group-hover:text-indigo-600"}`}
                >
                  {item.question}
                </span>
                <motion.div
                  animate={{ rotate: isOpen ? 180 : 0 }}
                  transition={{ duration: 0.25 }}
                  className="shrink-0 ml-4"
                >
                  <ChevronDown
                    className={`h-4 w-4 transition-colors ${isOpen ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-600"}`}
                  />
                </motion.div>
              </button>

              {/* Answer */}
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    id={`faq-answer-${index}`}
                    role="region"
                    aria-labelledby={`faq-btn-${index}`}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.22, ease: "easeInOut" }}
                  >
                    <div className="px-5 pb-5 text-sm text-slate-600 leading-relaxed border-t border-indigo-100 pt-4 font-normal">
                      {item.answer}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
