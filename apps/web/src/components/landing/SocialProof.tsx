"use client";

import React from "react";
import { motion } from "framer-motion";

const COMPANIES = [
  { name: "Apex Capital", role: "Investment Research" },
  { name: "Vanguard Tech", role: "SaaS DevOps" },
  { name: "Nova Legal", role: "Compliance & Auditing" },
  { name: "Helix Bio", role: "Clinical Trials" },
  { name: "Aegis Security", role: "Sovereign Audit" },
  { name: "Meridian Law", role: "Contract Intelligence" },
  { name: "Atlas Finance", role: "Regulatory Review" },
];

const STATS = [
  { value: 14205, suffix: "+", label: "Documents Analyzed" },
  { value: 3892, suffix: "+", label: "Contradictions Caught" },
  { value: 99.2, suffix: "%", label: "Retrieval Accuracy", decimals: 1 },
];

function AnimatedCounter({
  value,
  suffix,
  decimals = 0,
}: {
  value: number;
  suffix: string;
  decimals?: number;
}) {
  const [count, setCount] = React.useState(0);
  const ref = React.useRef<HTMLDivElement>(null);
  const started = React.useRef(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          let frame = 0;
          const total = 80;
          const interval = setInterval(() => {
            frame++;
            const progress = frame / total;
            const eased = 1 - Math.pow(1 - progress, 3);
            setCount(parseFloat((eased * value).toFixed(decimals)));
            if (frame >= total) {
              setCount(value);
              clearInterval(interval);
            }
          }, 20);
        }
      },
      { threshold: 0.5 },
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [value, decimals]);

  return (
    <div ref={ref} className="text-3xl sm:text-4xl font-extrabold text-slate-900 tabular-nums">
      {decimals > 0 ? count.toFixed(decimals) : Math.floor(count).toLocaleString()}
      {suffix}
    </div>
  );
}

export default function SocialProof() {
  const doubled = [...COMPANIES, ...COMPANIES];

  return (
    <section className="py-16 sm:py-20 relative" aria-label="Social proof and statistics">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Divider line */}
        <div className="h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent mb-16" />

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-6 sm:gap-10 mb-16 max-w-2xl mx-auto">
          {STATS.map((stat) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ type: "spring", stiffness: 200, damping: 24 }}
              className="flex flex-col items-center text-center gap-1"
            >
              <AnimatedCounter value={stat.value} suffix={stat.suffix} decimals={stat.decimals} />
              <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                {stat.label}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Trusted by */}
        <p className="text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-6">
          Trusted by leading enterprises
        </p>
      </div>

      {/* Marquee ticker */}
      <div className="relative overflow-hidden">
        {/* Fade edges */}
        <div className="absolute left-0 top-0 bottom-0 w-24 z-10 bg-gradient-to-r from-[#faf9f6] to-transparent pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-24 z-10 bg-gradient-to-l from-[#faf9f6] to-transparent pointer-events-none" />

        <div className="flex marquee-track gap-6">
          {doubled.map((company, i) => (
            <div
              key={i}
              className="flex-shrink-0 flex flex-col items-center justify-center gap-1 px-6 py-3.5 rounded-xl border border-slate-200/80 bg-white/90 shadow-sm backdrop-blur-sm min-w-[160px]"
            >
              <span className="text-sm font-bold text-slate-800 whitespace-nowrap">
                {company.name}
              </span>
              <span className="text-[10px] text-slate-500 font-medium whitespace-nowrap">
                {company.role}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
