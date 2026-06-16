"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/useAuthStore";
import { sdk } from "@/store/useAuthStore";
import AuthLayout from "../AuthLayout";
import { GoogleButton } from "../GoogleButton";
import { Input, Button } from "@documind/ui";
import { Loader2, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function SignupPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const isAuthenticated = useAuthStore((s) => !!s.token);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <div className="relative">
          <Loader2 className="h-8 w-8 animate-spin text-primary relative z-10" />
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse" />
        </div>
        <p className="mt-4 text-sm text-muted-foreground font-medium animate-pulse">Entering Workspace...</p>
      </div>
    );
  }

  const handleGoogleSuccess = async (token: string) => {
    setGoogleLoading(true);
    setError(null);
    try {
      const res = await sdk.googleLogin(token);
      const user = res.user || await sdk.getMe();
      setAuth(user, res.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to authenticate with Google");
      setGoogleLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !name) return;

    setLoading(true);
    setError(null);
    try {
      const res = await sdk.signup(name, email, password);
      if (res.access_token) {
        setAuth(res, res.access_token);
      } else {
        const loginRes = await sdk.login(email, password);
        const user = loginRes.user || await sdk.getMe();
        setAuth(user, loginRes.access_token);
      }
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to create account");
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Create Workspace</h2>
        <p className="text-sm text-muted-foreground mt-1">Join the next generation of document intelligence</p>
      </div>

      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-xl text-center"
        >
          {error}
        </motion.div>
      )}

      <GoogleButton 
        onSuccess={handleGoogleSuccess} 
        onError={setError} 
        isLoading={googleLoading} 
        setIsLoading={setGoogleLoading}
        text="Sign up with Google"
      />

      <div className="my-6 flex items-center">
        <div className="flex-1 border-t border-border/50"></div>
        <span className="px-3 text-xs text-muted-foreground uppercase tracking-wider font-semibold">Or</span>
        <div className="flex-1 border-t border-border/50"></div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5 group">
          <label className="text-xs font-semibold text-foreground uppercase tracking-wide group-focus-within:text-primary transition-colors">Full Name</label>
          <Input
            type="text"
            placeholder="Jane Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="bg-background/50 h-11 focus-visible:ring-primary/20 transition-all duration-300"
            required
          />
        </div>
        <div className="space-y-1.5 group">
          <label className="text-xs font-semibold text-foreground uppercase tracking-wide group-focus-within:text-primary transition-colors">Work Email</label>
          <Input
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-background/50 h-11 focus-visible:ring-primary/20 transition-all duration-300"
            required
          />
        </div>
        <div className="space-y-1.5 group">
          <label className="text-xs font-semibold text-foreground uppercase tracking-wide group-focus-within:text-primary transition-colors">Password</label>
          <Input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-background/50 h-11 focus-visible:ring-primary/20 transition-all duration-300"
            required
            minLength={8}
          />
        </div>
        <Button
          type="submit"
          className="w-full h-11 mt-2 flex items-center justify-center gap-2 group relative overflow-hidden"
          disabled={loading || googleLoading}
        >
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out pointer-events-none" />
          <span className="relative z-10 flex items-center gap-2">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create Account"}
            {!loading && <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />}
          </span>
        </Button>
      </form>

      <div className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/auth/login" className="text-primary hover:underline font-semibold">
          Sign In
        </Link>
      </div>
    </AuthLayout>
  );
}
