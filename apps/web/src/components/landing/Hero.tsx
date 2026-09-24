"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/useAuthStore";

import { ArrowRight, Play, Sparkles, ChevronDown } from "lucide-react";
import { motion } from "framer-motion";

const WORDS = ["Documents", "Contracts", "Audit Files", "Research"];

function TypewriterWord() {
  const [index, setIndex] = React.useState(0);
  const [displayed, setDisplayed] = React.useState("");
  const [isDeleting, setIsDeleting] = React.useState(false);

  React.useEffect(() => {
    const word = WORDS[index];
    let timeout: NodeJS.Timeout;

    if (!isDeleting && displayed.length < word.length) {
      timeout = setTimeout(() => setDisplayed(word.slice(0, displayed.length + 1)), 80);
    } else if (!isDeleting && displayed.length === word.length) {
      timeout = setTimeout(() => setIsDeleting(true), 2000);
    } else if (isDeleting && displayed.length > 0) {
      timeout = setTimeout(() => setDisplayed(displayed.slice(0, -1)), 45);
    } else if (isDeleting && displayed.length === 0) {
      setIsDeleting(false);
      setIndex((i) => (i + 1) % WORDS.length);
    }
    return () => clearTimeout(timeout);
  }, [displayed, isDeleting, index]);

  return (
    <span className="relative inline-block">
      <span className="bg-gradient-to-r from-indigo-600 via-teal-600 to-sky-600 bg-clip-text text-transparent font-extrabold">
        {displayed}
      </span>
      <span className="ml-0.5 inline-block w-[3px] h-[0.85em] bg-indigo-600 align-middle animate-pulse" />
    </span>
  );
}

export default function Hero() {
  const { user, isLoading, initialize } = useAuthStore();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    initialize();
  }, [initialize]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.12, delayChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 24 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: "spring", stiffness: 260, damping: 26 },
    },
  };

  return (
    <section
      className="relative overflow-hidden min-h-[92vh] flex flex-col items-center justify-center pt-16 pb-20"
      aria-labelledby="hero-heading"
    >
      {/* ── Ambient orb layer (hardware-accelerated radial gradients) ── */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden transform-gpu">
        <div
          className="absolute -top-[20%] left-[15%] h-[60vw] w-[60vw] rounded-full opacity-60"
          style={{
            background:
              "radial-gradient(circle, rgba(99, 102, 241, 0.16) 0%, rgba(99, 102, 241, 0) 70%)",
            willChange: "transform",
          }}
        />
        <div
          className="absolute -bottom-[15%] right-[10%] h-[50vw] w-[50vw] rounded-full opacity-50"
          style={{
            background:
              "radial-gradient(circle, rgba(13, 148, 136, 0.14) 0%, rgba(13, 148, 136, 0) 70%)",
            willChange: "transform",
          }}
        />
      </div>

      <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8 w-full">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center"
        >
          {/* Release Badge */}
          <motion.div variants={itemVariants} className="mb-8">
            <span className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50/90 py-1.5 px-4.5 text-[11px] font-bold text-indigo-700 shadow-sm backdrop-blur-sm">
              <Sparkles className="h-3 w-3 text-indigo-600" />
              DocuMind AI v1.0 — Enterprise Intelligence
              <span className="h-1.5 w-1.5 rounded-full bg-teal-500 animate-pulse" />
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            id="hero-heading"
            variants={itemVariants}
            className="text-5xl sm:text-6xl md:text-7xl lg:text-[5.5rem] font-extrabold tracking-tight leading-[1.05] text-slate-900 max-w-5xl font-sans"
          >
            Intelligence for your <br className="hidden sm:inline" />
            <TypewriterWord />
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            variants={itemVariants}
            className="mt-7 max-w-2xl text-base sm:text-lg text-slate-600 font-medium leading-relaxed"
          >
            Compile files, scan logical contradictions, extract entity maps, and perform
            conversational queries over your knowledge base with{" "}
            <span className="text-slate-900 font-semibold">enterprise precision</span>.
          </motion.p>

          {/* Actions */}
          <motion.div
            variants={itemVariants}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto px-4"
          >
            {!mounted || isLoading ? (
              // Skeleton placeholder while validating token — prevents flash of wrong CTA
              <div className="h-12 w-48 rounded-xl bg-slate-200 animate-pulse" />
            ) : user ? (
              <Link
                href="/dashboard"
                id="hero-cta-workspace"
                className="group relative inline-flex w-full sm:w-auto items-center justify-center gap-2 overflow-hidden rounded-xl px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/25 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-600/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
              >
                <span className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 bg-gradient-to-r from-white/20 to-transparent" />
                Go to Workspace
                <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
              </Link>
            ) : (
              <>
                <Link
                  href="/auth/signup"
                  id="hero-cta-signup"
                  className="group relative inline-flex w-full sm:w-auto items-center justify-center gap-2.5 whitespace-nowrap overflow-hidden rounded-xl px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/25 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-600/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
                >
                  <span className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 bg-gradient-to-r from-white/20 to-transparent" />
                  Get Started Free
                  <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                </Link>
                <a
                  href="#demo"
                  id="hero-cta-demo"
                  className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white/90 px-7 py-3.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-100 hover:text-slate-900 transition-all duration-200 backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                >
                  <Play className="h-4 w-4 fill-current opacity-70 text-indigo-600" />
                  Explore Tour
                </a>
              </>
            )}
          </motion.div>

          {/* Trusted by line */}
          <motion.p variants={itemVariants} className="mt-8 text-xs text-slate-500 font-medium">
            Trusted by teams at{" "}
            <span className="text-slate-700 font-semibold">
              Apex Capital · Nova Legal · Helix Bio · Aegis Security
            </span>
          </motion.p>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-slate-400"
      >
        <span className="text-[10px] font-semibold uppercase tracking-widest">Scroll</span>
        <motion.div animate={{ y: [0, 5, 0] }} transition={{ duration: 1.5, repeat: Infinity }}>
          <ChevronDown className="h-4 w-4 text-slate-500" />
        </motion.div>
      </motion.div>
    </section>
  );
}
