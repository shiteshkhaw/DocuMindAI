"use client";

import React, { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Brain, Shield, Lock, Layers } from "lucide-react";
import Image from "next/image";
import logoImg from "../../../public/logo.png";

// Particle System Background
// Lightweight GPU-friendly Particle System
const ParticleSystem = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let particles: { x: number; y: number; vx: number; vy: number; size: number }[] = [];
    let animationFrameId: number;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const initParticles = () => {
      particles = [];
      const particleCount = 28;
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.25,
          vy: (Math.random() - 0.5) * 0.25,
          size: Math.random() * 1.5 + 0.8,
        });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(99, 102, 241, 0.35)";

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = canvas.width;
        else if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        else if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener("resize", resize, { passive: true });
    resize();
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 z-0 pointer-events-none opacity-40 dark:opacity-60"
    />
  );
};

const TrustIndicators = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.6, duration: 0.8 }}
    className="mt-12 grid grid-cols-2 gap-4 max-w-sm"
  >
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50 shadow-2xs">
      <Shield className="h-3.5 w-3.5 text-emerald-500" /> Private by Design
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50 shadow-2xs">
      <Brain className="h-3.5 w-3.5 text-indigo-500" /> AI Powered
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50 shadow-2xs">
      <Lock className="h-3.5 w-3.5 text-violet-500" /> Encrypted Storage
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50 shadow-2xs">
      <Layers className="h-3.5 w-3.5 text-blue-500" /> Workspace Isolation
    </div>
  </motion.div>
);

const MetricsCounter = () => {
  const [docs, setDocs] = useState(0);
  const [contras, setContras] = useState(0);

  useEffect(() => {
    let frame = 0;
    const interval = setInterval(() => {
      frame++;
      setDocs(Math.min(14205, Math.floor(frame * 123)));
      setContras(Math.min(3892, Math.floor(frame * 34)));
      if (frame > 150) clearInterval(interval);
    }, 16);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1, duration: 1 }}
      className="mt-16 pt-8 border-t border-border/30"
    >
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
        Why organizations trust DocuMind
      </p>
      <div className="flex gap-8">
        <div>
          <div className="text-2xl font-bold text-foreground">{docs.toLocaleString()}+</div>
          <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">
            Documents Analyzed
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-foreground">{contras.toLocaleString()}+</div>
          <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">
            Contradictions Detected
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen w-full flex bg-background relative overflow-hidden select-none">
      {/* High-performance GPU-composited Aurora Layer */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none transform-gpu">
        <div
          className="absolute -top-[20%] -right-[10%] w-[65vw] h-[65vw] rounded-full opacity-60"
          style={{
            background:
              "radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%)",
          }}
        />
        <div
          className="absolute -bottom-[20%] -left-[10%] w-[55vw] h-[55vw] rounded-full opacity-50"
          style={{
            background:
              "radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, rgba(139, 92, 246, 0) 70%)",
          }}
        />
      </div>

      <ParticleSystem />

      <div className="w-full h-full flex flex-col lg:flex-row z-10">
        {/* Left Branding Area */}
        <div className="hidden lg:flex flex-1 flex-col justify-center p-16 xl:p-24 relative">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="flex h-16 w-16 items-center justify-center rounded-2xl bg-transparent overflow-hidden shadow-lg shadow-primary/10 mb-8 border border-border/50"
            >
              <Image
                src={logoImg}
                alt="DocuMind AI Logo"
                className="h-full w-full object-cover mix-blend-multiply"
                priority
              />
            </motion.div>

            <h1 className="text-4xl xl:text-5xl font-bold text-foreground tracking-tight leading-tight mb-4">
              Your Intelligence <br /> Workspace
            </h1>
            <p className="text-xl text-muted-foreground font-medium">Analyze. Verify. Trust.</p>

            <TrustIndicators />
            <MetricsCounter />
          </motion.div>
        </div>

        {/* Right Auth Card Area */}
        <div className="flex-1 flex items-center justify-center p-8 lg:p-16 relative">
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 120 }}
            className="w-full max-w-[420px] bg-card/95 border border-border/60 rounded-3xl p-8 shadow-xl relative overflow-hidden transform-gpu"
          >
            {/* Inner dynamic glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-50 pointer-events-none" />

            <div className="relative z-10">{children}</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
