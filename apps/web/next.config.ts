import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@documind/ui", "@documind/types", "@documind/sdk", "@documind/prompts"],
  /* config options here */
};

export default nextConfig;
