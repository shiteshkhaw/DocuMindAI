"use client";

import React from "react";
import { TECH_ITEMS } from "./landing-config";
import * as Icons from "lucide-react";
import { motion } from "framer-motion";

const METRICS = [
  { value: "1.45s", label: "Avg. reasoning latency" },
  { value: "99.9%", label: "Query accuracy" },
  { value: "<50ms", label: "Vector retrieval" },
];

export default function ArchitectureOverview() {
  return (
    <section
      id="tech"
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
      aria-labelledby="tech-heading"
    >
      {/* Separator */}
      <div className="h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent mb-20" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        {/* Left: Header */}
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ type: "spring", stiffness: 180, damping: 22 }}
          className="lg:col-span-5 space-y-6 lg:sticky lg:top-28"
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 py-1.5 px-4 text-xs font-bold text-indigo-700 shadow-xs">
            Developer Experience
          </span>
          <h2
            id="tech-heading"
            className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight"
          >
            Built for{" "}
            <span className="bg-gradient-to-r from-indigo-600 to-teal-600 bg-clip-text text-transparent">
              infrastructure-level
            </span>{" "}
            performance.
          </h2>
          <p className="text-base text-slate-600 leading-relaxed font-normal">
            Our codebase is engineered with strict separation of concerns — maintaining completely
            isolated client caches and streaming API endpoints to handle document compilation
            safely.
          </p>

          {/* Metrics */}
          <div className="flex flex-wrap gap-4 pt-2">
            {METRICS.map((m) => (
              <div
                key={m.label}
                className="flex flex-col gap-1 p-5 rounded-2xl border border-slate-200 bg-white shadow-sm min-w-[120px]"
              >
                <span className="text-2xl font-extrabold text-slate-900 tabular-nums">
                  {m.value}
                </span>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                  {m.label}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right: Tech Cards */}
        <div className="lg:col-span-7 space-y-5">
          {TECH_ITEMS.map((item, index) => {
            const LucideIcon = (Icons as any)[item.iconName] || Icons.Code;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, x: 24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ type: "spring", stiffness: 180, damping: 22, delay: index * 0.08 }}
                className="group flex items-start gap-5 p-6 rounded-2xl border border-slate-200 bg-white shadow-sm hover:border-indigo-300 hover:shadow-md transition-all duration-300"
              >
                {/* Icon */}
                <div className="h-12 w-12 shrink-0 flex items-center justify-center rounded-xl border border-indigo-200 bg-indigo-50 text-indigo-600 group-hover:border-indigo-300 transition-colors duration-300 shadow-xs">
                  <LucideIcon className="h-6 w-6" />
                </div>

                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                    <span className="text-[9px] font-bold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-200 font-mono">
                      {item.badge}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
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
