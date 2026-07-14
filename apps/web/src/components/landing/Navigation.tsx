"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuthStore } from "@/store/useAuthStore";
import { NAVIGATION_ITEMS, DESIGN_TOKENS } from "./landing-config";
import logoImg from "../../../public/logo.png";
import { Menu, X, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Navigation() {
  const { user } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-neutral-200/50 bg-[#fcfbfa]/80 backdrop-blur-md dark:border-neutral-800/50 dark:bg-[#09090b]/80 transition-colors duration-300">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-8">
            <Link
              href="/"
              className="flex items-center gap-2.5 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
              aria-label="DocuMind AI Home"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg overflow-hidden border border-neutral-200/60 bg-white shadow-xs dark:border-neutral-800 dark:bg-neutral-900">
                <Image
                  src={logoImg}
                  alt=""
                  className="h-full w-full object-cover dark:mix-blend-lighten"
                  priority
                />
              </div>
              <span className="text-base font-bold tracking-tight text-neutral-900 dark:text-white">
                DocuMind{" "}
                <span className="text-indigo-600 dark:text-indigo-400 font-medium">AI</span>
              </span>
            </Link>

            {/* Desktop Navigation Link Array */}
            <nav className="hidden md:flex items-center gap-6" aria-label="Main Navigation">
              {NAVIGATION_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`text-xs font-semibold text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors duration-200 rounded-md py-1.5 px-2.5 ${DESIGN_TOKENS.shadows.focus}`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* Action CTAs */}
          <div className="hidden md:flex items-center gap-3">
            {mounted &&
              (user ? (
                <Link
                  href="/dashboard"
                  className={`inline-flex items-center gap-1.5 px-4.5 py-2 text-xs font-semibold rounded-xl shadow-xs ${DESIGN_TOKENS.colors.primary} ${DESIGN_TOKENS.shadows.focus}`}
                >
                  Open Console
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              ) : (
                <>
                  <Link
                    href="/auth/login"
                    className={`text-xs font-semibold text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors py-2 px-3 rounded-lg ${DESIGN_TOKENS.shadows.focus}`}
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/auth/signup"
                    className={`inline-flex items-center gap-1 px-4 py-2 text-xs font-semibold rounded-xl shadow-sm ${DESIGN_TOKENS.colors.primary} ${DESIGN_TOKENS.shadows.focus}`}
                  >
                    Get Started
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </>
              ))}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              type="button"
              className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-neutral-200 text-neutral-500 hover:text-neutral-900 dark:border-neutral-800 dark:text-neutral-400 dark:hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle mobile menu"
            >
              {mobileMenuOpen ? <X className="h-4.5 w-4.5" /> : <Menu className="h-4.5 w-4.5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Panel */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={DESIGN_TOKENS.animation.spring}
            className="md:hidden border-b border-neutral-200/50 bg-[#fcfbfa] px-4 py-4 dark:border-neutral-800/50 dark:bg-[#09090b] overflow-hidden"
          >
            <nav className="flex flex-col gap-2.5" aria-label="Mobile Navigation">
              {NAVIGATION_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-sm font-medium text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white py-2 px-3 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
                >
                  {item.label}
                </Link>
              ))}

              <div className="h-px bg-neutral-200/60 my-2 dark:bg-neutral-800/60" />

              <div className="flex flex-col gap-2 px-3">
                {mounted &&
                  (user ? (
                    <Link
                      href="/dashboard"
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold rounded-xl text-center shadow-xs ${DESIGN_TOKENS.colors.primary}`}
                    >
                      Open Console
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  ) : (
                    <>
                      <Link
                        href="/auth/login"
                        onClick={() => setMobileMenuOpen(false)}
                        className="text-xs font-semibold text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white text-center py-2 rounded-lg"
                      >
                        Sign In
                      </Link>
                      <Link
                        href="/auth/signup"
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center justify-center gap-1 px-4 py-2.5 text-xs font-semibold rounded-xl text-center shadow-sm ${DESIGN_TOKENS.colors.primary}`}
                      >
                        Get Started
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </>
                  ))}
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
