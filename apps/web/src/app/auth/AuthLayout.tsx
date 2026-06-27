"use client";

import React, { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Brain, Shield, Lock, Layers } from "lucide-react";
import Image from "next/image";
import logoImg from "../../../public/logo.png";

// Particle System Background
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
      const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          size: Math.random() * 1.5 + 0.5,
        });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(100, 100, 255, 0.4)";
      ctx.strokeStyle = "rgba(100, 100, 255, 0.05)";

      particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener("resize", resize);
    resize();
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none opacity-40 dark:opacity-60" />;
};

const TrustIndicators = () => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.6, duration: 0.8 }}
    className="mt-12 grid grid-cols-2 gap-4 max-w-sm"
  >
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/30 px-3 py-2 rounded-lg border border-border/50 backdrop-blur-md">
      <Shield className="h-3.5 w-3.5 text-emerald-500" /> Private by Design
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/30 px-3 py-2 rounded-lg border border-border/50 backdrop-blur-md">
      <Brain className="h-3.5 w-3.5 text-indigo-500" /> AI Powered
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/30 px-3 py-2 rounded-lg border border-border/50 backdrop-blur-md">
      <Lock className="h-3.5 w-3.5 text-violet-500" /> Encrypted Storage
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/30 px-3 py-2 rounded-lg border border-border/50 backdrop-blur-md">
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
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">Why organizations trust DocuMind</p>
      <div className="flex gap-8">
        <div>
          <div className="text-2xl font-bold text-foreground">{docs.toLocaleString()}+</div>
          <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">Documents Analyzed</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-foreground">{contras.toLocaleString()}+</div>
          <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">Contradictions Detected</div>
        </div>
      </div>
    </motion.div>
  );
};

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    setMousePos({
      x: (e.clientX / window.innerWidth - 0.5) * 20,
      y: (e.clientY / window.innerHeight - 0.5) * 20,
    });
  };

  return (
    <div 
      onMouseMove={handleMouseMove}
      className="min-h-screen w-full flex bg-background relative overflow-hidden select-none"
    >
      {/* Animated Aurora Layer */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.5, 0.3],
            x: [0, 50, 0],
            y: [0, -50, 0]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute -top-[20%] -right-[10%] w-[70vw] h-[70vw] rounded-full bg-indigo-500/10 blur-[120px] dark:bg-indigo-500/5 mix-blend-screen"
        />
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.4, 0.2],
            x: [0, -30, 0],
            y: [0, 50, 0]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute -bottom-[20%] -left-[10%] w-[60vw] h-[60vw] rounded-full bg-violet-500/10 blur-[120px] dark:bg-violet-500/5 mix-blend-screen"
        />
        <motion.div
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.2, 0.3, 0.2]
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[30%] left-[30%] w-[40vw] h-[40vw] rounded-full bg-blue-500/10 blur-[100px] dark:bg-blue-500/5 mix-blend-screen"
        />
      </div>

      <ParticleSystem />

      <div className="w-full h-full flex flex-col lg:flex-row z-10">
        {/* Left Branding Area */}
        <div className="hidden lg:flex flex-1 flex-col justify-center p-16 xl:p-24 relative">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <motion.div 
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="flex h-16 w-16 items-center justify-center rounded-2xl bg-transparent overflow-hidden shadow-lg shadow-primary/10 mb-8 border border-border/50"
            >
              <Image src={logoImg} alt="DocuMind AI Logo" className="h-full w-full object-cover mix-blend-multiply" priority />
            </motion.div>
            
            <h1 className="text-4xl xl:text-5xl font-bold text-foreground tracking-tight leading-tight mb-4">
              Your Intelligence <br/> Workspace
            </h1>
            <p className="text-xl text-muted-foreground font-medium">
              Analyze. Verify. Trust.
            </p>

            <TrustIndicators />
            <MetricsCounter />
          </motion.div>
        </div>

        {/* Right Auth Card Area */}
        <div className="flex-1 flex items-center justify-center p-8 lg:p-16 relative">
          <motion.div
            style={{
              rotateX: mousePos.y * -0.5,
              rotateY: mousePos.x * 0.5,
              transformPerspective: 1000
            }}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 100 }}
            className="w-full max-w-[420px] bg-card/60 backdrop-blur-2xl border border-border/50 rounded-3xl p-8 shadow-2xl relative overflow-hidden"
          >
            {/* Inner dynamic glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-50 pointer-events-none" />
            
            <div className="relative z-10">
              {children}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
