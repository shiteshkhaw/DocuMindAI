"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import logoImg from "../../../public/logo.png";
import { Shield } from "lucide-react";

const FOOTER_LINKS = {
  Product: [
    { label: "Features", href: "#features" },
    { label: "Interactive Demo", href: "#demo" },
    { label: "Architecture", href: "#tech" },
  ],
  Security: [
    { label: "Data Privacy", href: "#security" },
    { label: "Audit Trails", href: "#security" },
    { label: "Workspace Isolation", href: "#security" },
  ],
  Platform: [
    { label: "Sign In", href: "/auth/login" },
    { label: "Get Started", href: "/auth/signup" },
    { label: "FAQ", href: "#faq" },
  ],
};

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white" aria-label="DocuMind Footer">
      {/* Separator glow */}
      <div className="h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Main footer grid */}
        <div className="py-14 grid grid-cols-1 md:grid-cols-12 gap-10">
          {/* Brand */}
          <div className="md:col-span-4 space-y-5">
            <Link href="/" className="flex items-center gap-2.5 group w-fit">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl overflow-hidden border border-slate-200 bg-white shadow-xs transition-all duration-300 group-hover:border-indigo-300">
                <Image
                  src={logoImg}
                  alt=""
                  className="h-full w-full object-cover mix-blend-multiply"
                />
              </div>
              <span className="text-sm font-bold tracking-tight text-slate-900">
                DocuMind{" "}
                <span className="bg-gradient-to-r from-indigo-600 to-teal-600 bg-clip-text text-transparent">
                  AI
                </span>
              </span>
            </Link>

            <p className="text-xs text-slate-600 leading-relaxed max-w-xs font-normal">
              Verifiable document intelligence, sharded vector caching, and logical compliance
              scanners for modern enterprise operations.
            </p>

            {/* Security badge */}
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-semibold">
              <Shield className="h-3.5 w-3.5 text-teal-600" />
              Enterprise-grade security
            </div>
          </div>

          {/* Links */}
          <div className="md:col-span-8 grid grid-cols-3 gap-6">
            {Object.entries(FOOTER_LINKS).map(([category, links]) => (
              <div key={category}>
                <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">
                  {category}
                </h3>
                <ul className="space-y-2.5">
                  {links.map((link) => (
                    <li key={link.label}>
                      {link.href.startsWith("#") ? (
                        <a
                          href={link.href}
                          className="text-xs text-slate-600 hover:text-indigo-600 transition-colors duration-200 font-medium"
                        >
                          {link.label}
                        </a>
                      ) : (
                        <Link
                          href={link.href}
                          className="text-xs text-slate-600 hover:text-indigo-600 transition-colors duration-200 font-medium"
                        >
                          {link.label}
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom row */}
        <div className="border-t border-slate-200 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-[10px] text-slate-500 font-mono">
            &copy; {new Date().getFullYear()} DocuMind AI. All rights reserved.
          </p>
          <p className="text-[10px] text-slate-500 font-mono">
            Built with FastAPI · Next.js · ChromaDB · OpenAI · Supabase
          </p>
        </div>
      </div>
    </footer>
  );
}
