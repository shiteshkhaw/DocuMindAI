"use client";

import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { GoogleOAuthProvider } from "@react-oauth/google";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      }),
  );

  React.useEffect(() => {
    // Warm up Render backend API (addresses free tier sleep cold start)
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "https://documind-api-qzei.onrender.com";
    fetch(`${apiBaseUrl.replace(/\/$/, "")}/health`).catch((err) => {
      console.warn("API pre-warm ping failed", err);
    });
  }, []);

  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "missing-client-id"}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </GoogleOAuthProvider>
  );
}
