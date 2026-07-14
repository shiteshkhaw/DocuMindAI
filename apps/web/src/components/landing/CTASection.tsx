"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/useAuthStore";
import { DESIGN_TOKENS } from "./landing-config";
import { ArrowRight, Sparkles } from "lucide-react";

export default function CTASection() {
  const { user } = useAuthStore();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section
      className="py-20 sm:py-28 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 border-t border-neutral-200/40 dark:border-neutral-800/40"
      aria-label="CTA"
    >
      <div className="relative overflow-hidden bg-indigo-50/50 dark:bg-indigo-950/20 px-6 py-20 text-center shadow-lg rounded-3xl sm:px-16 sm:py-28 border border-indigo-100/80 dark:border-indigo-900/30">
        {/* Decorative background lights */}
        <div className="absolute inset-0 -z-10 flex items-center justify-center">
          <div className="h-[250px] w-[250px] sm:h-[400px] w-[400px] rounded-full bg-indigo-500/10 blur-[80px]" />
        </div>

        <div className="mx-auto max-w-2xl space-y-6">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-550/10 dark:bg-indigo-500/10 py-1 px-3.5 text-[9px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">
            <Sparkles className="h-3 w-3" /> Get Instant Access
          </span>
          <h2 className="text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-white sm:text-4xl font-sans">
            Ready to audit your documents?
          </h2>
          <p className="mx-auto max-w-xl text-xs sm:text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed font-medium">
            Join enterprise operations teams indexing data repositories and scanning clauses in
            seconds. No credit card required.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            {mounted &&
              (user ? (
                <Link
                  href="/dashboard"
                  className={`inline-flex w-full sm:w-auto items-center justify-center gap-2 px-6 py-3 text-xs font-semibold rounded-xl shadow-md ${DESIGN_TOKENS.colors.primary} ${DESIGN_TOKENS.shadows.focus}`}
                >
                  Go to Workspace Console
                  <ArrowRight className="h-4 w-4" />
                </Link>
              ) : (
                <>
                  <Link
                    href="/auth/signup"
                    className={`inline-flex w-full sm:w-auto items-center justify-center gap-2 px-6 py-3 text-xs font-semibold rounded-xl shadow-md ${DESIGN_TOKENS.colors.primary} ${DESIGN_TOKENS.shadows.focus}`}
                  >
                    Create Free Account
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <a
                    href="#demo"
                    className="inline-flex w-full sm:w-auto items-center justify-center gap-2 px-6 py-3 text-xs font-semibold rounded-xl border border-neutral-200 bg-white text-neutral-800 hover:bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-200 dark:hover:bg-neutral-800 transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-indigo-500/20 focus-visible:outline-none"
                  >
                    Explore Demo
                  </a>
                </>
              ))}
          </div>
        </div>
      </div>
    </section>
  );
}
