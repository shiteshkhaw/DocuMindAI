"use client";

import React from "react";
import Link from "next/link";
import { HelpCircle, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#fcfbfa] dark:bg-[#09090b] px-6 text-center transition-colors duration-300">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950/30 dark:text-indigo-400 border border-indigo-100/50 dark:border-indigo-900/30 mb-5">
        <HelpCircle className="h-6 w-6" />
      </div>

      <h2 className="text-lg font-bold text-neutral-900 dark:text-white font-sans">
        Vault not found
      </h2>
      <p className="mt-2 max-w-sm text-xs text-neutral-400 dark:text-neutral-500 font-medium leading-relaxed font-sans">
        The requested routing node or workspace vault does not exist or has been relocated from the
        indexing catalog.
      </p>

      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-1.5 px-4.5 py-2.5 text-xs font-semibold text-neutral-800 bg-white border border-neutral-200 hover:bg-neutral-50 dark:bg-neutral-900 dark:text-neutral-200 dark:border-neutral-800 dark:hover:bg-neutral-850 rounded-xl shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Return home
      </Link>
    </div>
  );
}
