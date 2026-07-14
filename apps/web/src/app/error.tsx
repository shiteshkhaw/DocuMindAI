"use client";

import React, { useEffect } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log exception to logging pipelines (e.g. Sentry/Console)
    console.error("App boundary caught runtime error:", error);
  }, [error]);

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#fcfbfa] dark:bg-[#09090b] px-6 text-center transition-colors duration-300">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600 dark:bg-red-950/30 dark:text-red-400 border border-red-100/50 dark:border-red-900/30 mb-5">
        <AlertCircle className="h-6 w-6" />
      </div>

      <h2 className="text-lg font-bold text-neutral-900 dark:text-white font-sans">
        Unexpected error encountered
      </h2>
      <p className="mt-2 max-w-sm text-xs text-neutral-400 dark:text-neutral-500 font-medium leading-relaxed font-sans">
        The workspace system encountered a runtime exception. Diagnostic code:{" "}
        <code className="font-mono bg-neutral-100 dark:bg-neutral-800 px-1 py-0.5 rounded text-[10px]">
          {error.digest || "SYS-ERR"}
        </code>
      </p>

      <button
        onClick={() => reset()}
        className="mt-6 inline-flex items-center gap-1.5 px-4.5 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 rounded-xl shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
      >
        <RotateCcw className="h-3.5 w-3.5" />
        Reset workspace
      </button>
    </div>
  );
}
