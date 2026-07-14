"use client";

import React, { useState, useEffect } from "react";

import {
  FileText,
  Brain,
  ArrowRight,
  Sparkles,
  ShieldAlert,
  Network,
  CheckCircle2,
  AlertCircle,
  FileCheck,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// Helper for classes
import { cn } from "@documind/ui";

// Mock Data for the simulator
const DEMO_DOCS = [
  { id: "d1", name: "Sales_Headcount_Contract_2026.pdf", size: "45 KB", type: "PDF", pages: 12 },
  { id: "d2", name: "Alpha_Project_Charter_v2.docx", size: "120 KB", type: "DOCX", pages: 8 },
];

const PRESETS = [
  {
    question: "Analyze headcount targets and identify discrepancies.",
    response:
      "I have audited both **Sales_Headcount_Contract_2026.pdf** and **Alpha_Project_Charter_v2.docx** across all pages.\n\n### Core Inconsistency Found:\nThere is a critical **headcount target mismatch**:\n- **Alpha_Project_Charter_v2.docx (Page 4)**: Mandates a hiring target of **60 employees**.\n- **Sales_Headcount_Contract_2026.pdf (Page 8)**: Limits vendor headcount to a maximum of **45 employees**.\n\nThis represents an unbudgeted deficit of **15 resources**.",
    citations: [
      {
        doc: "Sales_Headcount_Contract_2026.pdf",
        page: 8,
        snippet:
          "The vendor-allocated expenses shall under no circumstances support headcount exceeding 45 full-time personnel.",
      },
      {
        doc: "Alpha_Project_Charter_v2.docx",
        page: 4,
        snippet:
          "Project Alpha mandates the onboarding of 60 full-time resources by Q4 2026 to hit phase 2 launch timelines.",
      },
    ],
  },
  {
    question: "Verify project kickoff timeline against billing start dates.",
    response:
      "A **timeline misalignment** has been identified between Section 1.2 of the Charter and Section 2 of the Contract:\n\n- **Project Charter (Page 1)**: Kickoff and onboarding schedule is set to launch on **October 10, 2026**.\n- **Headcount Contract (Page 2)**: Billing commencement and resource support is restricted to begin on or after **November 1, 2026**.\n\nThis creates a **22-day operational gap** where vendor resources will perform services prior to active billing cycles.",
    citations: [
      {
        doc: "Alpha_Project_Charter_v2.docx",
        page: 1,
        snippet: "Kickoff and resource onboarding is scheduled to initiate on October 10, 2026.",
      },
      {
        doc: "Sales_Headcount_Contract_2026.pdf",
        page: 2,
        snippet:
          "The effective date of this agreement and commencement of active billing is November 1, 2026.",
      },
    ],
  },
];

const DEMO_CONTRADICTIONS = [
  {
    id: "c1",
    severity: "high",
    type: "Numerical Discrepancy",
    title: "Headcount limit mismatch: 45 vs 60 resources",
    description:
      "The project plan requires staffing 60 full-time resources, while the vendor expenditure contract imposes a hard budgetary ceiling of 45 resources. This leaves a gap of 15 resources unaccounted for in billing contracts.",
    docs: ["Alpha_Project_Charter_v2.docx", "Sales_Headcount_Contract_2026.pdf"],
  },
  {
    id: "c2",
    severity: "medium",
    type: "Timeline Conflict",
    title: "Kickoff date precedes billing commencement",
    description:
      "Onboarding and kickoff are scheduled for October 10, 2026. However, the commercial contract does not authorize active billing rates until November 1, 2026, risking unbilled resource utilization.",
    docs: ["Alpha_Project_Charter_v2.docx", "Sales_Headcount_Contract_2026.pdf"],
  },
];

const DEMO_ENTITIES = [
  {
    id: "e1",
    text: "DocuMind Corp",
    type: "ORGANIZATION",
    frequency: 8,
    related: ["Acme Inc", "John Doe"],
    x: 160,
    y: 150,
  },
  {
    id: "e2",
    text: "Acme Inc",
    type: "ORGANIZATION",
    frequency: 6,
    related: ["DocuMind Corp", "John Doe"],
    x: 440,
    y: 150,
  },
  {
    id: "e3",
    text: "John Doe",
    type: "PERSON",
    frequency: 4,
    related: ["DocuMind Corp", "Acme Inc"],
    x: 300,
    y: 70,
  },
  {
    id: "e4",
    text: "60 resources",
    type: "CAPACITY",
    frequency: 5,
    related: ["DocuMind Corp"],
    x: 230,
    y: 220,
  },
  {
    id: "e5",
    text: "45 resources",
    type: "CAPACITY",
    frequency: 4,
    related: ["Acme Inc"],
    x: 370,
    y: 220,
  },
];

export default function InteractiveDemo() {
  const [activeTab, setActiveTab] = useState<"chat" | "contradictions" | "entities" | "trust">(
    "chat",
  );

  // Chat specific state
  const [selectedPresetIndex, setSelectedPresetIndex] = useState<number | null>(null);
  const [messages, setMessages] = useState<any[]>([
    {
      role: "assistant",
      content:
        "Select one of the quick audit prompts in the right sidebar or click on the documents list to run compiler checks.",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [typedResponse, setTypedResponse] = useState("");
  const [activeCitations, setActiveCitations] = useState<any[]>([]);

  // Entity specific state
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Trigger RAG compile simulator
  const handleTriggerPreset = (index: number) => {
    if (isTyping) return;
    setSelectedPresetIndex(index);
    const preset = PRESETS[index];

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: preset.question }]);

    setIsTyping(true);
    setTypedResponse("");
    setActiveCitations([]);

    // Simulate thinking/streaming
    setTimeout(() => {
      let charIndex = 0;
      const textToType = preset.response;
      const interval = setInterval(() => {
        setTypedResponse((prev) => prev + textToType.charAt(charIndex));
        charIndex++;
        if (charIndex >= textToType.length) {
          clearInterval(interval);
          setIsTyping(false);
          // Set final message and citations
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: textToType, citations: preset.citations },
          ]);
          setTypedResponse("");
          setActiveCitations(preset.citations);
        }
      }, 7); // Fast stream typing
    }, 800);
  };

  // Node Colors helper
  const getNodeColor = (type: string) => {
    switch (type) {
      case "ORGANIZATION":
        return "fill-indigo-500 stroke-indigo-200 dark:stroke-indigo-900";
      case "PERSON":
        return "fill-pink-500 stroke-pink-200 dark:stroke-pink-900";
      case "CAPACITY":
        return "fill-amber-500 stroke-amber-200 dark:stroke-amber-900";
      default:
        return "fill-neutral-500 stroke-neutral-200 dark:stroke-neutral-800";
    }
  };

  // Re-run animation gauge
  const [trustScoreFill, setTrustScoreFill] = useState(0);
  useEffect(() => {
    let timer: NodeJS.Timeout | undefined;
    if (activeTab === "trust") {
      setTrustScoreFill(0);
      timer = setTimeout(() => {
        setTrustScoreFill(84);
      }, 200);
    }
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [activeTab]);

  return (
    <section
      id="demo"
      className="py-20 sm:py-28 bg-[#f5f4f0] dark:bg-[#0c0c0e] border-t border-b border-neutral-200/50 dark:border-neutral-900/50 transition-colors duration-300"
      aria-labelledby="demo-heading"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-[10px] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            Interactive Showcase
          </h2>
          <p
            id="demo-heading"
            className="mt-3 text-3xl font-bold tracking-tight text-neutral-900 dark:text-white sm:text-4xl font-sans"
          >
            Explore the DocuMind workspace.
          </p>
          <p className="mt-4 text-base text-neutral-500 dark:text-neutral-400 font-medium">
            Test our structural RAG indexer, check logical contract contradictions, and view
            cross-document entity mappings interactively.
          </p>
        </div>

        {/* Workspace Shell */}
        <div className="w-full border border-neutral-200/70 bg-[#fcfbfa] dark:border-neutral-800/80 dark:bg-[#0f0f12] rounded-2xl shadow-xl overflow-hidden flex flex-col md:flex-row h-[620px] transition-all duration-300">
          {/* Workspace Shell Sidebar */}
          <div className="w-full md:w-64 border-r border-neutral-200/60 dark:border-neutral-800/60 bg-[#f8f7f3] dark:bg-[#0c0c0e] flex flex-col shrink-0">
            {/* Header Workspace Identifier */}
            <div className="p-4 border-b border-neutral-200/60 dark:border-neutral-800/60 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded bg-indigo-600 flex items-center justify-center text-white text-[10px] font-extrabold">
                  D
                </div>
                <div>
                  <h4 className="text-xs font-bold text-neutral-800 dark:text-neutral-200 leading-none">
                    Demo Workspace
                  </h4>
                  <span className="text-[9px] text-neutral-400 dark:text-neutral-500 font-medium mt-1 inline-block">
                    SaaS Research
                  </span>
                </div>
              </div>
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>

            {/* Ingestion Area */}
            <div className="p-4 space-y-4 flex-1 overflow-y-auto">
              <div className="space-y-2">
                <span className="text-[9px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider block">
                  Routing Model
                </span>
                <div className="grid grid-cols-3 gap-0.5 bg-neutral-200/50 dark:bg-neutral-800/50 p-0.5 rounded-lg text-[10px] font-semibold text-neutral-500">
                  <div className="bg-white dark:bg-neutral-700 text-neutral-800 dark:text-white text-center py-1 rounded shadow-xs cursor-pointer">
                    RAG v3
                  </div>
                  <div className="text-center py-1 hover:text-neutral-800 dark:hover:text-white cursor-pointer transition-colors">
                    R1
                  </div>
                  <div className="text-center py-1 hover:text-neutral-800 dark:hover:text-white cursor-pointer transition-colors">
                    Claude
                  </div>
                </div>
              </div>

              {/* Indexed Files List */}
              <div className="space-y-2.5">
                <span className="text-[9px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider block">
                  Indexed Vault
                </span>
                <div className="space-y-1.5">
                  {DEMO_DOCS.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center gap-2.5 p-2 bg-white dark:bg-neutral-900 border border-neutral-200/50 dark:border-neutral-800/80 rounded-xl shadow-2xs"
                    >
                      <div className="h-7 w-7 rounded bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                        <FileText className="h-3.5 w-3.5" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-[10px] font-bold text-neutral-800 dark:text-neutral-200 truncate leading-none">
                          {doc.name}
                        </p>
                        <span className="text-[8px] text-neutral-400 dark:text-neutral-500 font-medium block mt-1">
                          {doc.size} • {doc.pages} pages
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Action compilation footer */}
            <div className="p-4 border-t border-neutral-200/60 dark:border-neutral-800/60 bg-neutral-100/30 dark:bg-neutral-900/10">
              <button
                disabled
                className="w-full py-2.5 rounded-xl text-[10px] font-bold bg-neutral-200 text-neutral-400 dark:bg-neutral-800 dark:text-neutral-600 flex items-center justify-center gap-1.5 cursor-not-allowed"
              >
                <Sparkles className="h-3 w-3" /> Compiled & Indexed
              </button>
            </div>
          </div>

          {/* Main workspace contents */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#fcfbfa] dark:bg-[#0f0f12]">
            {/* Top Workspace Tab controls */}
            <div className="h-12 border-b border-neutral-200/60 dark:border-neutral-800/60 px-4 flex items-center gap-4 bg-[#f8f7f3] dark:bg-[#0c0c0e] overflow-x-auto overflow-y-hidden select-none shrink-0">
              <button
                onClick={() => setActiveTab("chat")}
                className={cn(
                  "h-full text-[11px] font-bold flex items-center gap-1.5 border-b-2 px-1 transition-all",
                  activeTab === "chat"
                    ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
                    : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-300",
                )}
              >
                <Brain className="h-3.5 w-3.5" /> Conversational RAG
              </button>
              <button
                onClick={() => setActiveTab("contradictions")}
                className={cn(
                  "h-full text-[11px] font-bold flex items-center gap-1.5 border-b-2 px-1 transition-all",
                  activeTab === "contradictions"
                    ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
                    : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-300",
                )}
              >
                <ShieldAlert className="h-3.5 w-3.5" /> Collision scan
              </button>
              <button
                onClick={() => setActiveTab("entities")}
                className={cn(
                  "h-full text-[11px] font-bold flex items-center gap-1.5 border-b-2 px-1 transition-all",
                  activeTab === "entities"
                    ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
                    : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-300",
                )}
              >
                <Network className="h-3.5 w-3.5" /> Entity Graph
              </button>
              <button
                onClick={() => setActiveTab("trust")}
                className={cn(
                  "h-full text-[11px] font-bold flex items-center gap-1.5 border-b-2 px-1 transition-all",
                  activeTab === "trust"
                    ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
                    : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-300",
                )}
              >
                <FileCheck className="h-3.5 w-3.5" /> Compliance score
              </button>
            </div>

            {/* Display screen body */}
            <div className="flex-1 overflow-hidden relative">
              <AnimatePresence mode="wait">
                {/* 1. Conversational RAG Tab */}
                {activeTab === "chat" && (
                  <motion.div
                    key="chat"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="h-full flex flex-col md:flex-row overflow-hidden"
                  >
                    {/* Chat Feed */}
                    <div className="flex-1 flex flex-col h-full border-r border-neutral-200/50 dark:border-neutral-800/50 overflow-hidden">
                      <div className="flex-1 p-4 space-y-4 overflow-y-auto min-h-0 select-text">
                        {messages.map((msg, idx) => (
                          <div
                            key={idx}
                            className={cn(
                              "flex gap-3",
                              msg.role === "user" ? "justify-end" : "justify-start",
                            )}
                          >
                            <div
                              className={cn(
                                "max-w-[85%] rounded-2xl p-3 text-[11px] leading-relaxed font-sans shadow-2xs border",
                                msg.role === "user"
                                  ? "bg-indigo-600 text-white border-transparent"
                                  : "bg-white border-neutral-200/60 text-neutral-800 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-200",
                              )}
                            >
                              {/* Content format parser (Markdown formatting) */}
                              <div className="whitespace-pre-wrap">{msg.content}</div>
                            </div>
                          </div>
                        ))}

                        {/* Stream typing placeholder */}
                        {isTyping && (
                          <div className="flex gap-3 justify-start">
                            <div className="max-w-[85%] rounded-2xl p-3 text-[11px] leading-relaxed font-sans bg-white border border-neutral-200/60 text-neutral-800 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-200">
                              <p className="whitespace-pre-wrap">{typedResponse}</p>
                              <span className="inline-block w-1.5 h-3.5 bg-indigo-500 animate-pulse ml-0.5" />
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Chat Input Field placeholder */}
                      <div className="p-3 border-t border-neutral-200/60 dark:border-neutral-800/60 bg-[#f8f7f3] dark:bg-[#0c0c0e]">
                        <div className="w-full bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800/80 rounded-xl px-3.5 py-2.5 flex items-center justify-between text-[11px] text-neutral-400">
                          <span>Ask a question about the headcount targets...</span>
                          <button className="h-6 w-6 rounded-lg bg-indigo-600 flex items-center justify-center text-white cursor-not-allowed">
                            <ArrowRight className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Chat Sidebar Controls (Presets & Citation Viewer) */}
                    <div className="w-full md:w-56 shrink-0 p-4 bg-[#fcfbfa] dark:bg-[#0f0f12] overflow-y-auto space-y-5 h-full">
                      <div className="space-y-2">
                        <span className="text-[9px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider block">
                          Preset Audits
                        </span>
                        <div className="space-y-1.5">
                          {PRESETS.map((preset, index) => (
                            <button
                              key={index}
                              onClick={() => handleTriggerPreset(index)}
                              disabled={isTyping}
                              className={cn(
                                "w-full text-left p-2.5 rounded-xl border text-[10px] font-semibold transition-all duration-200 leading-tight block",
                                selectedPresetIndex === index
                                  ? "bg-indigo-50/50 border-indigo-200/80 text-indigo-700 dark:bg-indigo-950/20 dark:border-indigo-900/50 dark:text-indigo-400 font-bold"
                                  : "bg-white border-neutral-200 hover:bg-neutral-50 text-neutral-600 dark:bg-neutral-900 dark:border-neutral-800 dark:hover:bg-neutral-800 dark:text-neutral-400",
                              )}
                            >
                              {preset.question}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Dynamic Citation Viewer */}
                      {activeCitations.length > 0 && (
                        <div className="space-y-2 pt-2 border-t border-neutral-200/50 dark:border-neutral-800/50 animate-fade-in-up">
                          <span className="text-[9px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider block">
                            Source Citations
                          </span>
                          <div className="space-y-2">
                            {activeCitations.map((cit, idx) => (
                              <div
                                key={idx}
                                className="p-2 border border-neutral-200/60 bg-white dark:border-neutral-800/80 dark:bg-neutral-900/60 rounded-xl text-[9px] text-neutral-500 space-y-1 leading-normal"
                              >
                                <div className="flex items-center justify-between text-neutral-700 dark:text-neutral-300 font-bold">
                                  <span className="truncate max-w-[110px]">{cit.doc}</span>
                                  <span className="shrink-0 bg-neutral-100 dark:bg-neutral-800 px-1 py-0.5 rounded text-[8px]">
                                    Page {cit.page}
                                  </span>
                                </div>
                                <p className="italic text-neutral-500 mt-1">
                                  &ldquo;{cit.snippet}&rdquo;
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}

                {/* 2. Collision Scan (Contradiction Intelligence) */}
                {activeTab === "contradictions" && (
                  <motion.div
                    key="contradictions"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="h-full p-4 overflow-y-auto space-y-4"
                  >
                    <div className="flex items-center justify-between pb-2 border-b border-neutral-200/50 dark:border-neutral-800/50">
                      <div>
                        <h4 className="text-xs font-bold text-neutral-800 dark:text-neutral-200">
                          Scan Timeline Conflicts
                        </h4>
                        <span className="text-[9px] text-neutral-400 dark:text-neutral-500 font-medium">
                          Cross-document verification results
                        </span>
                      </div>
                      <span className="bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                        2 conflicts detected
                      </span>
                    </div>

                    <div className="grid grid-cols-1 gap-4">
                      {DEMO_CONTRADICTIONS.map((contra) => (
                        <div
                          key={contra.id}
                          className="p-3.5 border border-neutral-200/80 bg-white dark:border-neutral-800/80 dark:bg-neutral-900/40 rounded-xl space-y-2 text-left shadow-2xs relative overflow-hidden group"
                        >
                          {/* Severity Indicator */}
                          <div
                            className={cn(
                              "absolute top-0 left-0 bottom-0 w-1",
                              contra.severity === "high" ? "bg-rose-500" : "bg-amber-500",
                            )}
                          />

                          <div className="pl-1.5 flex items-center justify-between">
                            <span
                              className={cn(
                                "text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border",
                                contra.severity === "high"
                                  ? "bg-rose-500/10 text-rose-600 border-rose-500/20"
                                  : "bg-amber-500/10 text-amber-600 border-amber-500/20",
                              )}
                            >
                              {contra.type}
                            </span>
                            <span className="text-[8px] font-mono text-neutral-400 dark:text-neutral-500">
                              ID: {contra.id}
                            </span>
                          </div>

                          <div className="pl-1.5 space-y-1">
                            <h5 className="text-[11px] font-bold text-neutral-800 dark:text-neutral-100">
                              {contra.title}
                            </h5>
                            <p className="text-[10px] leading-relaxed text-neutral-500 dark:text-neutral-400 font-medium">
                              {contra.description}
                            </p>
                          </div>

                          {/* Source Files tags */}
                          <div className="pl-1.5 pt-2 flex items-center gap-1.5 border-t border-neutral-200/50 dark:border-neutral-800/40 mt-3 text-[8px] text-neutral-400">
                            <span>Compared Sources:</span>
                            {contra.docs.map((doc, idx) => (
                              <span
                                key={idx}
                                className="bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 font-semibold px-1.5 py-0.5 rounded"
                              >
                                {doc}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* 3. Entity Connection Map Graph */}
                {activeTab === "entities" && (
                  <motion.div
                    key="entities"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="h-full flex flex-col overflow-hidden"
                  >
                    <div className="p-4 border-b border-neutral-200/50 dark:border-neutral-800/50 flex justify-between items-center shrink-0">
                      <div>
                        <h4 className="text-xs font-bold text-neutral-800 dark:text-neutral-200">
                          Interactive Entity Connections
                        </h4>
                        <span className="text-[9px] text-neutral-400 dark:text-neutral-500 font-medium">
                          Hover over nodes to illuminate cross-document relations
                        </span>
                      </div>
                    </div>

                    <div className="flex-1 bg-neutral-50/50 dark:bg-[#0c0c0e]/30 relative flex items-center justify-center p-4">
                      {/* SVG connections drawer */}
                      <svg
                        viewBox="0 0 600 300"
                        className="w-full h-full max-w-[550px] select-none"
                      >
                        {/* Render line connectors */}
                        {DEMO_ENTITIES.map((node) =>
                          node.related.map((relName) => {
                            const targetNode = DEMO_ENTITIES.find((n) => n.text === relName);
                            if (
                              !targetNode ||
                              DEMO_ENTITIES.indexOf(node) > DEMO_ENTITIES.indexOf(targetNode)
                            )
                              return null;

                            const isHighlight =
                              hoveredNode === node.text || hoveredNode === targetNode.text;

                            return (
                              <line
                                key={`${node.text}-${targetNode.text}`}
                                x1={node.x}
                                y1={node.y}
                                x2={targetNode.x}
                                y2={targetNode.y}
                                stroke={isHighlight ? "#6366f1" : "#cbd5e1"}
                                strokeWidth={isHighlight ? 2 : 1}
                                strokeDasharray={isHighlight ? "none" : "3,3"}
                                opacity={hoveredNode && !isHighlight ? 0.15 : 0.6}
                                className="transition-all duration-300"
                              />
                            );
                          }),
                        )}

                        {/* Render Nodes */}
                        {DEMO_ENTITIES.map((node) => {
                          const size = 12 + Math.min(8, node.frequency * 1.5);
                          const isHovered = hoveredNode === node.text;
                          const isDimmed =
                            hoveredNode && !isHovered && !node.related.includes(hoveredNode);

                          return (
                            <g
                              key={node.text}
                              className="cursor-pointer transition-all duration-300"
                              onMouseEnter={() => setHoveredNode(node.text)}
                              onMouseLeave={() => setHoveredNode(null)}
                              opacity={isDimmed ? 0.3 : 1}
                            >
                              {isHovered && (
                                <circle
                                  cx={node.x}
                                  cy={node.y}
                                  r={size + 6}
                                  fill="none"
                                  stroke="#6366f1"
                                  strokeWidth={1.5}
                                  className="animate-pulse"
                                />
                              )}
                              <circle
                                cx={node.x}
                                cy={node.y}
                                r={size}
                                className={cn(
                                  "stroke-white stroke-[1.5px]",
                                  getNodeColor(node.type),
                                )}
                              />
                              <text
                                x={node.x}
                                y={node.y + size + 11}
                                textAnchor="middle"
                                className="fill-neutral-700 dark:fill-neutral-300 text-[8px] font-bold select-none pointer-events-none"
                              >
                                {node.text}
                              </text>
                            </g>
                          );
                        })}
                      </svg>
                    </div>
                  </motion.div>
                )}

                {/* 4. Trust Gauge and Compliance Checklist */}
                {activeTab === "trust" && (
                  <motion.div
                    key="trust"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="h-full p-4 overflow-y-auto flex flex-col md:flex-row gap-6 items-center"
                  >
                    {/* Circle Score Gauge */}
                    <div className="flex flex-col items-center justify-center p-4 bg-white dark:bg-neutral-900 border border-neutral-200/50 dark:border-neutral-800/80 rounded-2xl w-full md:w-56 shrink-0 shadow-2xs">
                      <div className="relative h-28 w-28 flex items-center justify-center">
                        <svg className="h-full w-full transform -rotate-90" viewBox="0 0 100 100">
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            stroke="var(--border, #cbd5e1)"
                            strokeWidth="8"
                            fill="transparent"
                            className="opacity-25"
                          />
                          <motion.circle
                            cx="50"
                            cy="50"
                            r="40"
                            stroke="#6366f1"
                            strokeWidth="8"
                            fill="transparent"
                            strokeDasharray="251.2"
                            strokeDashoffset={251.2 - (251.2 * trustScoreFill) / 100}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                          />
                        </svg>
                        <div className="absolute flex flex-col items-center justify-center">
                          <span className="text-2xl font-extrabold text-neutral-800 dark:text-white leading-none">
                            {trustScoreFill}%
                          </span>
                          <span className="text-[8px] text-neutral-400 dark:text-neutral-500 font-bold uppercase tracking-wider mt-1">
                            Compliance
                          </span>
                        </div>
                      </div>
                      <p className="text-[10px] text-neutral-500 dark:text-neutral-400 mt-4 font-semibold text-center leading-normal">
                        Workspace index shows high risk discrepancies in headcount budgeting.
                      </p>
                    </div>

                    {/* Auditor Checklist items */}
                    <div className="flex-1 space-y-3 w-full">
                      <span className="text-[9px] font-bold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider block">
                        Workspace Integrity Checklist
                      </span>

                      <div className="space-y-2">
                        <div className="flex items-center gap-3 p-2.5 rounded-xl border border-neutral-200 bg-white dark:border-neutral-850 dark:bg-neutral-900/50 text-[10px] text-neutral-700 dark:text-neutral-300">
                          <AlertCircle className="h-4 w-4 text-rose-500 shrink-0" />
                          <div className="flex-1">
                            <span className="font-bold">Hiring Count Constraints</span>
                            <span className="text-neutral-400 block mt-0.5">
                              Charter mandates 60 FTE, Contract limits budget to 45 FTE.
                            </span>
                          </div>
                          <span className="text-rose-600 bg-rose-50 px-2 py-0.5 rounded font-bold border border-rose-100">
                            FAIL
                          </span>
                        </div>

                        <div className="flex items-center gap-3 p-2.5 rounded-xl border border-neutral-200 bg-white dark:border-neutral-850 dark:bg-neutral-900/50 text-[10px] text-neutral-700 dark:text-neutral-300">
                          <AlertCircle className="h-4 w-4 text-amber-500 shrink-0" />
                          <div className="flex-1">
                            <span className="font-bold">Kickoff Alignment</span>
                            <span className="text-neutral-400 block mt-0.5">
                              Kickoff set for Oct 10, billing support restricted to Nov 1.
                            </span>
                          </div>
                          <span className="text-amber-600 bg-amber-50 px-2 py-0.5 rounded font-bold border border-amber-100">
                            WARN
                          </span>
                        </div>

                        <div className="flex items-center gap-3 p-2.5 rounded-xl border border-neutral-200 bg-white dark:border-neutral-850 dark:bg-neutral-900/50 text-[10px] text-neutral-700 dark:text-neutral-300">
                          <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                          <div className="flex-1">
                            <span className="font-bold">Signature Blocks Complete</span>
                            <span className="text-neutral-400 block mt-0.5">
                              All customer and vendor execution lines contain active tags.
                            </span>
                          </div>
                          <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded font-bold border border-emerald-100">
                            PASS
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
