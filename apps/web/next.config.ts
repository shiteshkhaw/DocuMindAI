import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@documind/ui", "@documind/types", "@documind/sdk", "@documind/prompts"],
  /* config options here */
};

// Wrap the configuration with Sentry options
export default withSentryConfig(nextConfig, {
  // For all available options, see:
  // https://github.com/getsentry/sentry-javascript/blob/master/packages/nextjs/src/config/types.ts

  org: "documind-ai",
  project: "documind-frontend",

  // Only print logs when there's an error during uploading source maps
  silent: true,

  // Forwards the uploads to Sentry
  widenClientFileUpload: true,

  // Route browser requests to Sentry through a Next.js rewrite to bypass ad-blockers
  tunnelRoute: "/monitoring",

  // Automatically tree-shake Sentry logger statements
  disableLogger: true,
});
