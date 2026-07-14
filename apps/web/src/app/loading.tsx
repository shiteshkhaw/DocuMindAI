"use client";

import React from "react";
import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#fcfbfa] dark:bg-[#09090b] transition-colors duration-300">
      <div className="relative">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600 dark:text-indigo-400 relative z-10" />
        <div className="absolute inset-0 bg-indigo-500/20 blur-xl rounded-full animate-pulse" />
      </div>
      <p className="mt-4 text-xs font-semibold text-neutral-400 dark:text-neutral-500 uppercase tracking-widest animate-pulse font-sans">
        Loading Workspace...
      </p>
    </div>
  );
}
