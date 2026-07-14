"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import logoImg from "../../../public/logo.png";

export default function Footer() {
  return (
    <footer
      className="bg-[#fcfbfa] dark:bg-[#09090b] border-t border-neutral-200/50 dark:border-neutral-800/60 transition-colors duration-300"
      aria-label="DocuMind Footer"
    >
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 md:flex md:items-center md:justify-between lg:px-8 lg:py-16">
        {/* Brand Information */}
        <div className="space-y-4 md:order-1 md:mt-0 max-w-xs">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg overflow-hidden border border-neutral-200/60 bg-white shadow-xs dark:border-neutral-800 dark:bg-neutral-900">
              <Image
                src={logoImg}
                alt=""
                className="h-full w-full object-cover dark:mix-blend-lighten"
              />
            </div>
            <span className="text-sm font-bold tracking-tight text-neutral-900 dark:text-white">
              DocuMind <span className="text-indigo-600 dark:text-indigo-400 font-medium">AI</span>
            </span>
          </div>
          <p className="text-xs text-neutral-400 dark:text-neutral-500 font-medium leading-relaxed font-sans">
            Verifiable document intelligence, sharded vector caching, and logical compliance
            scanners for modern enterprise operations.
          </p>
        </div>

        {/* Links Grid Column layout */}
        <div className="mt-8 grid grid-cols-2 gap-8 sm:grid-cols-3 md:order-2 md:mt-0">
          <div>
            <h3 className="text-[10px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-widest block mb-4">
              Product
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="#features"
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white transition-colors font-medium"
                >
                  Features
                </a>
              </li>
              <li>
                <a
                  href="#demo"
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white transition-colors font-medium"
                >
                  Interactive Demo
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-[10px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-widest block mb-4">
              Security
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="#security"
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white transition-colors font-medium"
                >
                  Data Privacy
                </a>
              </li>
              <li>
                <a
                  href="#security"
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white transition-colors font-medium"
                >
                  Audit Trails
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-[10px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-widest block mb-4">
              Developer
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="#tech"
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white transition-colors font-medium"
                >
                  Architecture
                </a>
              </li>
              <li>
                <Link
                  href="/auth/login"
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white transition-colors font-medium"
                >
                  API Portal
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Copyright statement bottom row */}
      <div className="mx-auto max-w-7xl px-4 py-6 border-t border-neutral-200/30 dark:border-neutral-850/60 sm:px-6 md:flex md:items-center md:justify-between lg:px-8">
        <p className="text-center text-[10px] text-neutral-400 dark:text-neutral-500 font-mono tracking-tight md:text-left">
          &copy; {new Date().getFullYear()} DocuMind AI. All rights reserved. Verifiable Document
          SaaS monorepo pipeline.
        </p>
      </div>
    </footer>
  );
}
