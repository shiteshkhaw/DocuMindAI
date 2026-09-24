"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuthStore } from "@/store/useAuthStore";
import { NAVIGATION_ITEMS } from "./landing-config";
import logoImg from "../../../public/logo.png";
import { Menu, X, ArrowRight, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Navigation() {
  const { user, isLoading, initialize } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    initialize();
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [initialize]);

  return (
    <header
      className={`sticky top-0 z-40 w-full transition-all duration-500 ${
        scrolled
          ? "border-b border-slate-200/80 bg-white/80 shadow-md shadow-slate-900/5 backdrop-blur-xl"
          : "border-b border-transparent bg-transparent"
      }`}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-8">
            <Link
              href="/"
              id="nav-logo"
              className="group flex items-center gap-2.5 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
              aria-label="DocuMind AI Home"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl overflow-hidden border border-slate-200 bg-white shadow-xs transition-all duration-300 group-hover:border-indigo-500/40 group-hover:shadow-indigo-500/10">
                <Image
                  src={logoImg}
                  alt=""
                  className="h-full w-full object-cover mix-blend-multiply"
                  priority
                />
              </div>
              <span className="text-base font-bold tracking-tight text-slate-900">
                DocuMind{" "}
                <span className="bg-gradient-to-r from-indigo-600 via-teal-600 to-sky-600 bg-clip-text text-transparent">
                  AI
                </span>
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
              {NAVIGATION_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="group relative px-3 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors duration-200 rounded-lg hover:bg-slate-100/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                >
                  {item.label}
                  <span className="absolute bottom-1 left-3 right-3 h-0.5 bg-gradient-to-r from-indigo-600 to-teal-600 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-full" />
                </Link>
              ))}
            </nav>
          </div>

          {/* Action CTAs */}
          <div className="hidden md:flex items-center gap-3">
            {!mounted || isLoading ? (
              <div className="h-9 w-32 rounded-xl bg-slate-200/70 animate-pulse" />
            ) : user ? (
              <Link
                href="/dashboard"
                id="nav-cta-console"
                className="group relative inline-flex items-center gap-2 overflow-hidden rounded-xl px-6 py-2.5 text-xs font-bold text-white tracking-wide whitespace-nowrap shadow-md shadow-indigo-600/25 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-600/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
              >
                <span className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 bg-gradient-to-r from-white/20 to-transparent" />
                <Sparkles className="h-3.5 w-3.5" />
                Open Console
                <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
              </Link>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  id="nav-cta-signin"
                  className="text-xs font-semibold text-slate-700 hover:text-indigo-600 transition-colors py-2 px-3.5 rounded-lg hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                >
                  Sign In
                </Link>
                <Link
                  href="/auth/signup"
                  id="nav-cta-signup"
                  className="group relative inline-flex items-center gap-2 overflow-hidden rounded-xl px-6 py-2.5 text-xs font-bold text-white tracking-wide whitespace-nowrap shadow-md shadow-indigo-600/20 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-600/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
                >
                  <span className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 bg-gradient-to-r from-white/20 to-transparent" />
                  Get Started
                  <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              type="button"
              id="nav-mobile-toggle"
              className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 transition-all"
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
            transition={{ type: "spring", stiffness: 300, damping: 28 }}
            className="md:hidden border-b border-slate-200 bg-white/95 px-4 py-4 backdrop-blur-xl overflow-hidden shadow-lg"
          >
            <nav className="flex flex-col gap-1" aria-label="Mobile Navigation">
              {NAVIGATION_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-sm font-medium text-slate-700 hover:text-indigo-600 py-2 px-3 rounded-lg hover:bg-slate-100 transition-all"
                >
                  {item.label}
                </Link>
              ))}

              <div className="h-px bg-slate-200 my-2" />

              <div className="flex flex-col gap-2 px-3">
                {!mounted || isLoading ? (
                  <div className="h-10 rounded-xl bg-slate-200 animate-pulse" />
                ) : user ? (
                  <Link
                    href="/dashboard"
                    onClick={() => setMobileMenuOpen(false)}
                    id="nav-mobile-cta-console"
                    className="group relative flex items-center justify-center gap-2 overflow-hidden rounded-xl px-6 py-3 text-xs font-bold text-white shadow-md"
                    style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
                  >
                    Open Console
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                ) : (
                  <>
                    <Link
                      href="/auth/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="text-xs font-semibold text-slate-700 hover:text-slate-900 text-center py-2 rounded-lg hover:bg-slate-100"
                    >
                      Sign In
                    </Link>
                    <Link
                      href="/auth/signup"
                      onClick={() => setMobileMenuOpen(false)}
                      id="nav-mobile-cta-signup"
                      className="flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-xs font-bold text-white text-center shadow-md"
                      style={{ background: "linear-gradient(135deg, #4f46e5, #0d9488)" }}
                    >
                      Get Started
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </>
                )}
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
