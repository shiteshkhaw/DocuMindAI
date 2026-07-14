"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/useAuthStore";
import { DESIGN_TOKENS } from "./landing-config";
import { ArrowRight, Play, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export default function Hero() {
  const { user } = useAuthStore();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: DESIGN_TOKENS.animation.spring,
    },
  };

  return (
    <section
      className="relative overflow-hidden pt-20 pb-16 sm:pt-28 sm:pb-20 md:pt-32 md:pb-24 lg:pt-40 lg:pb-32"
      aria-labelledby="hero-heading"
    >
      {/* Premium ambient glows */}
      <div className="absolute inset-0 -z-10 flex items-center justify-center">
        <div className="h-[450px] w-[450px] sm:h-[600px] w-[600px] rounded-full bg-gradient-to-tr from-indigo-500/10 to-purple-500/10 blur-[120px] dark:from-indigo-500/5 dark:to-purple-500/5 dark:blur-[180px]" />
      </div>

      <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center"
        >
          {/* Release Badge */}
          <motion.div variants={itemVariants} className="mb-6 flex items-center">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200/60 bg-indigo-50/50 py-1 px-3 text-[10px] font-bold text-indigo-700 dark:border-indigo-900/50 dark:bg-indigo-950/30 dark:text-indigo-400">
              <Sparkles className="h-3 w-3 text-indigo-500" />
              DocuMind AI v1.0
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            id="hero-heading"
            variants={itemVariants}
            className={`${DESIGN_TOKENS.typography.heroTitle} text-neutral-900 dark:text-white max-w-4xl font-sans`}
          >
            Document intelligence, <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-600 bg-clip-text text-transparent dark:from-indigo-400 dark:via-purple-400 dark:to-indigo-400">
              re-engineered for the enterprise.
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            variants={itemVariants}
            className="mt-6 max-w-2xl text-base sm:text-lg text-neutral-500 dark:text-neutral-400 font-medium leading-relaxed font-sans"
          >
            Compile files, scan logical contradictions, extract entity maps, and perform
            conversational queries over your knowledge base with cinematic precision.
          </motion.p>

          {/* Actions */}
          <motion.div
            variants={itemVariants}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto px-4"
          >
            {mounted &&
              (user ? (
                <Link
                  href="/dashboard"
                  className={`inline-flex w-full sm:w-auto items-center justify-center gap-2 px-7 py-3 text-sm font-semibold rounded-xl shadow-md ${DESIGN_TOKENS.colors.primary} ${DESIGN_TOKENS.shadows.focus}`}
                >
                  Go to Workspace Console
                  <ArrowRight className="h-4 w-4" />
                </Link>
              ) : (
                <>
                  <Link
                    href="/auth/signup"
                    className={`inline-flex w-full sm:w-auto items-center justify-center gap-2 px-7 py-3 text-sm font-semibold rounded-xl shadow-md ${DESIGN_TOKENS.colors.primary} ${DESIGN_TOKENS.shadows.focus}`}
                  >
                    Enter Workspace
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <a
                    href="#demo"
                    className={`inline-flex w-full sm:w-auto items-center justify-center gap-2 px-7 py-3 text-sm font-semibold rounded-xl transition-all duration-200 border border-neutral-200 bg-white hover:bg-neutral-50 hover:border-neutral-300 dark:border-neutral-800 dark:bg-neutral-900 dark:hover:bg-neutral-800 dark:text-neutral-200 ${DESIGN_TOKENS.shadows.focus}`}
                  >
                    <Play className="h-4 w-4 fill-current text-neutral-600 dark:text-neutral-400" />
                    Explore Tour
                  </a>
                </>
              ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
