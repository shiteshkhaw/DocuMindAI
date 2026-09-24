"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/useAuthStore";
import { ArrowRight, Sparkles, Zap } from "lucide-react";
import { motion } from "framer-motion";

export default function CTASection() {
  const { user, isLoading } = useAuthStore();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
      aria-label="Call to action"
    >
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ type: "spring", stiffness: 180, damping: 22 }}
        className="relative overflow-hidden rounded-3xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/90 via-white to-teal-50/80 backdrop-blur-md px-6 py-20 text-center sm:px-16 sm:py-28 shadow-xl shadow-indigo-500/5"
      >
        {/* Animated gradient mesh background */}
        <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden rounded-3xl">
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.4, 0.6, 0.4] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] rounded-full bg-indigo-400/20 blur-[100px]"
          />
          <motion.div
            animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3], x: [0, 40, 0] }}
            transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-1/4 -left-1/4 w-1/2 h-full rounded-full bg-teal-400/20 blur-[120px]"
          />
        </div>

        {/* Content */}
        <div className="relative mx-auto max-w-2xl space-y-6">
          <div className="flex justify-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-white py-1.5 px-4 text-[11px] font-bold text-indigo-700 shadow-xs">
              <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
              Get Instant Access
              <span className="h-1.5 w-1.5 rounded-full bg-teal-500 animate-pulse" />
            </span>
          </div>

          <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Ready to audit your{" "}
            <span className="bg-gradient-to-r from-indigo-600 to-teal-600 bg-clip-text text-transparent">
              documents
            </span>
            ?
          </h2>

          <p className="mx-auto max-w-xl text-base text-slate-600 leading-relaxed font-normal">
            Join enterprise operations teams indexing repositories and scanning clauses in seconds.
            No credit card required. Deployed in under 2 minutes.
          </p>

          {/* Features inline */}
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-medium text-slate-600">
            {["Free to start", "Zero retention storage", "Sub-second retrieval"].map((f) => (
              <span key={f} className="flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 text-indigo-600" />
                {f}
              </span>
            ))}
          </div>

          {/* CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            {!mounted || isLoading ? (
              <div className="h-12 w-44 rounded-xl bg-slate-200 animate-pulse" />
            ) : user ? (
              <Link
                href="/dashboard"
                id="cta-workspace"
                className="group relative inline-flex w-full sm:w-auto items-center justify-center gap-2 overflow-hidden rounded-xl px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/25 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-600/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
              >
                <span className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 bg-gradient-to-r from-white/20 to-transparent" />
                Go to Workspace Console
                <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
              </Link>
            ) : (
              <>
                <Link
                  href="/auth/signup"
                  id="cta-signup"
                  className="group relative inline-flex w-full sm:w-auto items-center justify-center gap-2 overflow-hidden rounded-xl px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/25 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-600/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
                >
                  <span className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 bg-gradient-to-r from-white/20 to-transparent" />
                  Create Free Account
                  <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                </Link>
                <a
                  href="#demo"
                  id="cta-demo"
                  className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-7 py-3.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-100 hover:text-slate-900 transition-all duration-200 backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                >
                  Explore Demo
                </a>
              </>
            )}
          </div>
        </div>
      </motion.div>
    </section>
  );
}
