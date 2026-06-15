"use client";

import * as React from "react";
import { 
  FileText, 
  Brain, 
  Database,
  AlertCircle,
  Plus,
  Loader2,
  Trash2,
  BookOpen,
  Sun,
  Moon,
  Settings,
  Search,
  ChevronRight,
  Activity,
  ArrowUpRight,
  GitBranch,
  Info,
  Maximize2,
  Sparkles,
  ChevronDown,
  Users,
  Network,
  HeartPulse,
  Tag,
  BarChart2,
  CheckCircle2,
  Cpu,
  Shield,
  BookMarked,
  ListChecks,
  XCircle,
  HelpCircle,
  Link,
  ClipboardList,
  Zap,
  Menu,
  X,
  PanelLeftClose,
  PanelLeftOpen,
  Lock
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import logoImg from "../../public/logo.png";

import { 
  Button, 
  Card, 
  CardContent, 
  Dropzone, 
  Input,
  Badge,
  Tooltip,
  CommandPalette,
  CommandItem,
  Dropdown,
  DropdownTrigger,
  DropdownContent,
  DropdownItem,
  DropdownSeparator,
  cn,
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter
} from "@documind/ui";
import { useChatStore } from "../store/useChatStore";
import { Message, DocumentAnalysis, HealthStatus, RetrievalDiagnostics, TrustScore, ExecutiveSummary, ReviewCopilot, AmbiguityFinding, ReferenceItem, RequirementItem } from "@documind/types";

// We use the singleton sdk from useAuthStore to ensure tokens are attached
import { sdk, useAuthStore } from "../store/useAuthStore";
import { useWorkspaceStore } from "../store/useWorkspaceStore";
import { useRouter } from "next/navigation";

interface SystemLog {
  id: string;
  time: string;
  level: "INFO" | "SUCCESS" | "WARN" | "ERROR" | "VECTOR" | "QUERY";
  message: string;
}

// Custom SVG Network Connections Graph Component
function EntityRelationshipGraph({ entities }: { entities: any[] }) {
  const topEntities = React.useMemo(() => {
    return [...entities]
      .sort((a, b) => (b.frequency || 1) - (a.frequency || 1))
      .slice(0, 12);
  }, [entities]);

  const width = 800;
  const height = 300;
  const cx = width / 2;
  const cy = height / 2;
  const radius = 100;

  const nodes = React.useMemo(() => {
    return topEntities.map((ent, idx) => {
      const angle = (idx * 2 * Math.PI) / topEntities.length;
      // Seeded deterministic jitter — avoids re-render flicker from Math.random()
      const seed = ent.text.charCodeAt(0) * 31 + (ent.text.charCodeAt(1) || 0);
      const jitterX = ((seed % 20) - 10);
      const jitterY = (((seed * 7) % 20) - 10);
      return {
        ...ent,
        x: cx + radius * Math.cos(angle) + jitterX,
        y: cy + radius * Math.sin(angle) + jitterY,
      };
    });
  }, [topEntities, cx, cy, radius]);

  const edges = React.useMemo(() => {
    const list: { source: any; target: any }[] = [];
    const nodeNames = nodes.map(n => n.text.toLowerCase().trim());
    
    nodes.forEach((sourceNode) => {
      if (sourceNode.related_entities) {
        sourceNode.related_entities.forEach((targetName: string) => {
          const targetIndex = nodeNames.indexOf(targetName.toLowerCase().trim());
          if (targetIndex !== -1 && targetIndex > nodes.indexOf(sourceNode)) {
            list.push({
              source: sourceNode,
              target: nodes[targetIndex],
            });
          }
        });
      }
    });
    return list;
  }, [nodes]);

  const getTypeColor = (type: string) => {
    switch (type.toUpperCase()) {
      case "PERSON": return "#ec4899";
      case "ORGANIZATION": return "#6366f1";
      case "LOCATION": return "#14b8a6";
      case "DATE": return "#eab308";
      case "MONEY": return "#22c55e";
      case "PRODUCT": return "#3b82f6";
      case "REQUIREMENT_ID": return "#f97316";
      case "SECTION_REF": return "#a855f7";
      default: return "#6b7280";
    }
  };

  const [hoveredNode, setHoveredNode] = React.useState<string | null>(null);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full select-none">
      <g>
        {edges.map((edge, idx) => {
          const isHighlight = hoveredNode === edge.source.text || hoveredNode === edge.target.text;
          return (
            <line
              key={idx}
              x1={edge.source.x}
              y1={edge.source.y}
              x2={edge.target.x}
              y2={edge.target.y}
              stroke={isHighlight ? "var(--primary, #6366f1)" : "#cbd5e1"}
              strokeWidth={isHighlight ? 2 : 1}
              strokeDasharray={isHighlight ? "none" : "3,3"}
              opacity={hoveredNode && !isHighlight ? 0.2 : 0.6}
              className="transition-all duration-300"
            />
          );
        })}
      </g>
      <g>
        {nodes.map((node, idx) => {
          const size = 8 + Math.min(12, (node.frequency || 1) * 2);
          const isHovered = hoveredNode === node.text;
          const isDimmed = hoveredNode && !isHovered && !node.related_entities?.includes(hoveredNode);
          
          return (
            <g
              key={idx}
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
                  stroke={getTypeColor(node.type)}
                  strokeWidth={1.5}
                  className="animate-pulse"
                />
              )}
              <circle
                cx={node.x}
                cy={node.y}
                r={size}
                fill={getTypeColor(node.type)}
                opacity={0.85}
                stroke="#ffffff"
                strokeWidth={1.5}
              />
              <text
                x={node.x}
                y={node.y + size + 12}
                textAnchor="middle"
                fontSize={isHovered ? "9px" : "8px"}
                fontWeight={isHovered ? "bold" : "medium"}
                className="fill-foreground font-sans pointer-events-none select-none text-[8px] leading-none"
              >
                {node.text}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: isAuthLoading, initialize: initAuth } = useAuthStore();
  const { workspaces, activeWorkspaceId, fetchWorkspaces, setActiveWorkspace, createWorkspace } = useWorkspaceStore();

  // Keep logs in state to avoid breaking dependencies, but hidden from the main editorial UI
  const [systemLogs, setSystemLogs] = React.useState<SystemLog[]>([
    { id: "log-1", time: "19:41:19", level: "INFO", message: "SYSTEM: DocuMind Kernel booting..." },
    { id: "log-2", time: "19:41:19", level: "SUCCESS", message: "CLUSTER: Vector shard online." },
  ]);

  const addLog = React.useCallback((level: SystemLog["level"], message: string) => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    setSystemLogs((prev) => [
      ...prev,
      { id: `log-${Date.now()}-${Math.random()}`, time: timeStr, level, message }
    ]);
  }, []);

  React.useEffect(() => {
    initAuth();
  }, [initAuth]);

  React.useEffect(() => {
    if (user) {
      fetchWorkspaces();
    }
  }, [user, fetchWorkspaces]);

  const {
    documents,
    selectedDocumentIds,
    activeSession,
    sessions,
    isStreaming,
    setDocuments,
    toggleDocumentSelection,
    setSelectedDocumentIds,
    setActiveSession,
    setSessions,
    setIsStreaming,
    addMessageToActiveSession,
    updateLastMessageContent
  } = useChatStore();

  const [chatInput, setChatInput] = React.useState("");
  const [isUploading, setIsUploading] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);
  const [activeModel, setActiveModel] = React.useState<"documind-v3" | "deepseek-r1" | "claude-35">("documind-v3");
  const [expandedThoughtId, setExpandedThoughtId] = React.useState<string | null>(null);

  // Sidebar responsive toggle states
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = React.useState(false);

  // Copy success animation states
  const [copiedPackage, setCopiedPackage] = React.useState(false);
  const [copiedInst, setCopiedInst] = React.useState(false);

  // Trust score count-up animated state
  const [animatedScore, setAnimatedScore] = React.useState(0);

  // Workspace management modal states
  const [isWorkspaceModalOpen, setIsWorkspaceModalOpen] = React.useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = React.useState("");
  const [newWorkspaceDesc, setNewWorkspaceDesc] = React.useState("");
  const [isDeletingWorkspaceId, setIsDeletingWorkspaceId] = React.useState<string | null>(null);
  const [isWorkspaceSubmitting, setIsWorkspaceSubmitting] = React.useState(false);

  // Tab-based workspace modal
  const [wsModalTab, setWsModalTab] = React.useState<"workspaces" | "orgs" | "members" | "audit">("workspaces");
  
  // Organization states
  const [organizations, setOrganizations] = React.useState<any[]>([]);
  const [selectedOrgId, setSelectedOrgId] = React.useState<string>("");
  const [isOrgSubmitting, setIsOrgSubmitting] = React.useState(false);
  const [newOrgName, setNewOrgName] = React.useState("");
  
  // Member invite states
  const [inviteUserId, setInviteUserId] = React.useState("");
  const [inviteRole, setInviteRole] = React.useState("member");
  const [orgMembers, setOrgMembers] = React.useState<any[]>([]);
  
  // Workspace audit states
  const [workspaceAuditLogs, setWorkspaceAuditLogs] = React.useState<any[]>([]);
  const [auditSelectedWorkspaceId, setAuditSelectedWorkspaceId] = React.useState<string>("");
  
  // Rate limit warning banner state
  const [rateLimitWarning, setRateLimitWarning] = React.useState<string | null>(null);

  const handleRateLimitError = React.useCallback((err: any) => {
    const message = err.message || String(err);
    if (message.includes("429") || message.toLowerCase().includes("too many requests") || message.toLowerCase().includes("rate limit exceeded")) {
      setRateLimitWarning("⚠️ Rate Limit Exceeded. You have made too many requests. Please wait a moment.");
      addLog("ERROR", "Rate limit exceeded (HTTP 429).");
      setTimeout(() => {
        setRateLimitWarning(null);
      }, 6000);
      return true;
    }
    return false;
  }, [addLog]);

  const handleOpenWorkspaceModal = async () => {
    setIsWorkspaceModalOpen(true);
    setWsModalTab("workspaces");
    try {
      const orgs = await sdk.listOrganizations();
      setOrganizations(orgs);
      if (orgs.length > 0) {
        setSelectedOrgId(orgs[0].id);
        const members = await sdk.listOrganizationMembers(orgs[0].id);
        setOrgMembers(members);
      }
    } catch (err: any) {
      console.warn("Failed to load organizations", err);
      handleRateLimitError(err);
    }
    
    if (activeWorkspaceId) {
      setAuditSelectedWorkspaceId(activeWorkspaceId);
      try {
        const logs = await sdk.getWorkspaceAuditLogs(activeWorkspaceId);
        setWorkspaceAuditLogs(logs);
      } catch (err: any) {
        console.warn("Failed to load active workspace audit logs", err);
        handleRateLimitError(err);
      }
    }
  };

  const handleOrgChange = async (orgId: string) => {
    setSelectedOrgId(orgId);
    try {
      const members = await sdk.listOrganizationMembers(orgId);
      setOrgMembers(members);
    } catch (err: any) {
      console.warn("Failed to load organization members", err);
      handleRateLimitError(err);
    }
  };

  const handleAuditWorkspaceChange = async (wsId: string) => {
    setAuditSelectedWorkspaceId(wsId);
    try {
      const logs = await sdk.getWorkspaceAuditLogs(wsId);
      setWorkspaceAuditLogs(logs);
    } catch (err: any) {
      console.warn("Failed to load workspace audit logs", err);
      handleRateLimitError(err);
    }
  };

  // Validation suite (Test Lab) states
  const [validationReport, setValidationReport] = React.useState<any>(null);
  const [isRunningSuite, setIsRunningSuite] = React.useState(false);
  const [suiteLogs, setSuiteLogs] = React.useState<string[]>([]);

  const handleCopy = async (text: string, type: "package" | "inst") => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === "package") {
        setCopiedPackage(true);
        setTimeout(() => setCopiedPackage(false), 2000);
        addLog("INFO", "Copied npm package name to clipboard");
      } else {
        setCopiedInst(true);
        setTimeout(() => setCopiedInst(false), 2000);
        addLog("INFO", "Copied SDK instantiation script to clipboard");
      }
    } catch (err) {
      console.warn("Failed to copy to clipboard", err);
    }
  };

  const renderSidebarContent = () => (
    <div className="flex flex-col h-full bg-sidebar-background overflow-hidden">
      {/* Header Workspace Picker */}
      <div className="p-4 border-b border-sidebar-border flex items-center justify-between shrink-0">
        <Dropdown>
          <DropdownTrigger>
            <button className="flex items-center gap-2.5 p-1 rounded-lg hover:bg-secondary/60 text-left transition-all duration-200 focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:outline-none">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg overflow-hidden shadow-sm shadow-primary/10 border border-border/50 bg-background">
                <Image src={logoImg} alt="DocuMind AI Logo" className="h-full w-full object-cover" priority />
              </div>
              <div className="flex items-center gap-1">
                <div>
                  <h1 className="text-sm font-semibold text-foreground leading-tight flex items-center gap-1.5 font-sans">
                    DocuMind AI
                  </h1>
                  <span className="text-[10px] text-muted-foreground font-medium leading-none">
                    {workspaces.find(w => w.id === activeWorkspaceId)?.name || "Select Workspace"}
                  </span>
                </div>
                <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-1" />
              </div>
            </button>
          </DropdownTrigger>
          <DropdownContent align="left" className="w-56 bg-card border-card-border text-foreground shadow-lg rounded-xl p-1.5 z-50">
            <div className="px-2.5 py-2 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
              Workspaces
            </div>
            {workspaces.map(ws => (
              <DropdownItem 
                key={ws.id} 
                icon={<GitBranch className={cn("h-4 w-4", ws.id === activeWorkspaceId ? "text-primary" : "text-muted-foreground")} />}
                onClick={() => setActiveWorkspace(ws.id)}
              >
                {ws.name}
              </DropdownItem>
            ))}
            <DropdownSeparator className="border-border" />
            <DropdownItem 
              icon={<Plus className="h-4 w-4 text-emerald-500" />}
              onClick={() => {
                setNewWorkspaceName("");
                setNewWorkspaceDesc("");
                setIsDeletingWorkspaceId(null);
                handleOpenWorkspaceModal();
              }}
            >
              Create workspace
            </DropdownItem>
            <DropdownSeparator className="border-border" />
            <DropdownItem 
              icon={<Settings className="h-4 w-4 text-muted-foreground" />}
              onClick={() => {
                useAuthStore.getState().logout();
                router.push("/auth/login");
              }}
            >
              Sign out ({user?.name})
            </DropdownItem>
          </DropdownContent>
        </Dropdown>

        {/* Responsive Header Button (Close on mobile, Badge on desktop) */}
        <div className="md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMobileSidebarOpen(false)}
            className="h-8 w-8 rounded-xl border border-border"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="hidden md:block">
          <Badge variant="outline" className="border-primary/25 text-primary bg-primary/5 text-[9px] font-medium leading-none py-1 px-2 rounded-full">
            v1.0
          </Badge>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        
        {/* Model routing desk */}
        <div className="space-y-2">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
            Routing Model
          </span>
          <div className="relative grid grid-cols-3 gap-1 bg-secondary/40 p-1 rounded-xl border border-border z-0">
            {(["documind-v3", "deepseek-r1", "claude-35"] as const).map((m) => {
              const isActive = activeModel === m;
              return (
                <button
                  key={m}
                  onClick={() => setActiveModel(m)}
                  className={cn(
                    "relative py-1.5 text-xs font-semibold font-sans transition-all text-center rounded-lg select-none z-10",
                    isActive ? "text-foreground font-bold animate-fade-in" : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {isActive && (
                    <motion.span
                      layoutId="activeModelPill"
                      className="absolute inset-0 bg-card border border-card-border shadow-xs rounded-lg -z-10"
                      transition={{ type: "spring", stiffness: 350, damping: 28 }}
                    />
                  )}
                  {m === "documind-v3" ? "RAG v3" : m === "deepseek-r1" ? "R1" : "Claude"}
                </button>
              );
            })}
          </div>
        </div>

        {/* Upload Zone */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
              Source Ingestion
            </span>
            <Dropdown>
              <DropdownTrigger>
                <button className="text-[10px] text-primary hover:text-primary/80 font-semibold hover:underline flex items-center gap-1 focus-visible:outline-none">
                  <Plus className="h-3 w-3" /> Test Lab
                </button>
              </DropdownTrigger>
              <DropdownContent align="right" className="w-72">
                <DropdownItem onClick={() => handleGenerateTestDataset("easy")}>
                  Sales Headcount Contract (Easy - 10p)
                </DropdownItem>
                <DropdownItem onClick={() => handleGenerateTestDataset("medium")}>
                  Alpha Project Charter (Medium - 30p)
                </DropdownItem>
                <DropdownItem onClick={() => handleGenerateTestDataset("hard")}>
                  Beta Project Spec (Hard - 50p)
                </DropdownItem>
                <DropdownItem onClick={() => handleGenerateTestDataset("nightmare")}>
                  Nexus Tech Spec (Nightmare - 100p+)
                </DropdownItem>
              </DropdownContent>
            </Dropdown>
          </div>
          <div className="relative group">
            <Dropzone 
              onFileSelect={handleFileSelect} 
              disabled={isUploading}
              className={cn(
                "text-xs bg-card/60 hover:bg-card border-card-border hover:border-primary/30 transition-all duration-300 py-7 text-center rounded-2xl border border-dashed relative overflow-hidden shadow-xs cursor-pointer",
                isUploading ? "pointer-events-none opacity-50" : ""
              )}
            />
          </div>
          {isUploading && (
            <div className="mt-2 flex items-center justify-center gap-2 text-xs text-primary font-medium animate-pulse">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              <span>Indexing source file...</span>
            </div>
          )}
        </div>

        {/* Document list */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
              Knowledge base
            </span>
            {selectedDocumentIds.length > 0 && (
              <button 
                onClick={() => setSelectedDocumentIds([])}
                className="text-[10px] text-primary hover:text-primary/80 font-semibold hover:underline"
              >
                Clear Focus
              </button>
            )}
          </div>

          <div className="space-y-1.5">
            {documents.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border p-6 text-center text-xs text-muted-foreground bg-card/40">
                No documents indexed
              </div>
            ) : (
              documents.map((doc) => {
                const isSelected = selectedDocumentIds.includes(doc.id);
                return (
                  <motion.div
                    key={doc.id}
                    onClick={() => handleToggleDoc(doc.id)}
                    whileTap={{ scale: 0.99 }}
                    className={cn(
                      "group flex items-center justify-between rounded-xl border p-2.5 cursor-pointer transition-all duration-200 shadow-2xs",
                      isSelected
                        ? "bg-primary/5 border-primary/30 text-foreground font-bold"
                        : "bg-card hover:bg-card/90 border-card-border hover:border-border text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <div className="flex items-center gap-2.5 overflow-hidden w-full">
                      <div className={cn(
                        "flex h-7 w-7 items-center justify-center rounded-lg text-xs transition-colors",
                        isSelected ? "bg-primary/10 text-primary" : "bg-secondary text-muted-foreground"
                      )}>
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="overflow-hidden w-full">
                        <div className="flex items-center gap-1.5 justify-between">
                          <p className="text-[11px] font-semibold truncate leading-none text-foreground">
                            {doc.name.replace(/\.[^/.]+$/, "")}
                          </p>
                          <Badge
                            variant={
                              doc.status === "COMPLETED" || doc.status === "processed"
                                ? "success"
                                : doc.status === "FAILED" || doc.status === "failed"
                                ? "error"
                                : "warning"
                            }
                            className={cn("text-[8px] font-medium leading-none tracking-tight scale-90 px-1.5 py-0.5 border-0 uppercase rounded-full", {
                              "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400": doc.status === "COMPLETED" || doc.status === "processed",
                              "bg-amber-500/10 text-amber-600 dark:text-amber-400 animate-pulse": doc.status !== "COMPLETED" && doc.status !== "processed" && doc.status !== "FAILED" && doc.status !== "failed",
                            })}
                          >
                            {doc.status === "COMPLETED" || doc.status === "processed" ? "Ready" : doc.status}
                          </Badge>
                        </div>
                        {/* Phase 3.4 Ingestion Pipeline Tracking */}
                        {(doc.status !== "COMPLETED" && doc.status !== "processed" && doc.status !== "FAILED" && doc.status !== "failed") && (
                          <div className="mt-2 w-full bg-secondary/50 rounded-full h-1.5 mb-1 overflow-hidden">
                            <div 
                              className="bg-primary h-1.5 rounded-full transition-all duration-500 ease-out" 
                              style={{ width: `${doc.progress_percentage || 0}%` }} 
                            />
                          </div>
                        )}
                        <div className="flex items-center gap-2 mt-1 text-[9px] text-muted-foreground">
                          <span>{(doc.metadata.fileSize / 1024).toFixed(0)} KB</span>
                          <span>•</span>
                          <span>{Math.max(4, Math.floor(doc.metadata.fileSize / 8000))} chunks</span>
                        </div>
                      </div>
                    </div>

                    <Tooltip content="Remove source">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteDoc(doc.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 h-6 w-6 flex items-center justify-center rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all duration-200"
                        aria-label={`Delete ${doc.name}`}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </Tooltip>
                  </motion.div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Action trigger footer */}
      <div className="p-4 border-t border-sidebar-border bg-sidebar-background shrink-0">
        <Button 
          className={cn(
            "w-full text-xs font-semibold py-5 rounded-xl transition-all duration-300 bg-secondary hover:bg-secondary-hover border border-border text-foreground shadow-2xs hover:shadow-xs",
            selectedDocumentIds.length > 0
              ? "bg-primary hover:bg-primary/95 text-primary-foreground border-transparent shadow-md shadow-primary/10"
              : "opacity-60 pointer-events-none"
          )} 
          onClick={handleStartSession}
          disabled={selectedDocumentIds.length === 0}
        >
          <Sparkles className="h-3.5 w-3.5 mr-2" />
          Compile Index ({selectedDocumentIds.length})
        </Button>
      </div>
    </div>
  );

  // Contradiction Intelligence States
  const [activeTab, setActiveTab] = React.useState<"chat" | "contradictions" | "entities" | "intelligence" | "retrieval" | "diagnostics" | "testlab">("chat");
  const [selectedContradictionDocId, setSelectedContradictionDocId] = React.useState<string | null>(null);
  const [contradictionInsights, setContradictionInsights] = React.useState<any[]>([]);
  const [isAnalyzingContradictions, setIsAnalyzingContradictions] = React.useState(false);
  const [contradictionStatus, setContradictionStatus] = React.useState("");
  const [contradictionTelemetry, setContradictionTelemetry] = React.useState<any | null>(null);
  const [expandedContradictionId, setExpandedContradictionId] = React.useState<string | null>(null);
  const [expandedReasoningMap, setExpandedReasoningMap] = React.useState<Record<string, Record<string, boolean>>>({}); 

  // Document Intelligence States
  const [intelligenceDocId, setIntelligenceDocId] = React.useState<string | null>(null);
  const [isLoadingIntelligence, setIsLoadingIntelligence] = React.useState(false);
  const [trustScore, setTrustScore] = React.useState<TrustScore | null>(null);

  React.useEffect(() => {
    let timer: NodeJS.Timeout | undefined;
    if (trustScore && typeof trustScore.score === "number") {
      const targetScore = trustScore.score;
      setAnimatedScore(0);
      const duration = 800; // 0.8s
      const steps = 40;
      const stepTime = duration / steps;
      let step = 0;
      timer = setInterval(() => {
        step++;
        setAnimatedScore(Math.min(targetScore, Math.round((targetScore / steps) * step)));
        if (step >= steps) {
          if (timer) clearInterval(timer);
        }
      }, stepTime);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [trustScore]);

  const [executiveSummary, setExecutiveSummary] = React.useState<ExecutiveSummary | null>(null);
  const [reviewCopilot, setReviewCopilot] = React.useState<ReviewCopilot | null>(null);
  const [ambiguities, setAmbiguities] = React.useState<AmbiguityFinding[]>([]);
  const [references, setReferences] = React.useState<ReferenceItem[]>([]);
  const [requirements, setRequirements] = React.useState<RequirementItem[]>([]);


  const [intelligenceSubTab, setIntelligenceSubTab] = React.useState<"overview" | "review" | "ambiguities" | "references" | "requirements">("overview");

  // Entity Intelligence States
  const [entityAnalysis, setEntityAnalysis] = React.useState<DocumentAnalysis | null>(null);
  const [isLoadingEntities, setIsLoadingEntities] = React.useState(false);
  const [entityDocId, setEntityDocId] = React.useState<string | null>(null);

  // Retrieval Diagnostics States (keyed by message ID)
  const [retrievalDiagnosticsMap, setRetrievalDiagnosticsMap] = React.useState<Record<string, RetrievalDiagnostics>>({});
  const [selectedDiagMsgId, setSelectedDiagMsgId] = React.useState<string | null>(null);

  // System Diagnostics State
  const [healthStatus, setHealthStatus] = React.useState<HealthStatus | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = React.useState(false);

  const toggleReasoningPanel = (insightId: string, panelKey: string) => {
    setExpandedReasoningMap((prev) => {
      const current = prev[insightId] || {};
      return {
        ...prev,
        [insightId]: {
          ...current,
          [panelKey]: !current[panelKey],
        },
      };
    });
  };

  const runContradictionScan = async (docId: string) => {
    setIsAnalyzingContradictions(true);
    setContradictionStatus("Initializing contradiction engine...");
    setContradictionInsights([]);
    setContradictionTelemetry(null);
    setExpandedContradictionId(null);
    setExpandedReasoningMap({});
    addLog("INFO", `Starting contradiction scan for document: ${docId}`);

    try {
      const generator = sdk.streamContradictions(docId, activeModel);
      for await (const chunk of generator) {
        if (chunk.type === "status") {
          setContradictionStatus(chunk.message);
          addLog("INFO", `Scan status: ${chunk.message}`);
        } else if (chunk.type === "insight") {
          setContradictionInsights((prev) => [...prev, chunk.insight]);
          addLog("WARN", `Contradiction detected: ${chunk.insight.summary}`);
        } else if (chunk.type === "telemetry") {
          setContradictionTelemetry(chunk.metrics);
          addLog("SUCCESS", `Contradiction scan completed. Found ${chunk.metrics.contradictionCount} conflict(s).`);
        } else if (chunk.type === "error") {
          throw new Error(chunk.message);
        }
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to analyze contradictions.");
      addLog("ERROR", `Contradiction scan failed: ${err.message}`);
    } finally {
      setIsAnalyzingContradictions(false);
      setContradictionStatus("");
    }
  };

  React.useEffect(() => {
    setActiveTab("chat");
    if (activeSession && activeSession.documentIds.length > 0) {
      setSelectedContradictionDocId(activeSession.documentIds[0]);
      setEntityDocId(activeSession.documentIds[0]);
      setIntelligenceDocId(activeSession.documentIds[0]);
    } else {
      setSelectedContradictionDocId(null);
      setEntityDocId(null);
      setIntelligenceDocId(null);
    }
    setContradictionInsights([]);
    setContradictionTelemetry(null);
    setExpandedContradictionId(null);
    setExpandedReasoningMap({});
    setEntityAnalysis(null);
    setRetrievalDiagnosticsMap({});
    setSelectedDiagMsgId(null);
    setHealthStatus(null);
    // Reset intelligence
    setTrustScore(null);
    setExecutiveSummary(null);
    setReviewCopilot(null);
    setAmbiguities([]);
    setReferences([]);
    setRequirements([]);
    setIntelligenceSubTab("overview");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSession?.id]);

  const scrollRef = React.useRef<HTMLDivElement>(null);

  // Theme support
  const [theme, setTheme] = React.useState<"light" | "dark">("light");

  const [isConsoleOpen, setIsConsoleOpen] = React.useState(false);

  React.useEffect(() => {
    if (systemLogs.length > 0) {
      console.debug("Log entry generated:", systemLogs[systemLogs.length - 1]);
    }
  }, [systemLogs]);
  React.useEffect(() => {
    if (isConsoleOpen && systemLogs.length > 0) {
      const el = document.getElementById("console-bottom");
      el?.scrollIntoView({ behavior: "smooth" });
    }
  }, [systemLogs, isConsoleOpen]);



  React.useEffect(() => {
    // Default to light mode for the premium alabaster look
    if (localStorage.theme === "dark") {
      document.documentElement.classList.add("dark");
      setTheme("dark");
    } else {
      document.documentElement.classList.remove("dark");
      setTheme("light");
    }
  }, []);

  const toggleTheme = React.useCallback(() => {
    if (theme === "light") {
      document.documentElement.classList.add("dark");
      localStorage.theme = "dark";
      setTheme("dark");
      addLog("INFO", "Switched environment theme to Dark.");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.theme = "light";
      setTheme("light");
      addLog("INFO", "Switched environment theme to Light.");
    }
  }, [theme, addLog]);

  // Command palette state
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = React.useState(false);

  // Global shortcut triggers
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMod = e.metaKey || e.ctrlKey;
      if (isMod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      } else if (isMod && e.shiftKey && e.key.toLowerCase() === "t") {
        e.preventDefault();
        toggleTheme();
      } else if (isMod && e.key.toLowerCase() === "u") {
        e.preventDefault();
        const inputEl = document.querySelector('input[type="file"]') as HTMLInputElement;
        inputEl?.click();
      } else if (isMod && e.key.toLowerCase() === "q" && activeSession) {
        e.preventDefault();
        setActiveSession(null);
      } else if (isMod && e.key.toLowerCase() === "d" && selectedDocumentIds.length > 0) {
        setSelectedDocumentIds([]);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [theme, activeSession, selectedDocumentIds, setSelectedDocumentIds, setActiveSession, toggleTheme, addLog]);

  // Load initial documents
  React.useEffect(() => {
    async function fetchDocs() {
      try {
        const docs = await sdk.listDocuments();
        setDocuments(docs);
      } catch (err) {
        console.warn("Failed to connect to backend", err);
        setDocuments([]);
      }
    }
    fetchDocs();
  }, [setDocuments]);

  // Scroll chat window to bottom
  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activeSession?.messages, isStreaming]);

  // Handle file drops / uploads
  const handleFileSelect = async (files: File[]) => {
    setIsUploading(true);
    setErrorMsg(null);
    try {
      for (const file of files) {
        addLog("INFO", `Ingesting file: ${file.name}`);
        const doc = await sdk.uploadDocument(file);
        setDocuments([...documents, doc]);
      }
    } catch (e: any) {
      setErrorMsg(e.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  };

  // Delete a document
  const handleDeleteDoc = async (id: string) => {
    const docToDelete = documents.find(d => d.id === id);
    try {
      await sdk.deleteDocument(id);
      setDocuments(documents.filter((d) => d.id !== id));
      setSelectedDocumentIds(selectedDocumentIds.filter((dId) => dId !== id));
      addLog("INFO", `Removed source document: ${docToDelete?.name || id}`);
    } catch {
      setDocuments(documents.filter((d) => d.id !== id));
      setSelectedDocumentIds(selectedDocumentIds.filter((dId) => dId !== id));
      addLog("INFO", `Removed source document: ${docToDelete?.name || id}`);
    }
  };

  // Toggle document focus selection
  const handleToggleDoc = (docId: string) => {
    toggleDocumentSelection(docId);
  };

  // Start RAG Chat Session
  const handleStartSession = async () => {
    if (selectedDocumentIds.length === 0) {
      setErrorMsg("Please select at least one document to analyze.");
      return;
    }
    setErrorMsg(null);

    const title = `${selectedDocumentIds.length} focused source(s)`;

    try {
      const sess = await sdk.createSession({ title, documentIds: selectedDocumentIds });
      setActiveSession(sess);
      setSessions([sess, ...sessions]);
      addLog("SUCCESS", `Session created: ${sess.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create session.";
      if (!handleRateLimitError(err)) {
        setErrorMsg(`Cannot start session: ${msg} — ensure the backend is running on port 8000.`);
        addLog("ERROR", `Session creation failed: ${msg}`);
      }
    }
  };

  const handleGenerateTestDataset = async (level: "easy" | "medium" | "hard" | "nightmare") => {
    setIsUploading(true);
    setErrorMsg(null);
    try {
      const generated = await sdk.generateTestDataset(level, activeWorkspaceId || undefined);
      setDocuments(prev => [...generated, ...prev]);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to generate test dataset.");
    } finally {
      setIsUploading(false);
    }
  };

  // Send message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !activeSession || isStreaming) return;

    const userMessageContent = chatInput.trim();
    setChatInput("");
    setIsStreaming(true);
    setErrorMsg(null);

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: userMessageContent,
      createdAt: new Date().toISOString()
    };

    addMessageToActiveSession(userMsg);

    const assistantMsgId = `msg-assistant-${Date.now()}`;
    const initialAssistantMsg: Message = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString()
    };
    addMessageToActiveSession(initialAssistantMsg);

    let streamSuccess = false;
    try {
      const generator = sdk.streamMessage({
        sessionId: activeSession.id,
        content: userMessageContent,
        documentIds: activeSession.documentIds,
        model: activeModel
      });

      for await (const chunk of generator) {
        if (chunk.type === "token" && chunk.content) {
          updateLastMessageContent(chunk.content);
        } else if (!chunk.type && chunk.content) {
          updateLastMessageContent(chunk.content);
        } else if (chunk.type === "retrieval_diagnostics") {
          setRetrievalDiagnosticsMap((prev) => ({
            ...prev,
            [assistantMsgId]: chunk,
          }));
          setSelectedDiagMsgId(assistantMsgId);
        }
      }

      addLog("SUCCESS", "RAG reasoning complete. Dynamic source attributions compiled.");
      streamSuccess = true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Streaming failed. Check that the backend is running.";
      console.error("Streaming error:", err);
      if (handleRateLimitError(err)) {
        setErrorMsg("Rate limit exceeded. Please wait a moment before sending another message.");
        updateLastMessageContent("⚠️ Rate limit exceeded. Please wait before retrying.");
      } else {
        setErrorMsg(msg);
        addLog("ERROR", `Stream failure: ${msg}`);
        updateLastMessageContent(`⚠️ ${msg}`);
      }
    } finally {
      setIsStreaming(false);
    }

    if (streamSuccess) {
      try {
        const updatedSession = await sdk.getSession(activeSession.id);
        setActiveSession(updatedSession);
        setSessions(sessions.map(s => s.id === updatedSession.id ? updatedSession : s));
      } catch (err) {
        console.warn("Failed to reload session after streaming:", err);
      }
    }
  };

  // Preset pill click handler
  const handlePresetTrigger = (promptText: string) => {
    setChatInput(promptText);
  };

  // Compute metrics
  const processedDocsCount = documents.filter(d => d.status === "processed").length;
  const totalSize = documents.reduce((acc, curr) => acc + curr.metadata.fileSize, 0);
  const sizeFormatted = (totalSize / (1024 * 1024)).toFixed(2);

  // Command palette configuration
  const commandItems = React.useMemo(() => {
    const list: CommandItem[] = [
      {
        id: "toggle-theme",
        title: "Toggle Theme",
        description: `Switch to ${theme === "light" ? "Dark" : "Light"} mode`,
        category: "System",
        icon: theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />,
        shortcut: ["ctrl", "shift", "t"],
        onSelect: () => toggleTheme(),
      },
      {
        id: "select-documind",
        title: "Use Model: DocuMind v3",
        description: "Switch to core DocuMind vector model",
        category: "Models",
        icon: <Cpu className="h-4 w-4 text-indigo-500" />,
        onSelect: () => setActiveModel("documind-v3")
      },
      {
        id: "select-deepseek",
        title: "Use Model: DeepSeek R1",
        description: "Switch to DeepSeek R1 reasoning chain",
        category: "Models",
        icon: <Sparkles className="h-4 w-4 text-amber-500" />,
        onSelect: () => setActiveModel("deepseek-r1")
      },
      {
        id: "select-claude",
        title: "Use Model: Claude 3.5 Sonnet",
        description: "Switch to Claude 3.5 Sonnet engine",
        category: "Models",
        icon: <Brain className="h-4 w-4 text-emerald-500" />,
        onSelect: () => setActiveModel("claude-35")
      },
      {
        id: "upload-doc",
        title: "Upload Document",
        description: "Import a new workspace document",
        category: "Actions",
        icon: <Plus className="h-4 w-4" />,
        shortcut: ["ctrl", "u"],
        onSelect: () => {
          const inputEl = document.querySelector('input[type="file"]') as HTMLInputElement;
          inputEl?.click();
        },
      },
    ];

    if (activeSession) {
      list.push({
        id: "close-session",
        title: "Unload Workspace Index",
        description: "Close active document session",
        category: "Actions",
        icon: <BookOpen className="h-4 w-4" />,
        shortcut: ["ctrl", "q"],
        onSelect: () => setActiveSession(null),
      });
    }

    return list;
  }, [theme, activeSession, toggleTheme, setActiveSession]);

  // 1. If auth is still checking, show loader
  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // 2. If no user after checking, redirect (the router push handles the redirect, but we return null to avoid flashing UI)
  if (!user) {
    if (typeof window !== "undefined") {
      router.push("/auth/login");
    }
    return null;
  }

  return (
    <div className="flex h-screen bg-background text-foreground font-sans select-none overflow-hidden relative">
      {rateLimitWarning && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 pointer-events-none animate-in fade-in slide-in-from-top-4 duration-300">
          <div className="bg-rose-500/10 backdrop-blur-md border border-rose-500/20 text-rose-700 dark:text-rose-400 text-xs font-semibold px-4.5 py-3 rounded-xl shadow-lg flex items-center gap-2 pointer-events-auto">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{rateLimitWarning}</span>
            <button 
              onClick={() => setRateLimitWarning(null)} 
              className="ml-2 hover:bg-rose-500/10 p-0.5 rounded transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
      
      {/* Premium ambient glows */}
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[140px] pointer-events-none z-0 dark:bg-indigo-500/2" />
      <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-primary/5 rounded-full blur-[100px] pointer-events-none z-0 dark:bg-primary/2" />

      {/* Main shell layer */}
      <div className="flex w-full h-full z-10 relative dot-grid">
        
        {/* Mobile Sidebar overlay drawer */}
        <AnimatePresence>
          {isMobileSidebarOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.4 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsMobileSidebarOpen(false)}
                className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-xs"
              />
              <motion.div
                initial={{ x: "-100%" }}
                animate={{ x: 0 }}
                exit={{ x: "-100%" }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="fixed top-0 bottom-0 left-0 w-[320px] bg-sidebar-background border-r border-border flex flex-col z-50 md:hidden shadow-2xl overflow-hidden"
              >
                {renderSidebarContent()}
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Desktop Collapsible Sidebar */}
        <motion.div
          animate={{ width: isSidebarOpen ? 320 : 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className={cn(
            "hidden md:flex flex-col flex-shrink-0 border-r border-border bg-sidebar-background overflow-hidden relative z-20 shadow-[1px_0_10px_rgba(0,0,0,0.01)] dark:shadow-none h-full"
          )}
        >
          {renderSidebarContent()}
        </motion.div>

        {/* 2. TOP NAVBAR & MAIN WORKSPACE */}
        <main className="flex-1 flex flex-col min-w-0 bg-background/95 relative overflow-hidden z-10">
          
          {/* Top Navbar */}
          <header className="h-14 border-b border-border px-4 md:px-6 flex items-center justify-between flex-shrink-0 bg-background/80 backdrop-blur-md sticky top-0 z-30 shadow-[0_1px_5px_rgba(0,0,0,0.005)] gap-3">
            <div className="flex items-center gap-3">
              {/* Mobile Menu Icon */}
              <button
                onClick={() => setIsMobileSidebarOpen(true)}
                className="md:hidden p-1.5 rounded-xl border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all duration-200 focus-visible:outline-none"
                aria-label="Open menu"
              >
                <Menu className="h-4.5 w-4.5" />
              </button>

              {/* Desktop Toggle Icon */}
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="hidden md:flex p-1.5 rounded-xl border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all duration-200 focus-visible:outline-none"
                aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
              >
                {isSidebarOpen ? <PanelLeftClose className="h-4.5 w-4.5" /> : <PanelLeftOpen className="h-4.5 w-4.5" />}
              </button>

              <div className="hidden sm:flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                <span>Workspace</span>
                <ChevronRight className="h-3 w-3 text-border" />
                <span>General</span>
                <ChevronRight className="h-3 w-3 text-border" />
                <span className="text-foreground font-semibold">Active RAG Session</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Search trigger button (Raycast/Arc style) */}
              <button
                onClick={() => setIsCommandPaletteOpen(true)}
                className="flex items-center justify-between w-48 px-3 py-1.5 text-xs text-muted-foreground bg-secondary/40 border border-border rounded-xl hover:border-border hover:bg-secondary/70 transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20"
              >
                <span className="flex items-center gap-2">
                  <Search className="h-3.5 w-3.5 text-muted-foreground/80" />
                  Search workspace
                </span>
                <kbd className="pointer-events-none select-none rounded border border-border bg-card px-1.5 font-sans text-[9px] font-semibold text-muted-foreground">
                  ⌘K
                </kbd>
              </button>

              {/* Status Badge */}
              <div className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400 shadow-2xs">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Synced
              </div>

              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                className="h-8 w-8 rounded-xl border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground shadow-2xs p-0 transition-all duration-200"
                aria-label="Toggle theme"
              >
                {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              </Button>
            </div>
          </header>

          {/* Content Section */}
          {activeSession ? (
            /* AI CHAT EXPERIENCE */
            <div className="flex-1 flex flex-col min-h-0 relative">
              
              {/* Floating RAG status & Tabs banner */}
              <div className="px-4 md:px-6 py-0 bg-secondary/10 border-b border-border flex items-center justify-between text-xs text-muted-foreground shadow-2xs overflow-x-auto gap-4 scrollbar-thin">
                <div className="flex items-center gap-1 overflow-x-auto py-1.5 z-0">
                  {([
                    { id: "chat", label: "Workspace Chat", icon: null },
                    { id: "contradictions", label: "Contradiction Intelligence", icon: <AlertCircle className="h-3.5 w-3.5 text-amber-500" /> },
                    { id: "entities", label: "Entity Intelligence", icon: <Users className="h-3.5 w-3.5 text-indigo-500" /> },
                    { id: "intelligence", label: "Document Intelligence", icon: <Shield className="h-3.5 w-3.5 text-violet-500" /> },
                    { id: "retrieval", label: "Retrieval Inspector", icon: <Network className="h-3.5 w-3.5 text-emerald-500" /> },
                    { id: "diagnostics", label: "Diagnostics", icon: <HeartPulse className="h-3.5 w-3.5 text-rose-500" /> },
                    { id: "testlab", label: "Test Lab", icon: <Cpu className="h-3.5 w-3.5 text-violet-500" /> },
                  ] as const).map(({ id, label, icon }) => {
                    const isActive = activeTab === id;
                    return (
                      <button
                        key={id}
                        onClick={() => setActiveTab(id)}
                        className={cn(
                          "relative px-4 py-2 text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 whitespace-nowrap rounded-lg select-none",
                          isActive
                            ? "text-foreground font-bold"
                            : "text-muted-foreground hover:text-foreground"
                        )}
                      >
                        {isActive && (
                          <motion.span
                            layoutId="activeTabGlow"
                            className="absolute inset-0 bg-secondary/60 rounded-lg -z-10"
                            transition={{ type: "spring", stiffness: 380, damping: 30 }}
                          />
                        )}
                        {isActive && (
                          <motion.span
                            layoutId="activeTabUnderline"
                            className="absolute bottom-0 left-2 right-2 h-0.5 bg-primary rounded-full"
                            transition={{ type: "spring", stiffness: 380, damping: 30 }}
                          />
                        )}
                        {icon}
                        <span>{label}</span>
                      </button>
                    );
                  })}
                </div>
                
                <div className="flex items-center gap-3">
                  <span className="hidden md:inline">
                    Sources: {activeSession.documentIds.length} focused file(s)
                  </span>
                  <span className="text-border hidden md:inline">|</span>
                  <span className="capitalize hidden md:inline">
                    Engine: {activeModel === "documind-v3" ? "DocuMind v3" : activeModel === "deepseek-r1" ? "DeepSeek R1" : "Claude 3.5"}
                  </span>
                  <span className="text-border hidden md:inline">|</span>
                  <button 
                    onClick={() => setActiveSession(null)}
                    className="text-xs text-muted-foreground hover:text-destructive transition-colors font-semibold py-1.5 px-2.5 rounded-lg hover:bg-secondary/40"
                  >
                    Close Session
                  </button>
                </div>
              </div>

              {activeTab === "chat" ? (
                <>
                  {/* Chat Messages Stream */}
                  <div 
                    ref={scrollRef}
                    className="flex-1 overflow-y-auto p-6 space-y-8 select-text"
                  >
                    <div className="max-w-3xl mx-auto space-y-8">
                      {activeSession.messages.map((msg) => {
                        const isUser = msg.role === "user";
                        const hasThought = msg.content.includes("<thought>") && msg.content.includes("</thought>");
                        
                        // Extract thought trace for DeepSeek
                        let thoughtTrace = "";
                        let cleanContent = msg.content;
                        if (hasThought) {
                          const startIdx = msg.content.indexOf("<thought>");
                          const endIdx = msg.content.indexOf("</thought>");
                          if (startIdx !== -1 && endIdx !== -1) {
                            thoughtTrace = msg.content.substring(startIdx + 9, endIdx).trim();
                            cleanContent = msg.content.substring(endIdx + 10).trim();
                          }
                        }

                        return (
                          <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ type: "spring", stiffness: 350, damping: 30 }}
                            className={cn("flex flex-col space-y-2.5", {
                              "items-end": isUser,
                              "items-start": !isUser,
                            })}
                          >
                            {/* Avatar / Identity Label */}
                            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground px-1">
                              {isUser ? (
                                <span>You</span>
                              ) : (
                                <span className="flex items-center gap-1.5 text-foreground">
                                  <Sparkles className="h-3.5 w-3.5 text-primary" />
                                  DocuMind AI
                                  <span className="text-[10px] text-muted-foreground font-normal">
                                    ({activeModel === "deepseek-r1" ? "DeepSeek R1" : activeModel === "claude-35" ? "Claude 3.5" : "RAG v3"})
                                  </span>
                                </span>
                              )}
                              <span className="text-[10px] font-normal opacity-60">•</span>
                              <span className="text-[10px] font-normal opacity-60">
                                {new Date(msg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })}
                              </span>
                            </div>

                            {/* Content bubble */}
                            <div
                              className={cn("max-w-2xl px-5 py-4 rounded-2xl shadow-xs transition-all duration-300 leading-relaxed font-sans text-sm", {
                                "bg-primary text-primary-foreground select-text shadow-sm": isUser,
                                "bg-card text-foreground border border-card-border select-text": !isUser,
                              })}
                            >
                              {/* Reasoning Trace Accordion */}
                              {thoughtTrace && (
                                <div className="border border-border rounded-xl bg-secondary/30 mb-3 overflow-hidden shadow-2xs">
                                  <button
                                    onClick={() => setExpandedThoughtId(expandedThoughtId === msg.id ? null : msg.id)}
                                    className="w-full px-3 py-2.5 flex items-center justify-between text-xs text-muted-foreground hover:text-foreground transition-colors font-semibold font-sans"
                                  >
                                    <span className="flex items-center gap-2">
                                      <Info className="h-3.5 w-3.5 text-primary/80" />
                                      Reasoning Trace ({expandedThoughtId === msg.id ? "Expanded" : "Collapsed"})
                                    </span>
                                    <Maximize2 className="h-3.5 w-3.5 opacity-60" />
                                  </button>
                                  <AnimatePresence initial={false}>
                                    {expandedThoughtId === msg.id && (
                                      <motion.div 
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        transition={{ duration: 0.2, ease: "easeInOut" }}
                                        className="overflow-hidden border-t border-border"
                                      >
                                        <div className="px-3 pb-3 pt-2 text-xs text-muted-foreground bg-card/40 whitespace-pre-wrap leading-relaxed font-sans">
                                          {thoughtTrace}
                                        </div>
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </div>
                              )}

                              <div className="prose dark:prose-invert max-w-none text-sm font-sans space-y-2">
                                {msg.content === "" && isStreaming ? (
                                  <div className="flex flex-col gap-1.5 py-1">
                                    <div className="flex items-center gap-1.5 mt-1">
                                      <motion.span
                                        animate={{ y: [0, -5, 0] }}
                                        transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut", delay: 0 }}
                                        className="h-2 w-2 bg-primary rounded-full"
                                      />
                                      <motion.span
                                        animate={{ y: [0, -5, 0] }}
                                        transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut", delay: 0.15 }}
                                        className="h-2 w-2 bg-primary rounded-full"
                                      />
                                      <motion.span
                                        animate={{ y: [0, -5, 0] }}
                                        transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut", delay: 0.3 }}
                                        className="h-2 w-2 bg-primary rounded-full"
                                      />
                                    </div>
                                    <span className="text-xs text-muted-foreground font-medium animate-pulse mt-0.5">Formulating response...</span>
                                  </div>
                                ) : (
                                  cleanContent
                                )}
                              </div>

                              {/* Matching metrics & citation link references */}
                              {!isUser && msg.content !== "" && (
                                <div className="pt-3 mt-3.5 border-t border-border flex flex-col gap-2.5">
                                  {/* Source Citation cards */}
                                  <div className="flex flex-wrap items-center gap-2">
                                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mr-1">Sources:</span>
                                    {msg.citations && msg.citations.length > 0 ? (
                                      msg.citations.map((cit, idx) => (
                                        <Tooltip key={idx} content={cit.snippet}>
                                          <div 
                                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-card-border bg-secondary/50 text-[10px] text-foreground font-medium hover:bg-secondary transition-colors cursor-help"
                                          >
                                            <FileText className="h-3 w-3 text-muted-foreground" />
                                            <span>{cit.documentName.substring(0, 14)}{cit.documentName.length > 14 ? "..." : ""}</span>
                                            <span className="text-muted-foreground opacity-80">(Page {cit.pageNumber})</span>
                                          </div>
                                        </Tooltip>
                                      ))
                                    ) : (
                                      <span className="text-[10px] text-muted-foreground italic">No context references matching query</span>
                                    )}
                                  </div>

                                  <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                                    <span className="flex items-center gap-1">
                                      <Activity className="h-3 w-3 text-primary" />
                                      Context relevance: <span className="text-foreground font-bold">
                                        {msg.citations && msg.citations.length > 0 
                                          ? `${(Math.max(...msg.citations.map(c => c.score || 0)) * 100).toFixed(1)}%` 
                                          : "N/A"}
                                      </span>
                                    </span>
                                    <span className="font-medium text-primary bg-primary/5 px-2 py-0.5 rounded-full scale-90">
                                      Shard hits: {msg.citations ? msg.citations.length : 0} blocks
                                    </span>
                                  </div>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Message Input prompt section */}
                  <div className="p-6 border-t border-border bg-background/80 backdrop-blur-md flex-shrink-0">
                    <div className="max-w-3xl mx-auto space-y-4">
                      
                      {/* Preset Pills */}
                      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mr-1 select-none">
                          Presets:
                        </span>
                        <button 
                          onClick={() => handlePresetTrigger("Provide a concise summary of the active document.")}
                          className="px-3 py-1.5 text-xs font-medium border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 rounded-full transition-all duration-200 shadow-2xs"
                        >
                          Summarize context
                        </button>
                        <button 
                          onClick={() => handlePresetTrigger("Extract key system requirements and entity interactions.")}
                          className="px-3 py-1.5 text-xs font-medium border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 rounded-full transition-all duration-200 shadow-2xs"
                        >
                          Extract core specifications
                        </button>
                        <button 
                          onClick={() => handlePresetTrigger("Verify system configurations and list missing dependencies.")}
                          className="px-3 py-1.5 text-xs font-medium border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 rounded-full transition-all duration-200 shadow-2xs"
                        >
                          Verify checklist
                        </button>
                      </div>

                      {/* Elegant Floating Input Box (Perplexity style) */}
                      <form onSubmit={handleSendMessage} className="relative flex items-center bg-card border border-card-border hover:border-border transition-all duration-300 rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-primary/20 p-1.5">
                        <Input
                          type="text"
                          placeholder="Ask the focused workspace documents..."
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          disabled={isStreaming}
                          className="w-full border-0 focus-visible:ring-0 shadow-none px-4 py-3 bg-transparent text-sm text-foreground focus-visible:outline-none placeholder:text-muted-foreground/75"
                        />
                        <button
                          type="submit"
                          disabled={!chatInput.trim() || isStreaming}
                          className="h-10 w-10 flex items-center justify-center rounded-xl bg-primary text-primary-foreground hover:bg-primary/95 transition-all duration-200 shadow-sm disabled:opacity-30 disabled:pointer-events-none shrink-0"
                        >
                          <ArrowUpRight className="h-5 w-5" />
                        </button>
                      </form>
                    </div>
                  </div>
                </>
              ) : activeTab === "contradictions" ? (
                /* CONTRADICTION INTELLIGENCE PANEL */
                <div className="flex-1 flex flex-col min-h-0 relative bg-background select-text">
                  <div className="flex-1 overflow-y-auto p-8 space-y-8 select-text">
                    <div className="max-w-4xl mx-auto space-y-8">
                      {/* Document Selector & Action Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border border-card-border bg-card/60 rounded-2xl shadow-xs">
                        <div className="space-y-1">
                          <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                            <AlertCircle className="h-5 w-5 text-amber-500" />
                            Contradiction Intelligence Audit
                          </h3>
                          <p className="text-xs text-muted-foreground">
                            Analyze vectors to detect inconsistent claims, timelines, or requirements.
                          </p>
                        </div>
                        <div className="flex items-center gap-3.5">
                          {/* target document picker if there are multiple documents */}
                          {activeSession.documentIds.length > 1 ? (
                            <select
                              value={selectedContradictionDocId || ""}
                              onChange={(e) => setSelectedContradictionDocId(e.target.value)}
                              disabled={isAnalyzingContradictions}
                              className="text-xs px-3 py-2 bg-secondary/50 border border-border rounded-xl text-foreground focus-visible:outline-none"
                            >
                              {activeSession.documentIds.map((docId) => {
                                const d = documents.find((doc) => doc.id === docId);
                                return (
                                  <option key={docId} value={docId}>
                                    {d ? d.name : docId}
                                  </option>
                                );
                              })}
                            </select>
                          ) : (
                            <span className="text-xs font-semibold bg-secondary/35 border border-border px-3 py-2 rounded-xl">
                              {documents.find((d) => d.id === selectedContradictionDocId)?.name || "1 Target Document"}
                            </span>
                          )}
                          
                          <Button
                            onClick={() => selectedContradictionDocId && runContradictionScan(selectedContradictionDocId)}
                            disabled={isAnalyzingContradictions || !selectedContradictionDocId}
                            className="bg-primary hover:bg-primary/95 text-primary-foreground font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-primary/10"
                          >
                            {isAnalyzingContradictions ? (
                              <>
                                <Loader2 className="h-3 w-3 animate-spin" />
                                Analyzing...
                              </>
                            ) : (
                              <>
                                <Search className="h-3 w-3" />
                                Scan Document
                              </>
                            )}
                          </Button>
                        </div>
                      </div>

                      {/* Scanning Cinematic State */}
                      {isAnalyzingContradictions && (
                        <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/25 rounded-2xl space-y-6">
                          <div className="relative flex items-center justify-center">
                            <span className="absolute h-14 w-14 rounded-full bg-primary/10 animate-ping" />
                            <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm">
                              <Sparkles className="h-5 w-5 animate-pulse text-primary" />
                            </div>
                          </div>
                          <div className="space-y-2 text-center">
                            <p className="text-sm font-semibold text-foreground animate-pulse">
                              {contradictionStatus}
                            </p>
                            <p className="text-[10px] text-muted-foreground uppercase tracking-widest leading-none font-mono">
                              Executing semantic analysis pipeline...
                            </p>
                          </div>
                          
                          {/* Progress bar loader */}
                          <div className="w-64 h-1.5 bg-secondary rounded-full overflow-hidden relative">
                            <motion.div
                              initial={{ left: "-100%" }}
                              animate={{ left: "100%" }}
                              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                              className="absolute w-1/2 h-full bg-primary rounded-full"
                            />
                          </div>
                        </div>
                      )}

                      {/* Empty State */}
                      {!isAnalyzingContradictions && contradictionInsights.length === 0 && (
                        <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/10 rounded-2xl text-center space-y-4">
                          <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground">
                            <Brain className="h-6 w-6" />
                          </div>
                          <div className="space-y-1">
                            <h4 className="text-sm font-bold text-foreground">
                              No findings generated yet
                            </h4>
                            <p className="text-xs text-muted-foreground max-w-sm">
                              Trigger a contradiction scan using the header control above to audit statements, dates, and numbers.
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Severity Metrics Card Summary */}
                      {!isAnalyzingContradictions && contradictionInsights.length > 0 && (
                        <div className="grid grid-cols-3 gap-4">
                          {(["high", "medium", "low"] as const).map((sev) => {
                            const count = contradictionInsights.filter((x) => x.severity === sev).length;
                            return (
                              <div
                                key={sev}
                                className={cn(
                                  "p-4 border rounded-xl flex items-center gap-3 shadow-2xs",
                                  sev === "high"
                                    ? "bg-rose-500/5 border-rose-500/20 text-rose-700 dark:text-rose-400"
                                    : sev === "medium"
                                    ? "bg-amber-500/5 border-amber-500/20 text-amber-700 dark:text-amber-400"
                                    : "bg-sky-500/5 border-sky-500/20 text-sky-700 dark:text-sky-400"
                                )}
                              >
                                <div
                                  className={cn(
                                    "h-8 w-8 rounded-lg flex items-center justify-center font-bold text-xs uppercase leading-none border",
                                    sev === "high"
                                      ? "bg-rose-500/10 border-rose-500/30"
                                      : sev === "medium"
                                      ? "bg-amber-500/10 border-amber-500/30"
                                      : "bg-sky-500/10 border-sky-500/30"
                                  )}
                                >
                                  {sev[0]}
                                </div>
                                <div>
                                  <span className="text-[10px] uppercase font-bold tracking-wider block opacity-75 leading-none">
                                    {sev} severity
                                  </span>
                                  <span className="text-lg font-extrabold block mt-1 font-sans">
                                    {count} findings
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Insights Audit feed */}
                      {!isAnalyzingContradictions && contradictionInsights.length > 0 && (
                        <div className="space-y-4">
                          {contradictionInsights.map((insight) => {
                            const isExpanded = expandedContradictionId === insight.id;
                            const isWhyOpen = expandedReasoningMap[insight.id]?.why ?? true;
                            const isEvidenceOpen = expandedReasoningMap[insight.id]?.evidence ?? false;
                            const isTimelineOpen = expandedReasoningMap[insight.id]?.timeline ?? false;
                            const isNumOpen = expandedReasoningMap[insight.id]?.numerical ?? false;

                            return (
                              <div
                                key={insight.id}
                                className={cn(
                                  "border rounded-2xl overflow-hidden transition-all duration-300 shadow-2xs bg-card",
                                  isExpanded ? "border-primary/30 ring-1 ring-primary/5" : "border-card-border hover:border-border"
                                )}
                              >
                                {/* Accordion Header */}
                                <div
                                  onClick={() => setExpandedContradictionId(isExpanded ? null : insight.id)}
                                  className="p-5 flex items-start justify-between gap-4 cursor-pointer select-none hover:bg-secondary/10 transition-colors"
                                >
                                  <div className="space-y-2.5">
                                    <div className="flex items-center gap-2">
                                      <Badge
                                        className={cn(
                                          "text-[8px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border-0",
                                          insight.severity === "high"
                                            ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                                            : insight.severity === "medium"
                                            ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                                            : "bg-sky-500/10 text-sky-600 dark:text-sky-400"
                                        )}
                                      >
                                        {insight.severity} severity
                                      </Badge>
                                      
                                      <Badge variant="outline" className="text-[8px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border-border bg-secondary/20 text-muted-foreground">
                                        {insight.type}
                                      </Badge>
                                      
                                      <span className="text-[10px] text-muted-foreground font-mono font-medium">
                                        {(insight.confidence * 100).toFixed(0)}% confidence
                                      </span>
                                    </div>
                                    <h4 className="text-sm font-bold text-foreground leading-tight">
                                      {insight.summary}
                                    </h4>
                                  </div>
                                  <ChevronDown
                                    className={cn("h-4.5 w-4.5 text-muted-foreground transition-transform duration-300 shrink-0 mt-1", {
                                      "transform rotate-180 text-primary": isExpanded,
                                    })}
                                  />
                                </div>

                                {/* Accordion Content */}
                                <AnimatePresence initial={false}>
                                  {isExpanded && (
                                    <motion.div
                                      initial={{ height: 0, opacity: 0 }}
                                      animate={{ height: "auto", opacity: 1 }}
                                      exit={{ height: 0, opacity: 0 }}
                                      transition={{ duration: 0.25, ease: "easeInOut" }}
                                      className="overflow-hidden border-t border-border bg-secondary/10"
                                    >
                                      <div className="p-5 space-y-4">
                                        
                                        {/* Sub-Accordion 1: Why contradiction detected */}
                                        <div className="border border-border rounded-xl bg-card overflow-hidden shadow-2xs">
                                          <button
                                            onClick={() => toggleReasoningPanel(insight.id, "why")}
                                            className="w-full px-4 py-2.5 flex items-center justify-between text-xs text-foreground font-semibold hover:bg-secondary/30 transition-colors"
                                          >
                                            <span className="flex items-center gap-2">
                                              <Info className="h-3.5 w-3.5 text-primary" />
                                              Why Contradiction Detected
                                            </span>
                                            <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", isWhyOpen && "transform rotate-180")} />
                                          </button>
                                          <AnimatePresence initial={false}>
                                            {isWhyOpen && (
                                              <motion.div
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: "auto", opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                transition={{ duration: 0.2, ease: "easeInOut" }}
                                                className="overflow-hidden border-t border-border"
                                              >
                                                <div className="px-4 pb-4 pt-2 text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap font-sans">
                                                  {insight.explanation}
                                                </div>
                                              </motion.div>
                                            )}
                                          </AnimatePresence>
                                        </div>

                                        {/* Sub-Accordion 2: Supporting evidence */}
                                        <div className="border border-border rounded-xl bg-card overflow-hidden shadow-2xs">
                                          <button
                                            onClick={() => toggleReasoningPanel(insight.id, "evidence")}
                                            className="w-full px-4 py-2.5 flex items-center justify-between text-xs text-foreground font-semibold hover:bg-secondary/30 transition-colors"
                                          >
                                            <span className="flex items-center gap-2">
                                              <FileText className="h-3.5 w-3.5 text-indigo-500" />
                                              Supporting Evidence ({insight.citations.length} cited segments)
                                            </span>
                                            <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", isEvidenceOpen && "transform rotate-180")} />
                                          </button>
                                          <AnimatePresence initial={false}>
                                            {isEvidenceOpen && (
                                              <motion.div
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: "auto", opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                transition={{ duration: 0.2, ease: "easeInOut" }}
                                                className="overflow-hidden border-t border-border"
                                              >
                                                <div className="px-4 pb-4 pt-2 space-y-3.5">
                                                  {insight.citations.map((cit: any, idx: number) => (
                                                    <div key={idx} className="space-y-1.5 p-3 rounded-lg border border-border bg-secondary/20">
                                                      <div className="flex items-center justify-between text-[9px] font-bold text-muted-foreground uppercase tracking-wider leading-none">
                                                        <span>Source Chunk {idx + 1}</span>
                                                        <span>Page {cit.pageNumber}</span>
                                                      </div>
                                                      <p className="text-xs text-foreground font-medium italic select-all leading-normal">
                                                        &ldquo;{cit.snippet}&rdquo;
                                                      </p>
                                                    </div>
                                                  ))}
                                                </div>
                                              </motion.div>
                                            )}
                                          </AnimatePresence>
                                        </div>

                                        {/* Sub-Accordion 3: Timeline comparison (Only for timeline conflicts) */}
                                        {insight.type === "timeline" && (
                                          <div className="border border-border rounded-xl bg-card overflow-hidden shadow-2xs">
                                            <button
                                              onClick={() => toggleReasoningPanel(insight.id, "timeline")}
                                              className="w-full px-4 py-2.5 flex items-center justify-between text-xs text-foreground font-semibold hover:bg-secondary/30 transition-colors"
                                            >
                                              <span className="flex items-center gap-2">
                                                <Activity className="h-3.5 w-3.5 text-amber-500" />
                                                Timeline Comparison
                                              </span>
                                              <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", isTimelineOpen && "transform rotate-180")} />
                                            </button>
                                            <AnimatePresence initial={false}>
                                              {isTimelineOpen && (
                                                <motion.div
                                                  initial={{ height: 0, opacity: 0 }}
                                                  animate={{ height: "auto", opacity: 1 }}
                                                  exit={{ height: 0, opacity: 0 }}
                                                  transition={{ duration: 0.2, ease: "easeInOut" }}
                                                  className="overflow-hidden border-t border-border"
                                                >
                                                  <div className="px-4 pb-4 pt-2 text-xs text-muted-foreground leading-relaxed">
                                                    <p className="font-semibold text-foreground mb-3 font-sans">Sequential Timeline Breakdown:</p>
                                                    <div className="relative pl-6 border-l-2 border-primary/30 space-y-5 py-2 font-sans ml-2">
                                                      {insight.conflictingStatements.map((stmt: any, idx: number) => (
                                                        <motion.div 
                                                          key={idx} 
                                                          initial={{ opacity: 0, x: -10 }}
                                                          animate={{ opacity: 1, x: 0 }}
                                                          transition={{ delay: idx * 0.1 }}
                                                          className="relative group/timeline"
                                                        >
                                                          <div className="absolute -left-[31px] top-1.5 h-3.5 w-3.5 rounded-full bg-card border-2 border-primary flex items-center justify-center transition-all duration-300 group-hover/timeline:scale-125 group-hover/timeline:bg-primary shadow-sm shadow-primary/20">
                                                            <div className="h-1.5 w-1.5 rounded-full bg-primary group-hover/timeline:bg-card" />
                                                          </div>
                                                          <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/15 uppercase tracking-wider mb-2 inline-block leading-none">
                                                            Page {stmt.page} claim
                                                          </span>
                                                          <p className="text-xs text-foreground leading-relaxed font-semibold p-3 rounded-xl bg-secondary/30 border border-border/40 group-hover/timeline:border-primary/20 group-hover/timeline:bg-secondary/50 transition-all duration-300">
                                                            {stmt.text}
                                                          </p>
                                                        </motion.div>
                                                      ))}
                                                    </div>
                                                  </div>
                                                </motion.div>
                                              )}
                                            </AnimatePresence>
                                          </div>
                                        )}

                                        {/* Sub-Accordion 4: Numerical mismatch reasoning */}
                                        {insight.type === "numerical" && (
                                          <div className="border border-border rounded-xl bg-card overflow-hidden shadow-2xs">
                                            <button
                                              onClick={() => toggleReasoningPanel(insight.id, "numerical")}
                                              className="w-full px-4 py-2.5 flex items-center justify-between text-xs text-foreground font-semibold hover:bg-secondary/30 transition-colors"
                                            >
                                              <span className="flex items-center gap-2">
                                                <Activity className="h-3.5 w-3.5 text-rose-500" />
                                                Numerical Mismatch Reasoning
                                              </span>
                                              <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", isNumOpen && "transform rotate-180")} />
                                            </button>
                                            <AnimatePresence initial={false}>
                                              {isNumOpen && (
                                                <motion.div
                                                  initial={{ height: 0, opacity: 0 }}
                                                  animate={{ height: "auto", opacity: 1 }}
                                                  exit={{ height: 0, opacity: 0 }}
                                                  transition={{ duration: 0.2, ease: "easeInOut" }}
                                                  className="overflow-hidden border-t border-border"
                                                >
                                                  <div className="px-4 pb-4 pt-2 text-xs text-muted-foreground leading-relaxed">
                                                    <p className="font-semibold text-foreground mb-1.5 font-sans">Quantitative audit:</p>
                                                    <div className="p-3 bg-secondary/15 rounded-lg border border-border space-y-2">
                                                      {insight.conflictingStatements.map((stmt: any, idx: number) => (
                                                        <div key={idx} className="text-xs">
                                                          <span className="font-bold text-foreground font-mono">Statement {idx + 1} (Page {stmt.page}):</span>{" "}
                                                          <span className="italic font-medium">&ldquo;{stmt.text}&rdquo;</span>
                                                        </div>
                                                      ))}
                                                    </div>
                                                  </div>
                                                </motion.div>
                                              )}
                                            </AnimatePresence>
                                          </div>
                                        )}

                                      </div>
                                    </motion.div>
                                  )}
                                </AnimatePresence>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Telemetry Observability block */}
                      {!isAnalyzingContradictions && contradictionTelemetry && (
                        <div className="space-y-3 pt-4">
                          <div className="flex items-center gap-2 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                            <Activity className="h-4 w-4 text-emerald-500 animate-pulse" />
                            Observability telemetry metrics
                          </div>
                          
                          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                            <div className="p-3.5 border border-card-border bg-card/45 rounded-xl shadow-2xs space-y-1">
                              <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider block leading-none">
                                retrieval hits
                              </span>
                              <span className="text-lg font-extrabold text-foreground block font-mono">
                                {contradictionTelemetry.retrievalCount} chunks
                              </span>
                            </div>
                            <div className="p-3.5 border border-card-border bg-card/45 rounded-xl shadow-2xs space-y-1">
                              <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider block leading-none">
                                contradictions
                              </span>
                              <span className="text-lg font-extrabold text-foreground block font-mono">
                                {contradictionTelemetry.contradictionCount} items
                              </span>
                            </div>
                            <div className="p-3.5 border border-card-border bg-card/45 rounded-xl shadow-2xs space-y-1">
                              <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider block leading-none">
                                reasoning time
                              </span>
                              <span className="text-lg font-extrabold text-foreground block font-mono">
                                {contradictionTelemetry.reasoningLatency}s
                              </span>
                            </div>
                            <div className="p-3.5 border border-card-border bg-card/45 rounded-xl shadow-2xs space-y-1">
                              <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider block leading-none">
                                orchestration
                              </span>
                              <span className="text-lg font-extrabold text-foreground block font-mono">
                                {contradictionTelemetry.orchestrationLatency}s
                              </span>
                            </div>
                            <div className="p-3.5 border border-card-border bg-card/45 rounded-xl shadow-2xs space-y-1">
                              <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider block leading-none">
                                model provider
                              </span>
                              <span className="text-lg font-extrabold text-foreground block font-mono">
                                {contradictionTelemetry.providerLatency}s
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                    </div>
                  </div>
                </div>
              ) : activeTab === "intelligence" ? (
                /* DOCUMENT INTELLIGENCE PANEL */
                <div className="flex-1 flex flex-col min-h-0 bg-background select-text">
                  <div className="flex-1 overflow-y-auto p-8 space-y-8">
                    <div className="max-w-4xl mx-auto space-y-8">

                      {/* Header + Run Button */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border border-card-border bg-card/60 rounded-2xl shadow-xs">
                        <div className="space-y-1">
                          <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                            <Shield className="h-5 w-5 text-violet-500" />
                            Document Intelligence Report
                          </h3>
                          <p className="text-xs text-muted-foreground">Trust score, executive brief, review checklist, ambiguities, references & requirements traceability.</p>
                        </div>
                        <div className="flex items-center gap-3">
                          {activeSession && activeSession.documentIds.length > 1 && (
                            <select
                              value={intelligenceDocId || ""}
                              onChange={e => setIntelligenceDocId(e.target.value)}
                              disabled={isLoadingIntelligence}
                              className="text-xs px-3 py-2 bg-secondary/50 border border-border rounded-xl text-foreground focus-visible:outline-none"
                            >
                              {activeSession.documentIds.map(docId => {
                                const d = documents.find(doc => doc.id === docId);
                                return <option key={docId} value={docId}>{d ? d.name : docId}</option>;
                              })}
                            </select>
                          )}
                          <Button
                            onClick={async () => {
                              if (!intelligenceDocId) return;
                              setIsLoadingIntelligence(true);
                              setTrustScore(null);
                              setExecutiveSummary(null);
                              setReviewCopilot(null);
                              setAmbiguities([]);
                              setReferences([]);
                              setRequirements([]);
                              addLog("INFO", `Running Document Intelligence for doc: ${intelligenceDocId}`);
                              try {
                                const [ts, es, rv, amb, refs, reqs] = await Promise.all([
                                  sdk.getTrustScore(intelligenceDocId),
                                  sdk.getExecutiveSummary(intelligenceDocId),
                                  sdk.getReview(intelligenceDocId),
                                  sdk.getAmbiguities(intelligenceDocId),
                                  sdk.getReferences(intelligenceDocId),
                                  sdk.getRequirements(intelligenceDocId),
                                ]);
                                setTrustScore(ts);
                                setExecutiveSummary(es);
                                setReviewCopilot(rv);
                                setAmbiguities(amb);
                                setReferences(refs);
                                setRequirements(reqs);
                                addLog("SUCCESS", `Intelligence report ready. Trust score: ${typeof ts.score === "number" ? ts.score.toFixed(1) : "N/A"}`);
                              } catch (err: any) {
                                addLog("ERROR", `Intelligence report failed: ${err.message}`);
                                setErrorMsg(err.message);
                              } finally {
                                setIsLoadingIntelligence(false);
                              }
                            }}
                            disabled={isLoadingIntelligence || !intelligenceDocId}
                            className="bg-violet-600 hover:bg-violet-700 text-white font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-violet-500/20"
                          >
                            {isLoadingIntelligence ? (
                              <><Loader2 className="h-3 w-3 animate-spin" />Analyzing...</>
                            ) : (
                              <><Zap className="h-3 w-3" />Run Intelligence</>  
                            )}
                          </Button>
                        </div>
                      </div>

                      {/* Loading State */}
                      {isLoadingIntelligence && (
                        <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/25 rounded-2xl space-y-6">
                          <div className="relative flex items-center justify-center">
                            <span className="absolute h-14 w-14 rounded-full bg-violet-500/10 animate-ping" />
                            <div className="h-10 w-10 rounded-full bg-violet-500/20 flex items-center justify-center">
                              <Shield className="h-5 w-5 animate-pulse text-violet-500" />
                            </div>
                          </div>
                          <p className="text-sm font-semibold text-foreground animate-pulse">Running intelligence pipeline…</p>
                          <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-mono">Trust · Summary · Review · Ambiguity · References · Requirements</p>
                          <div className="w-64 h-1.5 bg-secondary rounded-full overflow-hidden relative">
                            <motion.div
                              initial={{ left: "-100%" }} animate={{ left: "100%" }}
                              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                              className="absolute w-1/2 h-full bg-violet-500 rounded-full"
                            />
                          </div>
                        </div>
                      )}

                      {/* Empty State */}
                      {!isLoadingIntelligence && (!trustScore || typeof trustScore.score !== "number") && (
                        <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/10 rounded-2xl text-center space-y-4">
                          <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground">
                            <Shield className="h-6 w-6" />
                          </div>
                          <div className="space-y-1">
                            <h4 className="text-sm font-bold text-foreground">No intelligence report yet</h4>
                            <p className="text-xs text-muted-foreground max-w-sm">Click Run Intelligence to generate a full document trust score, executive summary, review checklist, and traceability audit.</p>
                          </div>
                        </div>
                      )}

                      {/* Intelligence Results */}
                      {!isLoadingIntelligence && trustScore && typeof trustScore.score === "number" && (
                        <>
                          {/* Sub-Tab Navigation */}
                          <div className="relative flex gap-1 bg-secondary/30 p-1 rounded-xl border border-border w-fit z-0">
                            {(["overview", "review", "ambiguities", "references", "requirements"] as const).map(st => {
                              const isActive = intelligenceSubTab === st;
                              return (
                                <button
                                  key={st}
                                  onClick={() => setIntelligenceSubTab(st)}
                                  className={cn(
                                    "relative px-3 py-1.5 text-[11px] font-semibold rounded-lg capitalize transition-all select-none z-10",
                                    isActive
                                      ? "text-foreground font-bold"
                                      : "text-muted-foreground hover:text-foreground"
                                  )}
                                >
                                  {isActive && (
                                    <motion.span
                                      layoutId="activeSubTabPill"
                                      className="absolute inset-0 bg-card border border-card-border shadow-xs rounded-lg -z-10"
                                      transition={{ type: "spring", stiffness: 350, damping: 28 }}
                                    />
                                  )}
                                  {st === "overview" ? "Overview" : st === "review" ? "Review Copilot" : st === "ambiguities" ? "Ambiguities" : st === "references" ? "References" : "Requirements"}
                                </button>
                              );
                            })}
                          </div>

                          {/* OVERVIEW SUB-TAB */}
                          {intelligenceSubTab === "overview" && (
                            <div className="space-y-6">
                              {/* Trust Score Gauge */}
                              <div className="p-6 border border-card-border bg-card rounded-2xl shadow-xs">
                                <div className="flex flex-col md:flex-row items-center gap-8">
                                  {/* Radial Gauge */}
                                  <div className="relative flex items-center justify-center shrink-0">
                                    <svg viewBox="0 0 120 120" className="w-36 h-36">
                                      <circle cx="60" cy="60" r="50" fill="none" stroke="currentColor" strokeWidth="8" className="text-secondary/60" />
                                      <motion.circle
                                        cx="60" cy="60" r="50" fill="none"
                                        stroke={trustScore.score >= 80 ? "#22c55e" : trustScore.score >= 60 ? "#eab308" : "#ef4444"}
                                        strokeWidth="8"
                                        strokeLinecap="round"
                                        initial={{ strokeDasharray: "0 314" }}
                                        animate={{ strokeDasharray: `${(trustScore.score / 100) * 314} 314` }}
                                        transition={{ duration: 1.2, ease: "easeOut" }}
                                        transform="rotate(-90 60 60)"
                                      />
                                    </svg>
                                    <div className="absolute text-center">
                                      <span className={cn("text-3xl font-extrabold font-mono block", trustScore.score >= 80 ? "text-emerald-500" : trustScore.score >= 60 ? "text-amber-500" : "text-rose-500")}>
                                        {animatedScore.toFixed(0)}
                                      </span>
                                      <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Trust Score</span>
                                    </div>
                                  </div>

                                  {/* Breakdown Bars */}
                                  <div className="flex-1 space-y-3 w-full">
                                    <h4 className="text-sm font-bold text-foreground">Score Breakdown</h4>
                                    {(trustScore.deductions || []).map((d, i) => {
                                      const deductionPts = d.points ?? d.weighted_deduction ?? 0;
                                      const deductionComp = d.component || d.dimension || "Deduction";
                                      const deductionReason = d.evidence || d.reason || "";
                                      return (
                                        <div key={i} className="space-y-1">
                                          <div className="flex items-center justify-between text-[10px]">
                                            <span className="font-semibold text-foreground capitalize">{deductionComp}</span>
                                            <span className="font-mono text-muted-foreground">-{deductionPts.toFixed(1)} pts</span>
                                          </div>
                                          <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                                            <motion.div
                                              initial={{ width: 0 }}
                                              animate={{ width: `${Math.min(100, deductionPts * 5)}%` }}
                                              transition={{ duration: 0.8, ease: "easeOut" }}
                                              className={cn("h-full rounded-full", deductionPts > 5 ? "bg-rose-500" : deductionPts > 2 ? "bg-amber-500" : "bg-emerald-500")}
                                            />
                                          </div>
                                          <p className="text-[9px] text-muted-foreground">{deductionReason}</p>
                                        </div>
                                      );
                                    })}
                                    {(trustScore.deductions || []).length === 0 && (
                                      <p className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold">✓ No significant deductions — document scores clean.</p>
                                    )}
                                  </div>
                                </div>

                                {trustScore.evidence && (
                                  <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground leading-relaxed">
                                    <span className="font-bold text-foreground block mb-1">Evidence Summary</span>
                                    {trustScore.evidence}
                                  </div>
                                )}
                              </div>

                              {/* Executive Summary */}
                              {executiveSummary && executiveSummary.executive_summary && (
                                <div className="p-6 border border-card-border bg-card rounded-2xl shadow-xs space-y-5">
                                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                                    <BookMarked className="h-4 w-4 text-violet-500" />
                                    Executive Summary
                                  </h4>
                                  <p className="text-xs text-muted-foreground leading-relaxed">{executiveSummary.executive_summary}</p>

                                  {(executiveSummary.key_findings || []).length > 0 && (
                                    <div className="space-y-2">
                                      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Key Findings</span>
                                      <ul className="space-y-1.5">
                                        {(executiveSummary.key_findings || []).map((f, i) => (
                                          <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 mt-0.5 shrink-0" />{f}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}

                                  {(executiveSummary.critical_risks || []).length > 0 && (
                                    <div className="space-y-2">
                                      <span className="text-[10px] font-bold text-rose-500 uppercase tracking-wider block">Critical Risks</span>
                                      <ul className="space-y-1.5">
                                        {(executiveSummary.critical_risks || []).map((r, i) => (
                                          <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                            <XCircle className="h-3.5 w-3.5 text-rose-500 mt-0.5 shrink-0" />{r}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}

                                  {(executiveSummary.recommended_actions || []).length > 0 && (
                                    <div className="space-y-2">
                                      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Recommended Actions</span>
                                      <ul className="space-y-1.5">
                                        {(executiveSummary.recommended_actions || []).map((a, i) => (
                                          <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                            <ArrowUpRight className="h-3.5 w-3.5 text-violet-500 mt-0.5 shrink-0" />{a}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}

                                  {executiveSummary.trust_assessment && (
                                    <div className="p-3 rounded-xl bg-secondary/20 border border-border text-xs text-muted-foreground">
                                      <span className="font-bold text-foreground block mb-1">Trust Assessment</span>
                                      {executiveSummary.trust_assessment}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}

                          {/* REVIEW COPILOT SUB-TAB */}
                          {intelligenceSubTab === "review" && reviewCopilot && (
                            <div className="space-y-6">
                              {/* Checklist */}
                              {(reviewCopilot.reviewer_checklist || []).length > 0 && (
                                <div className="p-5 border border-card-border bg-card rounded-2xl shadow-xs space-y-3">
                                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                                    <ListChecks className="h-4 w-4 text-violet-500" />
                                    Reviewer Checklist
                                  </h4>
                                  <div className="space-y-2">
                                    {(reviewCopilot.reviewer_checklist || []).map((item, i) => (
                                      <div key={i} className={cn("p-3 rounded-xl border flex items-start gap-3",
                                        item.status === "pass" ? "bg-emerald-500/5 border-emerald-500/20" :
                                        item.status === "fail" ? "bg-rose-500/5 border-rose-500/20" :
                                        item.status === "warning" ? "bg-amber-500/5 border-amber-500/20" :
                                        "bg-secondary/20 border-border"
                                      )}>
                                        <div className="shrink-0 mt-0.5">
                                          {item.status === "pass" ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> :
                                           item.status === "fail" ? <XCircle className="h-4 w-4 text-rose-500" /> :
                                           item.status === "warning" ? <AlertCircle className="h-4 w-4 text-amber-500" /> :
                                           <Info className="h-4 w-4 text-sky-500" />}
                                        </div>
                                        <div className="space-y-0.5 flex-1">
                                          <div className="flex items-center gap-2">
                                            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">{item.category}</span>
                                          </div>
                                          <p className="text-xs font-semibold text-foreground">{item.item}</p>
                                          <p className="text-[10px] text-muted-foreground leading-relaxed">{item.detail}</p>
                                          {item.evidence && <p className="text-[9px] text-muted-foreground italic mt-1">Evidence: {item.evidence}</p>}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Risk Items */}
                              {(reviewCopilot.risk_items || []).length > 0 && (
                                <div className="p-5 border border-card-border bg-card rounded-2xl shadow-xs space-y-3">
                                  <h4 className="text-sm font-bold text-rose-600 dark:text-rose-400 flex items-center gap-2">
                                    <AlertCircle className="h-4 w-4" />Risk Items
                                  </h4>
                                  <ul className="space-y-1.5">
                                    {(reviewCopilot.risk_items || []).map((r, i) => (
                                      <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                        <XCircle className="h-3.5 w-3.5 text-rose-500 mt-0.5 shrink-0" />{r}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Open Questions */}
                              {(reviewCopilot.open_questions || []).length > 0 && (
                                <div className="p-5 border border-card-border bg-card rounded-2xl shadow-xs space-y-3">
                                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                                    <HelpCircle className="h-4 w-4 text-amber-500" />Open Questions
                                  </h4>
                                  <ul className="space-y-1.5">
                                    {(reviewCopilot.open_questions || []).map((q, i) => (
                                      <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                        <HelpCircle className="h-3.5 w-3.5 text-amber-500 mt-0.5 shrink-0" />{q}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Verification Tasks */}
                              {(reviewCopilot.verification_tasks || []).length > 0 && (
                                <div className="p-5 border border-card-border bg-card rounded-2xl shadow-xs space-y-3">
                                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                                    <ClipboardList className="h-4 w-4 text-sky-500" />Verification Tasks
                                  </h4>
                                  <ul className="space-y-1.5">
                                    {(reviewCopilot.verification_tasks || []).map((t, i) => (
                                      <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                        <ClipboardList className="h-3.5 w-3.5 text-sky-500 mt-0.5 shrink-0" />{t}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}

                          {/* AMBIGUITIES SUB-TAB */}
                          {intelligenceSubTab === "ambiguities" && (
                            <div className="space-y-4">
                              {ambiguities.length === 0 ? (
                                <div className="p-10 border border-dashed border-border rounded-2xl text-center text-xs text-muted-foreground">
                                  No ambiguities detected in this document.
                                </div>
                              ) : (
                                <>
                                  <div className="grid grid-cols-3 gap-3">
                                    {(["high", "medium", "low"] as const).map(sev => {
                                      const count = ambiguities.filter(a => a.severity === sev).length;
                                      return (
                                        <div key={sev} className={cn("p-4 rounded-xl border flex items-center gap-3 shadow-2xs",
                                          sev === "high" ? "bg-rose-500/5 border-rose-500/20 text-rose-700 dark:text-rose-400" :
                                          sev === "medium" ? "bg-amber-500/5 border-amber-500/20 text-amber-700 dark:text-amber-400" :
                                          "bg-sky-500/5 border-sky-500/20 text-sky-700 dark:text-sky-400"
                                        )}>
                                          <span className="text-2xl font-extrabold font-mono">{count}</span>
                                          <span className="text-[10px] font-bold uppercase tracking-wider capitalize">{sev}</span>
                                        </div>
                                      );
                                    })}
                                  </div>
                                  <div className="space-y-3">
                                    {ambiguities.map((a, i) => (
                                      <div key={i} className={cn("p-4 border rounded-xl space-y-2",
                                        a.severity === "high" ? "border-rose-500/20 bg-rose-500/5" :
                                        a.severity === "medium" ? "border-amber-500/20 bg-amber-500/5" :
                                        "border-sky-500/20 bg-sky-500/5"
                                      )}>
                                        <div className="flex items-center gap-2">
                                          <Badge className={cn("text-[8px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border-0",
                                            a.severity === "high" ? "bg-rose-500/10 text-rose-600" :
                                            a.severity === "medium" ? "bg-amber-500/10 text-amber-600" :
                                            "bg-sky-500/10 text-sky-600"
                                          )}>{a.severity}</Badge>
                                          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">{a.type}</span>
                                          <span className="text-[10px] text-muted-foreground">· Page {a.page}</span>
                                        </div>
                                        <p className="text-xs text-foreground italic">&ldquo;{a.snippet}&rdquo;</p>
                                        <p className="text-[10px] text-muted-foreground">
                                          <span className="font-semibold">Pattern:</span> {a.matched_pattern}
                                        </p>
                                        {a.suggestion && (
                                          <p className="text-[10px] text-emerald-600 dark:text-emerald-400">
                                            <span className="font-semibold">Suggestion:</span> {a.suggestion}
                                          </p>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                </>
                              )}
                            </div>
                          )}

                          {/* REFERENCES SUB-TAB */}
                          {intelligenceSubTab === "references" && (
                            <div className="space-y-4">
                              {references.length === 0 ? (
                                <div className="p-10 border border-dashed border-border rounded-2xl text-center text-xs text-muted-foreground">
                                  No references detected in this document.
                                </div>
                              ) : (
                                <>
                                  <div className="grid grid-cols-3 gap-3">
                                    {(["resolved", "unresolved", "external"] as const).map(st => {
                                      const count = references.filter(r => r.status === st).length;
                                      return (
                                        <div key={st} className={cn("p-4 rounded-xl border flex items-center gap-3",
                                          st === "resolved" ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-700 dark:text-emerald-400" :
                                          st === "unresolved" ? "bg-rose-500/5 border-rose-500/20 text-rose-700 dark:text-rose-400" :
                                          "bg-sky-500/5 border-sky-500/20 text-sky-700 dark:text-sky-400"
                                        )}>
                                          <span className="text-2xl font-extrabold font-mono">{count}</span>
                                          <span className="text-[10px] font-bold uppercase tracking-wider capitalize">{st}</span>
                                        </div>
                                      );
                                    })}
                                  </div>
                                  <div className="space-y-2">
                                    {references.map((ref, i) => (
                                      <div key={i} className="p-4 border border-card-border bg-card rounded-xl flex items-start gap-3 shadow-2xs">
                                        <Link className={cn("h-4 w-4 mt-0.5 shrink-0",
                                          ref.status === "resolved" ? "text-emerald-500" :
                                          ref.status === "unresolved" ? "text-rose-500" : "text-sky-500"
                                        )} />
                                        <div className="flex-1 space-y-0.5">
                                          <div className="flex items-center gap-2">
                                            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">{ref.ref_type}</span>
                                            <Badge className={cn("text-[8px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full border-0",
                                              ref.status === "resolved" ? "bg-emerald-500/10 text-emerald-600" :
                                              ref.status === "unresolved" ? "bg-rose-500/10 text-rose-600" :
                                              "bg-sky-500/10 text-sky-600"
                                            )}>{ref.status}</Badge>
                                            <span className="text-[9px] text-muted-foreground">· Page {ref.page}</span>
                                          </div>
                                          <p className="text-xs font-mono text-foreground">{ref.raw}</p>
                                          {ref.detail && <p className="text-[10px] text-muted-foreground">{ref.detail}</p>}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </>
                              )}
                            </div>
                          )}

                          {/* REQUIREMENTS SUB-TAB */}
                          {intelligenceSubTab === "requirements" && (
                            <div className="space-y-4">
                              {requirements.length === 0 ? (
                                <div className="p-10 border border-dashed border-border rounded-2xl text-center text-xs text-muted-foreground">
                                  No requirements detected in this document.
                                </div>
                              ) : (
                                <>
                                  <div className="grid grid-cols-4 gap-3">
                                    {(["DEFINED", "REFERENCED", "ORPHANED", "MISSING"] as const).map(st => {
                                      const count = requirements.filter(r => r.status === st).length;
                                      return (
                                        <div key={st} className={cn("p-3 rounded-xl border text-center shadow-2xs",
                                          st === "DEFINED" ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-700 dark:text-emerald-400" :
                                          st === "REFERENCED" ? "bg-sky-500/5 border-sky-500/20 text-sky-700 dark:text-sky-400" :
                                          st === "ORPHANED" ? "bg-amber-500/5 border-amber-500/20 text-amber-700 dark:text-amber-400" :
                                          "bg-rose-500/5 border-rose-500/20 text-rose-700 dark:text-rose-400"
                                        )}>
                                          <span className="text-2xl font-extrabold font-mono block">{count}</span>
                                          <span className="text-[9px] font-bold uppercase tracking-wider">{st}</span>
                                        </div>
                                      );
                                    })}
                                  </div>
                                  <div className="space-y-2">
                                    {requirements.map((req, i) => (
                                      <div key={i} className="p-4 border border-card-border bg-card rounded-xl flex items-start gap-3 shadow-2xs">
                                        <div className="shrink-0 mt-0.5">
                                          {req.status === "DEFINED" ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> :
                                           req.status === "REFERENCED" ? <Link className="h-4 w-4 text-sky-500" /> :
                                           req.status === "ORPHANED" ? <AlertCircle className="h-4 w-4 text-amber-500" /> :
                                           <XCircle className="h-4 w-4 text-rose-500" />}
                                        </div>
                                        <div className="flex-1 space-y-0.5">
                                          <div className="flex items-center gap-2">
                                            <span className="text-xs font-bold font-mono text-foreground">{req.req_id}</span>
                                            <Badge className={cn("text-[8px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full border-0",
                                              req.status === "DEFINED" ? "bg-emerald-500/10 text-emerald-600" :
                                              req.status === "REFERENCED" ? "bg-sky-500/10 text-sky-600" :
                                              req.status === "ORPHANED" ? "bg-amber-500/10 text-amber-600" :
                                              "bg-rose-500/10 text-rose-600"
                                            )}>{req.status}</Badge>
                                            {req.defined_page !== undefined && (
                                              <span className="text-[9px] text-muted-foreground">Defined: p.{req.defined_page}</span>
                                            )}
                                          </div>
                                          <p className="text-xs text-muted-foreground">{req.description}</p>
                                          {(req.referenced_pages || []).length > 0 && (
                                            <p className="text-[9px] text-muted-foreground">
                                              Referenced on pages: {(req.referenced_pages || []).join(", ")}
                                            </p>
                                          )}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </>
                              )}
                            </div>
                          )}

                        </>
                      )}
                    </div>
                  </div>
                </div>

              ) : activeTab === "entities" ? (
                /* ENTITY INTELLIGENCE PANEL */
              <div className="flex-1 flex flex-col min-h-0 bg-background select-text">
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                  <div className="max-w-4xl mx-auto space-y-8">
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border border-card-border bg-card/60 rounded-2xl shadow-xs">
                      <div className="space-y-1">
                        <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                          <Users className="h-5 w-5 text-indigo-500" />
                          Entity Intelligence Audit
                        </h3>
                        <p className="text-xs text-muted-foreground">LLM-powered extraction of named entities, key facts, and entity conflicts from document content.</p>
                      </div>
                      <div className="flex items-center gap-3">
                        {activeSession && activeSession.documentIds.length > 1 && (
                          <select
                            value={entityDocId || ""}
                            onChange={e => setEntityDocId(e.target.value)}
                            disabled={isLoadingEntities}
                            className="text-xs px-3 py-2 bg-secondary/50 border border-border rounded-xl text-foreground focus-visible:outline-none"
                          >
                            {activeSession.documentIds.map(docId => {
                              const d = documents.find(doc => doc.id === docId);
                              return <option key={docId} value={docId}>{d ? d.name : docId}</option>;
                            })}
                          </select>
                        )}
                        <Button
                          onClick={async () => {
                            if (!entityDocId) return;
                            setIsLoadingEntities(true);
                            setEntityAnalysis(null);
                            try {
                              const analysis = await sdk.getAnalysis(entityDocId);
                              setEntityAnalysis(analysis);
                              addLog("SUCCESS", `Entity analysis complete: ${analysis.entities.length} entities found`);
                            } catch (err: any) {
                              addLog("ERROR", `Entity analysis failed: ${err.message}`);
                              setErrorMsg(err.message);
                            } finally {
                              setIsLoadingEntities(false);
                            }
                          }}
                          disabled={isLoadingEntities || !entityDocId}
                          className="bg-primary hover:bg-primary/95 text-primary-foreground font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-primary/10"
                        >
                          {isLoadingEntities ? (
                            <><Loader2 className="h-3 w-3 animate-spin" />Analysing...</>
                          ) : (
                            <><Tag className="h-3 w-3" />Extract Entities</>
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Loading */}
                    {isLoadingEntities && (
                      <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/25 rounded-2xl space-y-6">
                        <div className="relative flex items-center justify-center">
                          <span className="absolute h-14 w-14 rounded-full bg-indigo-500/10 animate-ping" />
                          <div className="h-10 w-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
                            <Users className="h-5 w-5 animate-pulse text-indigo-500" />
                          </div>
                        </div>
                        <p className="text-sm font-semibold text-foreground animate-pulse">Extracting entities from document...</p>
                        <div className="w-64 h-1.5 bg-secondary rounded-full overflow-hidden relative">
                          <motion.div
                            initial={{ left: "-100%" }} animate={{ left: "100%" }}
                            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                            className="absolute w-1/2 h-full bg-indigo-500 rounded-full"
                          />
                        </div>
                      </div>
                    )}

                    {/* Empty State */}
                    {!isLoadingEntities && !entityAnalysis && (
                      <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/10 rounded-2xl text-center space-y-4">
                        <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground">
                          <Users className="h-6 w-6" />
                        </div>
                        <div className="space-y-1">
                          <h4 className="text-sm font-bold text-foreground">No entity data yet</h4>
                          <p className="text-xs text-muted-foreground max-w-sm">Click Extract Entities to run LLM-powered extraction on the selected document.</p>
                        </div>
                      </div>
                    )}

                    {/* Entity Results */}
                    {!isLoadingEntities && entityAnalysis && (
                      <>
                        {/* Summary */}
                        {entityAnalysis.summary && (
                          <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3 shadow-xs">
                            <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                              <FileText className="h-4 w-4 text-primary" />Document Summary
                            </h4>
                            <p className="text-xs text-muted-foreground leading-relaxed">{entityAnalysis.summary.abstract}</p>
                            {(entityAnalysis.summary.keyPoints || []).length > 0 && (
                              <ul className="space-y-1">
                                {(entityAnalysis.summary.keyPoints || []).map((kp, i) => (
                                  <li key={i} className="text-xs text-foreground flex items-start gap-2">
                                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 mt-0.5 shrink-0" />
                                    {kp}
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}

                        {/* Entity Conflicts */}
                        {((entityAnalysis as any).entityConflicts || []).length > 0 && (
                          <div className="space-y-3">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Entity Conflicts Detected</span>
                            {((entityAnalysis as any).entityConflicts || []).map((conflict: any, i: number) => (
                              <div key={i} className="p-4 border border-amber-500/25 bg-amber-500/5 rounded-xl space-y-2">
                                <div className="flex items-center gap-2">
                                  <AlertCircle className="h-4 w-4 text-amber-500" />
                                  <span className="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wide">{conflict.entity_type} conflict</span>
                                </div>
                                <p className="text-xs text-foreground">{conflict.description}</p>
                                <div className="flex flex-wrap gap-2">
                                  {(conflict.values || []).map((v: string, vi: number) => (
                                    <span key={vi} className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-300 font-mono border border-amber-500/20">{v}</span>
                                  ))}
                                </div>
                                <p className="text-[10px] text-muted-foreground">Found on pages: {(conflict.pages || []).join(", ")}</p>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* SVG Relationship Graph */}
                        {(entityAnalysis.entities || []).length > 0 && (
                          <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3 shadow-xs">
                            <h4 className="text-sm font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-2">
                              <Network className="h-4.5 w-4.5" />
                              Entity Relationship Graph
                            </h4>
                            <p className="text-xs text-muted-foreground">
                              Visual map of co-occurrences and semantic relationships between top entities in the document text.
                            </p>
                            <div className="h-[320px] w-full border border-border rounded-xl bg-secondary/15 relative overflow-hidden flex items-center justify-center p-4">
                              <EntityRelationshipGraph entities={entityAnalysis.entities || []} />
                            </div>
                          </div>
                        )}

                        {/* Entity Cards */}
                        {(entityAnalysis.entities || []).length > 0 && (
                          <div className="space-y-3">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">{(entityAnalysis.entities || []).length} entities extracted</span>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              {(entityAnalysis.entities || []).map((entity) => {
                                const hasConflict = (entityAnalysis.entityConflicts || []).some((c: any) =>
                                  (c.values || []).some((v: string) => v.toLowerCase().trim() === entity.text.toLowerCase().trim())
                                );

                                return (
                                  <div key={entity.id} className="p-4 border border-card-border bg-card rounded-xl space-y-2.5 shadow-2xs hover:shadow-xs transition-all duration-200">
                                    <div className="flex items-center justify-between">
                                      <Badge className="text-[8px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-0">{entity.type}</Badge>
                                      <span className="text-[10px] text-muted-foreground font-mono">{Math.round(entity.confidence * 100)}% confidence</span>
                                    </div>
                                    <p className="text-sm font-semibold text-foreground">{entity.text}</p>
                                    
                                    {hasConflict && (
                                      <div className="flex items-center gap-1 text-[9px] text-amber-600 dark:text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 w-fit uppercase tracking-wider">
                                        <AlertCircle className="h-3 w-3" />
                                        Potential Conflict
                                      </div>
                                    )}

                                    <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                                      <span className="flex items-center gap-1"><BarChart2 className="h-3 w-3" />{entity.frequency || (entity.mentions || []).length || 1}× mentions</span>
                                      {(entity.mentions || []).length > 0 && (
                                        <span>Pages: {[...new Set((entity.mentions || []).map(m => m.page))].slice(0, 5).join(", ")}</span>
                                      )}
                                    </div>

                                    {entity.related_entities && (entity.related_entities || []).length > 0 && (
                                      <div className="pt-2 border-t border-border mt-2 space-y-1">
                                        <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Related Entities:</span>
                                        <div className="flex flex-wrap gap-1">
                                          {(entity.related_entities || []).map((rel: string, ri: number) => (
                                            <span key={ri} className="text-[9px] px-2 py-0.5 rounded-full bg-secondary text-muted-foreground font-medium border border-border">
                                              {rel}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Key-Value Pairs */}
                        {(entityAnalysis.keyValuePairs || []).length > 0 && (
                          <div className="space-y-3">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Key Facts Extracted</span>
                            <div className="space-y-1.5">
                              {(entityAnalysis.keyValuePairs || []).map((kv) => (
                                <div key={kv.id} className="flex items-center gap-3 p-3 border border-card-border bg-card rounded-xl text-xs">
                                  <span className="font-semibold text-foreground min-w-[120px]">{kv.key}</span>
                                  <span className="text-muted-foreground">→</span>
                                  <span className="text-foreground flex-1 font-mono">{kv.value}</span>
                                  <span className="text-[10px] text-muted-foreground">{Math.round(kv.confidence * 100)}%</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>

            ) : activeTab === "retrieval" ? (
              /* RETRIEVAL INSPECTOR PANEL */
              <div className="flex-1 flex flex-col min-h-0 bg-background select-text">
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                  <div className="max-w-4xl mx-auto space-y-8">
                    <div className="p-6 border border-card-border bg-card/60 rounded-2xl shadow-xs space-y-1">
                      <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                        <Network className="h-5 w-5 text-emerald-500" />
                        Retrieval Inspector
                      </h3>
                      <p className="text-xs text-muted-foreground">Per-message retrieval diagnostics showing which chunks were retrieved, semantic vs keyword scores, and query expansion.</p>
                    </div>

                    {Object.keys(retrievalDiagnosticsMap).length === 0 ? (
                      <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/10 rounded-2xl text-center space-y-4">
                        <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground">
                          <Network className="h-6 w-6" />
                        </div>
                        <div className="space-y-1">
                          <h4 className="text-sm font-bold text-foreground">No retrieval data yet</h4>
                          <p className="text-xs text-muted-foreground max-w-sm">Send a chat message and retrieval diagnostics will appear here automatically.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {/* Message selector */}
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(retrievalDiagnosticsMap).map(([msgId, diag]) => (
                            <button
                              key={msgId}
                              onClick={() => setSelectedDiagMsgId(msgId)}
                              className={cn(
                                "px-3 py-1.5 text-[10px] font-semibold rounded-xl border transition-all",
                                selectedDiagMsgId === msgId
                                  ? "bg-primary text-primary-foreground border-transparent"
                                  : "bg-card text-muted-foreground border-card-border hover:border-border"
                              )}
                            >
                              {diag.original_query.substring(0, 30)}{diag.original_query.length > 30 ? "..." : ""}
                            </button>
                          ))}
                        </div>

                        {/* Selected diagnostics */}
                        {selectedDiagMsgId && retrievalDiagnosticsMap[selectedDiagMsgId] && (() => {
                          const diag = retrievalDiagnosticsMap[selectedDiagMsgId];
                          return (
                            <div className="space-y-5">
                              {/* Query comparison */}
                              <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3 shadow-xs">
                                <div className="space-y-2">
                                  <div className="flex items-start gap-2">
                                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider w-28 shrink-0 mt-0.5">Original Query</span>
                                    <span className="text-xs text-foreground font-medium">{diag.original_query}</span>
                                  </div>
                                  {diag.expanded_query && (
                                    <div className="flex items-start gap-2">
                                      <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider w-28 shrink-0 mt-0.5">Expanded Query</span>
                                      <span className="text-xs text-foreground font-medium">{diag.expanded_query}</span>
                                    </div>
                                  )}
                                  <div className="flex items-center gap-2">
                                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider w-28 shrink-0">Chunks Retrieved</span>
                                    <span className="text-xs font-mono text-primary">{diag.retrieval_count}</span>
                                  </div>
                                </div>
                              </div>

                              {/* Chunk score cards */}
                              <div className="space-y-3">
                                {diag.chunks.map((chunk, i) => (
                                  <div key={i} className="p-4 border border-card-border bg-card rounded-xl shadow-2xs space-y-3">
                                    <div className="flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">Chunk #{i + 1}</span>
                                        <span className="text-[9px] text-muted-foreground">· {chunk.document_name} · Page {chunk.page}</span>
                                      </div>
                                      <span className="text-[10px] font-mono font-bold text-primary bg-primary/5 px-2 py-0.5 rounded-full">{(chunk.hybrid_score * 100).toFixed(1)}%</span>
                                    </div>
                                    <p className="text-xs text-muted-foreground italic leading-relaxed">&ldquo;{chunk.preview}&rdquo;</p>
                                    {/* Score bars */}
                                    <div className="space-y-1.5">
                                      <div className="flex items-center gap-3 text-[10px]">
                                        <span className="text-muted-foreground w-24">Semantic</span>
                                        <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                                          <motion.div 
                                            initial={{ width: 0 }}
                                            animate={{ width: `${chunk.semantic_score * 100}%` }}
                                            transition={{ duration: 0.8, ease: "easeOut" }}
                                            className="h-full bg-indigo-500 rounded-full" 
                                          />
                                        </div>
                                        <span className="text-muted-foreground font-mono w-10 text-right">{(chunk.semantic_score * 100).toFixed(0)}%</span>
                                      </div>
                                      <div className="flex items-center gap-3 text-[10px]">
                                        <span className="text-muted-foreground w-24">Keyword (BM25)</span>
                                        <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                                          <motion.div 
                                            initial={{ width: 0 }}
                                            animate={{ width: `${chunk.keyword_score * 100}%` }}
                                            transition={{ duration: 0.8, ease: "easeOut" }}
                                            className="h-full bg-emerald-500 rounded-full" 
                                          />
                                        </div>
                                        <span className="text-muted-foreground font-mono w-10 text-right">{(chunk.keyword_score * 100).toFixed(0)}%</span>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}
                  </div>
                </div>
              </div>

            ) : activeTab === "diagnostics" ? (
              /* SYSTEM DIAGNOSTICS PANEL */
              <div className="flex-1 flex flex-col min-h-0 bg-background select-text">
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                  <div className="max-w-4xl mx-auto space-y-8">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border border-card-border bg-card/60 rounded-2xl shadow-xs">
                      <div className="space-y-1">
                        <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                          <HeartPulse className="h-5 w-5 text-rose-500" />
                          System Diagnostics
                        </h3>
                        <p className="text-xs text-muted-foreground">Live status of all infrastructure components powering DocuMind AI.</p>
                      </div>
                      <Button
                        onClick={async () => {
                          setIsLoadingHealth(true);
                          try {
                            const status = await sdk.getHealth();
                            setHealthStatus(status);
                            addLog("SUCCESS", `Health check complete. Status: ${status.status}`);
                          } catch (err: any) {
                            addLog("ERROR", `Health check failed: ${err.message}`);
                          } finally {
                            setIsLoadingHealth(false);
                          }
                        }}
                        disabled={isLoadingHealth}
                        className="bg-primary hover:bg-primary/95 text-primary-foreground font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-primary/10"
                      >
                        {isLoadingHealth ? (
                          <><Loader2 className="h-3 w-3 animate-spin" />Checking...</>
                        ) : (
                          <><HeartPulse className="h-3 w-3" />Run Health Check</>
                        )}
                      </Button>
                    </div>

                    {!healthStatus && !isLoadingHealth && (
                      <div className="flex flex-col items-center justify-center p-16 border border-dashed border-border bg-card/10 rounded-2xl text-center space-y-4">
                        <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground">
                          <HeartPulse className="h-6 w-6" />
                        </div>
                        <h4 className="text-sm font-bold text-foreground">No diagnostics run yet</h4>
                        <p className="text-xs text-muted-foreground max-w-sm">Click Run Health Check to verify all infrastructure components.</p>
                      </div>
                    )}

                    {healthStatus && (
                      <div className="space-y-6">
                        {/* Overall status */}
                        <div className={cn(
                          "flex items-center gap-3 p-4 rounded-2xl border",
                          healthStatus.status === "healthy"
                            ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-700 dark:text-emerald-400"
                            : "bg-amber-500/5 border-amber-500/20 text-amber-700 dark:text-amber-400"
                        )}>
                          {healthStatus.status === "healthy" ? (
                            <CheckCircle2 className="h-5 w-5" />
                          ) : (
                            <AlertCircle className="h-5 w-5" />
                          )}
                          <span className="font-bold text-sm capitalize">{healthStatus.status}</span>
                          <span className="text-xs opacity-75 ml-1">— {healthStatus.service}</span>
                        </div>

                        {/* Component cards */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {([
                            { label: "PostgreSQL", value: healthStatus.postgres, icon: <Database className="h-4 w-4 text-indigo-500" /> },
                            { label: "Chroma Vector DB", value: `${healthStatus.chroma} (${healthStatus.chroma_backend})`, icon: <Brain className="h-4 w-4 text-primary" /> },
                            { label: "Embedding Provider", value: healthStatus.embedding_provider, icon: <Cpu className="h-4 w-4 text-amber-500" /> },
                            { label: "Collections", value: `${healthStatus.chroma_collection_count} collection(s)`, icon: <BarChart2 className="h-4 w-4 text-emerald-500" /> },
                          ]).map(({ label, value, icon }) => (
                            <div key={label} className="p-4 border border-card-border bg-card rounded-xl shadow-2xs flex items-start gap-3">
                              <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                                {icon}
                              </div>
                              <div>
                                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">{label}</span>
                                <span className="text-xs font-semibold text-foreground block mt-0.5">{value}</span>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* LLM Providers */}
                        <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3">
                          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Active LLM Providers</span>
                          <div className="flex flex-wrap gap-2">
                            {healthStatus.llm_providers.map(p => (
                              <span key={p} className="text-xs px-3 py-1 rounded-full border border-card-border bg-secondary/50 text-foreground font-medium">
                                {p}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

            ) : activeTab === "testlab" ? (
              /* TEST LAB PANEL */
              <div className="flex-1 flex flex-col min-h-0 bg-background select-text">
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                  <div className="max-w-4xl mx-auto space-y-8">
                    {/* Header card */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border border-card-border bg-card/60 rounded-2xl shadow-xs">
                      <div className="space-y-1">
                        <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                          <Cpu className="h-5 w-5 text-violet-500" />
                          Validation Suite & Test Lab
                        </h3>
                        <p className="text-xs text-muted-foreground text-left">
                          Run a comprehensive system-level validation harness checking functional metrics, security controls, and tenant isolation.
                        </p>
                      </div>
                      <Button
                        onClick={async () => {
                          setIsRunningSuite(true);
                          setSuiteLogs(["[Suite] Booting test harness...", "[Suite] Provisioning sandbox workspaces..."]);
                          try {
                            const res = await sdk.runValidationSuite();
                            setValidationReport(res);
                            setSuiteLogs(prev => [
                              ...prev,
                              `[Suite] Finished validation suite in ${res.summary.elapsed_ms}ms.`,
                              `[Suite] Result: ${res.summary.status} (${res.summary.passed}/${res.summary.total_tests} assertions passed)`
                            ]);
                            addLog("SUCCESS", `Validation suite completed: ${res.summary.status}`);
                          } catch (err: any) {
                            setSuiteLogs(prev => [...prev, `[ERROR] Validation suite crashed: ${err.message}`]);
                            addLog("ERROR", `Validation suite failed: ${err.message}`);
                          } finally {
                            setIsRunningSuite(false);
                          }
                        }}
                        disabled={isRunningSuite}
                        className="bg-primary hover:bg-primary/95 text-primary-foreground font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-primary/10 shrink-0"
                      >
                        {isRunningSuite ? (
                          <><Loader2 className="h-3 w-3 animate-spin" />Running Suite...</>
                        ) : (
                          <><Cpu className="h-3 w-3" />Run Validation Suite</>
                        )}
                      </Button>
                    </div>

                    {/* Report Summary */}
                    {validationReport && (
                      <div className="space-y-8 animate-fade-in text-left">
                        {/* Summary metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="p-4 border border-card-border bg-card rounded-xl shadow-2xs">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Suite Result</span>
                            <span className={cn("text-lg font-extrabold mt-1 block", {
                              "text-emerald-500": validationReport.summary.status === "PASS",
                              "text-rose-500": validationReport.summary.status === "FAIL"
                            })}>
                              {validationReport.summary.status}
                            </span>
                          </div>
                          <div className="p-4 border border-card-border bg-card rounded-xl shadow-2xs">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Passed Tests</span>
                            <span className="text-lg font-bold text-foreground mt-1 block font-sans">
                              {validationReport.summary.passed} / {validationReport.summary.total_tests}
                            </span>
                          </div>
                          <div className="p-4 border border-card-border bg-card rounded-xl shadow-2xs">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Failed Tests</span>
                            <span className="text-lg font-bold text-foreground mt-1 block font-sans">
                              {validationReport.summary.failed}
                            </span>
                          </div>
                          <div className="p-4 border border-card-border bg-card rounded-xl shadow-2xs">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Execution Latency</span>
                            <span className="text-lg font-bold text-foreground mt-1 block font-sans">
                              {validationReport.summary.elapsed_ms} ms
                            </span>
                          </div>
                        </div>

                        {/* Test Packs breakdown */}
                        <div className="space-y-4">
                          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Test Packs Matrix</span>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(validationReport.test_packs).map(([level, pack]: [string, any]) => (
                              <div key={level} className="p-5 border border-card-border bg-card rounded-2xl shadow-2xs space-y-4">
                                <div className="flex items-center justify-between">
                                  <h4 className="text-sm font-bold text-foreground capitalize flex items-center gap-1.5 font-sans">
                                    <Sparkles className="h-4 w-4 text-primary" />
                                    {level} Test Pack
                                  </h4>
                                  <Badge variant={pack.status === "PASS" ? "success" : "error"} className="rounded-full px-2 py-0.5 text-[9px] font-bold">
                                    {pack.status}
                                  </Badge>
                                </div>
                                
                                <div className="space-y-2 text-xs border-b border-border/40 pb-3">
                                  <div className="flex justify-between text-muted-foreground">
                                    <span>Contradictions Found:</span>
                                    <span className="font-bold text-foreground font-sans">{pack.metrics.contradictions_found}</span>
                                  </div>
                                  <div className="flex justify-between text-muted-foreground">
                                    <span>Requirements Traced:</span>
                                    <span className="font-bold text-foreground font-sans">{pack.metrics.requirements_traced.length}</span>
                                  </div>
                                  <div className="flex justify-between text-muted-foreground">
                                    <span>Trust Score:</span>
                                    <span className="font-bold text-foreground font-sans">{pack.metrics.trust_score.toFixed(1)}%</span>
                                  </div>
                                  {pack.metrics.entities_extracted.length > 0 && (
                                    <div className="text-muted-foreground mt-1">
                                      <span>Entities: </span>
                                      <span className="font-semibold text-foreground text-[10px] bg-secondary/80 py-0.5 px-1.5 rounded">{pack.metrics.entities_extracted.slice(0,3).join(", ")}</span>
                                    </div>
                                  )}
                                </div>

                                <div className="space-y-1.5 text-left">
                                  {pack.assertions.map((a: any, idx: number) => (
                                    <div key={idx} className="flex items-center gap-2 text-xs">
                                      {a.status === "PASS" ? (
                                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                                      ) : (
                                        <XCircle className="h-3.5 w-3.5 text-rose-500 shrink-0" />
                                      )}
                                      <span className={a.status === "PASS" ? "text-foreground font-sans font-medium" : "text-rose-500 font-semibold"}>
                                        {a.name}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Security, isolation & retrieval */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {([
                            { title: "Retrieval Integrity", data: validationReport.retrieval, icon: <Search className="h-4 w-4 text-emerald-500" /> },
                            { title: "Tenant Isolation", data: validationReport.isolation, icon: <Shield className="h-4 w-4 text-sky-500" /> },
                            { title: "Security Enforcement", data: validationReport.security, icon: <Lock className="h-4 w-4 text-violet-500" /> }
                          ] as any[]).map((col, idx) => (
                            <div key={idx} className="p-4 border border-card-border bg-card rounded-xl shadow-2xs space-y-3">
                              <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
                                {col.icon}
                                {col.title}
                              </h4>
                              <div className="space-y-2">
                                {col.data.assertions.map((a: any, idx: number) => (
                                  <div key={idx} className="text-xs space-y-1">
                                    <div className="flex items-center gap-1.5">
                                      {a.status === "PASS" ? (
                                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                                      ) : (
                                        <XCircle className="h-3.5 w-3.5 text-rose-500 shrink-0" />
                                      )}
                                      <span className="font-semibold text-foreground leading-none">{a.status}</span>
                                    </div>
                                    <p className="text-[10px] text-muted-foreground pl-5 leading-normal">{a.name}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Suit logs / console */}
                    <div className="p-5 border border-card-border bg-card rounded-2xl text-left space-y-3 shadow-sm">
                      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Suite Execution Logs</span>
                      <div className="bg-black/5 dark:bg-black/20 font-mono text-[10px] p-4 rounded-xl max-h-48 overflow-y-auto space-y-1 scrollbar-thin select-all border border-border/30">
                        {suiteLogs.length === 0 ? (
                          <span className="text-muted-foreground">Test suite idle. Click &quot;Run Validation Suite&quot; to begin.</span>
                        ) : (
                          suiteLogs.map((log, idx) => (
                            <div key={idx} className={cn("whitespace-pre-wrap", {
                              "text-rose-500 font-semibold": log.startsWith("[ERROR]"),
                              "text-emerald-500 font-semibold": log.includes("Result: PASS") || log.includes("SUCCESS"),
                              "text-muted-foreground": !log.startsWith("[ERROR]") && !log.includes("Result: PASS")
                            })}>
                              {log}
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              ) : null}
            </div>
          ) : (
            /* CODER VIBE WELCOME DECK (EDITORIAL REDESIGN) */
            <div className="flex-1 overflow-y-auto p-8 space-y-10">
              <div className="max-w-4xl mx-auto space-y-10">
                
                <div className="relative border border-card-border bg-card rounded-2xl p-8 overflow-hidden shadow-xs">
                  <div className="absolute top-0 right-0 h-full w-[350px] bg-gradient-to-l from-primary/5 to-transparent pointer-events-none" />
                  <div className="relative space-y-4 z-10">
                    <div className="flex items-center gap-2 text-xs font-semibold text-primary uppercase tracking-wider">
                      <Sparkles className="h-4 w-4" />
                      Semantic Intelligence Hub
                    </div>
                    <h2 className="text-3xl font-extrabold text-foreground tracking-tight">
                      Document Intelligence Platform
                    </h2>
                    <p className="text-sm text-muted-foreground max-w-2xl leading-relaxed">
                      Analyze, extract, and converse with multiple document datasets. DocuMind indexes text vectors to provide secure, cross-source RAG insights and reasoning capabilities.
                    </p>
                  </div>
                </div>

                {/* Workspace Statistics Widgets */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                    Workspace Statistics
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <Card className="bg-card border-card-border rounded-2xl shadow-2xs hover:shadow-xs transition-all duration-200">
                      <CardContent className="p-5 flex items-center gap-4">
                        <div className="h-11 w-11 flex items-center justify-center rounded-xl bg-primary/10 text-primary">
                          <Database className="h-5.5 w-5.5" />
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground font-medium block leading-none">Indexed sources</span>
                          <span className="text-xl font-bold text-foreground block mt-1.5 font-sans">
                            {processedDocsCount} / {documents.length} files
                          </span>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-card border-card-border rounded-2xl shadow-2xs hover:shadow-xs transition-all duration-200">
                      <CardContent className="p-5 flex items-center gap-4">
                        <div className="h-11 w-11 flex items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-500">
                          <FileText className="h-5.5 w-5.5" />
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground font-medium block leading-none">Index volume</span>
                          <span className="text-xl font-bold text-foreground block mt-1.5 font-sans">
                            {sizeFormatted} MB
                          </span>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-card border-card-border rounded-2xl shadow-2xs hover:shadow-xs transition-all duration-200">
                      <CardContent className="p-5 flex items-center gap-4">
                        <div className="h-11 w-11 flex items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
                          <Brain className="h-5.5 w-5.5" />
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground font-medium block leading-none">Selected LLM</span>
                          <span className="text-xl font-bold text-foreground block mt-1.5 font-sans uppercase">
                            {activeModel === "documind-v3" ? "RAG v3" : activeModel === "deepseek-r1" ? "DeepSeek R1" : "Claude 3.5"}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>

                {/* Error Banner */}
                {errorMsg && (
                  <div className="flex items-center gap-3 rounded-xl border border-destructive/20 bg-destructive/5 p-4 text-sm text-destructive">
                    <AlertCircle className="h-5 w-5 shrink-0" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                {/* Workflow guides (editorial column block) */}
                <div className="space-y-4">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                    Getting Started
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3 hover:shadow-2xs transition-all duration-200">
                      <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-secondary text-[10px] font-bold text-primary font-sans">
                        1
                      </div>
                      <h4 className="text-sm font-bold text-foreground">Ingest Knowledge</h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        Drag and drop your PDF, Word, or txt documents in the sidebar to extract semantic chunks and build vector embeddings.
                      </p>
                    </div>

                    <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3 hover:shadow-2xs transition-all duration-200">
                      <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-secondary text-[10px] font-bold text-primary font-sans">
                        2
                      </div>
                      <h4 className="text-sm font-bold text-foreground">Select Analysis Scope</h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        Select one or more documents from your active knowledge base. The AI will target its contextual analysis to these active documents.
                      </p>
                    </div>

                    <div className="p-5 border border-card-border bg-card rounded-2xl space-y-3 hover:shadow-2xs transition-all duration-200">
                      <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-secondary text-[10px] font-bold text-primary font-sans">
                        3
                      </div>
                      <h4 className="text-sm font-bold text-foreground">Start RAG Analysis</h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        Click compile to initialize a conversational context. Execute summaries or pose direct queries with precise source mapping.
                      </p>
                    </div>
                  </div>
                </div>

                {/* SDK Reference block */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                    Developer SDK Integration
                  </span>
                  <div className="p-5 border border-card-border bg-card rounded-2xl font-sans text-xs space-y-3.5 text-muted-foreground shadow-2xs">
                    <div className="flex items-center justify-between text-muted-foreground">
                      <span className="font-mono select-all p-1 bg-secondary/50 rounded border border-border/30">$ npm i @documind/sdk</span>
                      <button 
                        onClick={() => handleCopy("npm i @documind/sdk", "package")}
                        className="text-primary hover:text-primary/80 transition-all font-semibold flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary/50 border border-border/40 hover:bg-secondary"
                      >
                        {copiedPackage ? (
                          <span className="text-[10px] text-emerald-500 font-bold animate-pulse">Copied!</span>
                        ) : (
                          <span>Copy</span>
                        )}
                      </button>
                    </div>
                    <div className="border-t border-border pt-3.5 flex items-center justify-between">
                      <span className="font-mono select-all p-1 bg-secondary/50 rounded border border-border/30">const sdk = new DocuMindSDK(&#123; activeModel: &quot;{activeModel}&quot; &#125;)</span>
                      <button 
                        onClick={() => handleCopy(`const sdk = new DocuMindSDK({ activeModel: "${activeModel}" })`, "inst")}
                        className="text-primary hover:text-primary/80 transition-all font-semibold flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary/50 border border-border/40 hover:bg-secondary"
                      >
                        {copiedInst ? (
                          <span className="text-[10px] text-emerald-500 font-bold animate-pulse">Copied!</span>
                        ) : (
                          <span>Copy</span>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}
          
          {/* Collapsible Developer Console / Kernel Telemetry */}
          <div 
            className={cn(
              "border-t border-border bg-card/90 backdrop-blur-md transition-all duration-300 z-20 flex flex-col font-mono text-xs select-text",
              isConsoleOpen ? "h-64" : "h-9"
            )}
          >
            {/* Console Header Bar */}
            <div 
              onClick={() => setIsConsoleOpen(!isConsoleOpen)}
              className="h-9 px-4 border-b border-border/50 flex items-center justify-between cursor-pointer hover:bg-secondary/40 select-none"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] font-bold text-foreground uppercase tracking-wider">Kernel Console</span>
                <span className="text-[10px] text-muted-foreground font-normal">|</span>
                <span className="text-[10px] text-muted-foreground font-normal">
                  Chroma DB: Connected
                </span>
                <span className="text-[10px] text-muted-foreground font-normal">|</span>
                <span className="text-[10px] text-muted-foreground font-normal">
                  Provider: {activeModel === "deepseek-r1" ? "Groq / Llama" : "OpenAI"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[9px] text-muted-foreground font-semibold bg-secondary/80 px-2 py-0.5 rounded border border-border">
                  {systemLogs.length} logs
                </span>
                <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform duration-300", {
                  "transform rotate-180": isConsoleOpen
                })} />
              </div>
            </div>

            {/* Console Scroll Area */}
            {isConsoleOpen && (
              <div className="flex-1 overflow-y-auto p-3.5 space-y-1.5 bg-black/5 dark:bg-black/20 font-mono text-[10px] leading-relaxed">
                {systemLogs.map((log) => (
                  <div key={log.id} className="flex gap-2.5 items-start">
                    <span className="text-muted-foreground select-none shrink-0">[{log.time}]</span>
                    <span className={cn("font-bold shrink-0 uppercase tracking-tight select-none text-[9px] px-1 rounded", {
                      "text-sky-500 bg-sky-500/10 border border-sky-500/20": log.level === "INFO",
                      "text-emerald-500 bg-emerald-500/10 border border-emerald-500/20": log.level === "SUCCESS",
                      "text-amber-500 bg-amber-500/10 border border-amber-500/20": log.level === "WARN",
                      "text-rose-500 bg-rose-500/10 border border-rose-500/20": log.level === "ERROR",
                    })}>
                      {log.level}
                    </span>
                    <span className={cn("text-foreground whitespace-pre-wrap select-all", {
                      "text-rose-600 dark:text-rose-400 font-semibold": log.level === "ERROR",
                      "text-emerald-600 dark:text-emerald-400": log.level === "SUCCESS",
                    })}>
                      {log.message}
                    </span>
                  </div>
                ))}
                <div id="console-bottom" />
              </div>
            )}
          </div>
        </main>

        {/* Command Palette Overlay */}
        <CommandPalette
          isOpen={isCommandPaletteOpen}
          onClose={() => setIsCommandPaletteOpen(false)}
          items={commandItems}
        />

        {/* Workspace Management Modal */}
        <Modal isOpen={isWorkspaceModalOpen} onOpenChange={setIsWorkspaceModalOpen}>
          <ModalContent className="max-w-2xl bg-card border-card-border shadow-xl rounded-2xl p-6 text-foreground">
            <ModalHeader>
              <ModalTitle className="text-lg font-bold flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-primary" />
                Workspace & Organization Management
              </ModalTitle>
              <ModalDescription className="text-xs text-muted-foreground">
                Manage workspaces, user organizations, access control roles, and review workspace audit history.
              </ModalDescription>
            </ModalHeader>

            {/* Tab navigation */}
            <div className="flex border-b border-border my-4 gap-2">
              <button
                onClick={() => setWsModalTab("workspaces")}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 transition-all",
                  wsModalTab === "workspaces"
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                )}
              >
                <GitBranch className="h-3.5 w-3.5" />
                Workspaces
              </button>
              <button
                onClick={() => setWsModalTab("orgs")}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 transition-all",
                  wsModalTab === "orgs"
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                )}
              >
                <Users className="h-3.5 w-3.5" />
                Organizations
              </button>
              <button
                onClick={() => setWsModalTab("members")}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 transition-all",
                  wsModalTab === "members"
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                )}
              >
                <Shield className="h-3.5 w-3.5" />
                Org Members
              </button>
              <button
                onClick={() => setWsModalTab("audit")}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 transition-all",
                  wsModalTab === "audit"
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                )}
              >
                <Activity className="h-3.5 w-3.5" />
                Audit Logs
              </button>
            </div>

            <div className="space-y-5 text-left min-h-[300px]">
              {wsModalTab === "workspaces" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Creation Form */}
                  <form 
                    onSubmit={async (e) => {
                      e.preventDefault();
                      if (!newWorkspaceName.trim() || isWorkspaceSubmitting) return;
                      setIsWorkspaceSubmitting(true);
                      try {
                        addLog("INFO", `Creating workspace: ${newWorkspaceName}`);
                        const orgId = selectedOrgId === "personal" ? undefined : selectedOrgId;
                        await createWorkspace(newWorkspaceName.trim(), newWorkspaceDesc.trim() || undefined, orgId);
                        setNewWorkspaceName("");
                        setNewWorkspaceDesc("");
                        addLog("SUCCESS", `Workspace created successfully.`);
                      } catch (err: any) {
                        addLog("ERROR", `Failed to create workspace: ${err.message}`);
                        handleRateLimitError(err);
                      } finally {
                        setIsWorkspaceSubmitting(false);
                      }
                    }}
                    className="space-y-3 p-4 bg-secondary/20 rounded-xl border border-border/50 h-fit"
                  >
                    <h3 className="text-xs font-bold text-foreground uppercase tracking-wider block">
                      Create Workspace
                    </h3>
                    <div className="space-y-2.5">
                      <Input 
                        placeholder="Workspace Name (e.g. Finance Hub)" 
                        value={newWorkspaceName}
                        onChange={(e) => setNewWorkspaceName(e.target.value)}
                        required
                        className="text-xs py-2 px-3 bg-card border-border hover:border-primary/30 focus:border-primary transition-all duration-200"
                      />
                      <Input 
                        placeholder="Description (Optional)" 
                        value={newWorkspaceDesc}
                        onChange={(e) => setNewWorkspaceDesc(e.target.value)}
                        className="text-xs py-2 px-3 bg-card border-border hover:border-primary/30 focus:border-primary transition-all duration-200"
                      />
                      <div className="space-y-1">
                        <label className="text-[10px] font-bold text-muted-foreground uppercase">Assign Organization</label>
                        <select
                          value={selectedOrgId}
                          onChange={(e) => setSelectedOrgId(e.target.value)}
                          className="w-full text-xs py-2 px-3 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:border-primary transition-all"
                        >
                          <option value="personal">Personal Workspace (No Org)</option>
                          {organizations.map(org => (
                            <option key={org.id} value={org.id}>{org.name}</option>
                          ))}
                        </select>
                      </div>
                      <Button 
                        type="submit" 
                        disabled={isWorkspaceSubmitting || !newWorkspaceName.trim()}
                        className="w-full text-xs font-semibold py-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground shadow-sm transition-all"
                      >
                        {isWorkspaceSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin mx-auto" /> : "Create Workspace"}
                      </Button>
                    </div>
                  </form>

                  {/* Active Workspaces List */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
                      Existing Workspaces
                    </h3>
                    <div className="max-h-[300px] overflow-y-auto space-y-1.5 pr-1 scrollbar-thin">
                      {workspaces.map((ws) => {
                        const isActive = ws.id === activeWorkspaceId;
                        const isConfirmingDelete = isDeletingWorkspaceId === ws.id;
                        const wsOrg = organizations.find(o => o.id === ws.organization_id);
                        return (
                          <div 
                            key={ws.id}
                            className={cn(
                              "flex items-center justify-between p-2.5 rounded-xl border transition-all duration-200 text-xs",
                              isActive 
                                ? "bg-primary/5 border-primary/30 text-foreground font-bold" 
                                : "bg-card border-card-border hover:border-border text-muted-foreground hover:text-foreground"
                            )}
                          >
                            <div className="overflow-hidden pr-2">
                              <p className="font-semibold text-foreground truncate">{ws.name}</p>
                              <p className="text-[9px] text-muted-foreground truncate">
                                {wsOrg ? `Org: ${wsOrg.name}` : "Personal"} {ws.description ? `· ${ws.description}` : ""}
                              </p>
                            </div>

                            <div className="flex items-center gap-2 shrink-0">
                              {isActive && <Badge variant="outline" className="text-[9px] bg-primary/10 text-primary border-primary/20 rounded-full scale-90 px-1.5 py-0.5">Active</Badge>}
                              
                              {isConfirmingDelete ? (
                                <div className="flex items-center gap-1.5">
                                  <Button 
                                    size="sm" 
                                    variant="outline" 
                                    onClick={() => setIsDeletingWorkspaceId(null)}
                                    className="h-6 text-[10px] px-2 rounded-md border-border bg-card text-muted-foreground hover:text-foreground animate-fade-in"
                                  >
                                    Cancel
                                  </Button>
                                  <Button 
                                    size="sm" 
                                    className="h-6 text-[10px] px-2 rounded-md bg-destructive hover:bg-destructive/95 text-destructive-foreground animate-fade-in"
                                    onClick={async () => {
                                      try {
                                        addLog("INFO", `Deleting workspace: ${ws.name}`);
                                        await useWorkspaceStore.getState().deleteWorkspace(ws.id);
                                        setIsDeletingWorkspaceId(null);
                                        addLog("SUCCESS", `Workspace deleted successfully.`);
                                      } catch (err: any) {
                                        addLog("ERROR", `Failed to delete workspace: ${err.message}`);
                                        handleRateLimitError(err);
                                      }
                                    }}
                                  >
                                    Confirm
                                  </Button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => setIsDeletingWorkspaceId(ws.id)}
                                  className="h-6 w-6 flex items-center justify-center rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors duration-200"
                                  title="Delete Workspace"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {wsModalTab === "orgs" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Create Org Form */}
                  <form
                    onSubmit={async (e) => {
                      e.preventDefault();
                      if (!newOrgName.trim() || isOrgSubmitting) return;
                      setIsOrgSubmitting(true);
                      try {
                        addLog("INFO", `Creating organization: ${newOrgName}`);
                        const org = await sdk.createOrganization(newOrgName.trim());
                        setNewOrgName("");
                        const updatedOrgs = await sdk.listOrganizations();
                        setOrganizations(updatedOrgs);
                        addLog("SUCCESS", `Organization '${org.name}' created.`);
                      } catch (err: any) {
                        addLog("ERROR", `Failed to create organization: ${err.message}`);
                        handleRateLimitError(err);
                      } finally {
                        setIsOrgSubmitting(false);
                      }
                    }}
                    className="space-y-3 p-4 bg-secondary/20 rounded-xl border border-border/50 h-fit"
                  >
                    <h3 className="text-xs font-bold text-foreground uppercase tracking-wider block">
                      Create Organization
                    </h3>
                    <div className="space-y-2.5">
                      <Input 
                        placeholder="Organization Name (e.g. Acme Corp)" 
                        value={newOrgName}
                        onChange={(e) => setNewOrgName(e.target.value)}
                        required
                        className="text-xs py-2 px-3 bg-card border-border hover:border-primary/30 focus:border-primary transition-all duration-200"
                      />
                      <Button 
                        type="submit" 
                        disabled={isOrgSubmitting || !newOrgName.trim()}
                        className="w-full text-xs font-semibold py-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground shadow-sm transition-all"
                      >
                        {isOrgSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin mx-auto" /> : "Create Organization"}
                      </Button>
                    </div>
                  </form>

                  {/* Orgs List */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
                      My Organizations
                    </h3>
                    <div className="max-h-[300px] overflow-y-auto space-y-1.5 pr-1 scrollbar-thin">
                      {organizations.length === 0 ? (
                        <p className="text-xs text-muted-foreground p-3 border border-dashed rounded-xl text-center">No organizations joined yet.</p>
                      ) : (
                        organizations.map((org) => (
                          <div 
                            key={org.id}
                            className="flex items-center justify-between p-3 rounded-xl border border-card-border bg-card text-xs text-foreground"
                          >
                            <div>
                              <p className="font-semibold">{org.name}</p>
                              <p className="text-[9px] text-muted-foreground font-mono truncate max-w-[180px]">ID: {org.id}</p>
                            </div>
                            <Badge variant="outline" className="text-[9px] bg-secondary text-muted-foreground border-border rounded-full scale-90 px-1.5 py-0.5">Org</Badge>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}

              {wsModalTab === "members" && (
                <div className="space-y-4">
                  {/* Select Org Header */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3 bg-secondary/20 rounded-xl border border-border/50">
                    <div className="space-y-0.5">
                      <label className="text-[9px] font-bold text-muted-foreground uppercase">Organization Context</label>
                      <select
                        value={selectedOrgId}
                        onChange={(e) => handleOrgChange(e.target.value)}
                        className="text-xs py-1.5 px-3 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:border-primary transition-all font-semibold"
                      >
                        <option value="" disabled>Select an Organization</option>
                        {organizations.map(org => (
                          <option key={org.id} value={org.id}>{org.name}</option>
                        ))}
                      </select>
                    </div>

                    {selectedOrgId && selectedOrgId !== "personal" && (
                      <form
                        onSubmit={async (e) => {
                          e.preventDefault();
                          if (!inviteUserId.trim()) return;
                          try {
                            addLog("INFO", `Inviting user ${inviteUserId} as ${inviteRole}`);
                            await sdk.addOrganizationMember(selectedOrgId, inviteUserId.trim(), inviteRole);
                            setInviteUserId("");
                            const updatedMembers = await sdk.listOrganizationMembers(selectedOrgId);
                            setOrgMembers(updatedMembers);
                            addLog("SUCCESS", `User invited successfully.`);
                          } catch (err: any) {
                            addLog("ERROR", `Failed to invite member: ${err.message}`);
                            handleRateLimitError(err);
                          }
                        }}
                        className="flex flex-wrap items-end gap-2"
                      >
                        <div className="space-y-0.5">
                          <label className="text-[9px] font-bold text-muted-foreground uppercase block">User ID</label>
                          <Input
                            placeholder="user-id"
                            value={inviteUserId}
                            onChange={(e) => setInviteUserId(e.target.value)}
                            required
                            className="text-xs py-1 px-2.5 bg-card border-border hover:border-primary/20 focus:border-primary w-28 h-8"
                          />
                        </div>
                        <div className="space-y-0.5">
                          <label className="text-[9px] font-bold text-muted-foreground uppercase block">Role</label>
                          <select
                            value={inviteRole}
                            onChange={(e) => setInviteRole(e.target.value)}
                            className="text-xs py-1 px-2.5 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:border-primary h-8"
                          >
                            <option value="viewer">Viewer</option>
                            <option value="member">Member</option>
                            <option value="admin">Admin</option>
                          </select>
                        </div>
                        <Button type="submit" size="sm" className="h-8 text-[11px] bg-primary text-primary-foreground font-semibold px-3.5 rounded-lg shadow-sm">
                          Invite
                        </Button>
                      </form>
                    )}
                  </div>

                  {/* Members list */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
                      Organization Members
                    </h3>
                    <div className="max-h-[220px] overflow-y-auto space-y-1.5 pr-1 scrollbar-thin">
                      {!selectedOrgId || selectedOrgId === "personal" ? (
                        <p className="text-xs text-muted-foreground p-4 border border-dashed rounded-xl text-center">Select an organization to manage members.</p>
                      ) : orgMembers.length === 0 ? (
                        <p className="text-xs text-muted-foreground p-4 border border-dashed rounded-xl text-center">No members listed.</p>
                      ) : (
                        orgMembers.map((member) => (
                          <div 
                            key={member.user_id}
                            className="flex items-center justify-between p-3 rounded-xl border border-card-border bg-card text-xs text-foreground"
                          >
                            <div>
                              <p className="font-semibold">User: {member.user_name || member.user_email || member.user_id}</p>
                              <p className="text-[9px] text-muted-foreground font-mono">ID: {member.user_id}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              {member.user_id === user.id ? (
                                <Badge variant="outline" className="text-[9px] bg-secondary text-primary border-primary/20 rounded-full scale-90 px-1.5 py-0.5 uppercase tracking-wide font-bold">{member.role}</Badge>
                              ) : (
                                <select
                                  value={member.role}
                                  onChange={async (e) => {
                                    const newRole = e.target.value;
                                    try {
                                      addLog("INFO", `Changing member role for ${member.user_id} to ${newRole}`);
                                      await sdk.updateOrganizationMemberRole(selectedOrgId, member.user_id, newRole);
                                      const updatedMembers = await sdk.listOrganizationMembers(selectedOrgId);
                                      setOrgMembers(updatedMembers);
                                      addLog("SUCCESS", `Updated member role.`);
                                    } catch (err: any) {
                                      addLog("ERROR", `Failed to update member role: ${err.message}`);
                                      handleRateLimitError(err);
                                    }
                                  }}
                                  className="text-xs bg-card border border-border rounded-lg text-foreground focus:outline-none focus:border-primary py-0.5 px-1.5"
                                >
                                  <option value="viewer">Viewer</option>
                                  <option value="member">Member</option>
                                  <option value="admin">Admin</option>
                                </select>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}

              {wsModalTab === "audit" && (
                <div className="space-y-4">
                  {/* Select Workspace Header */}
                  <div className="flex items-center justify-between p-3 bg-secondary/20 rounded-xl border border-border/50">
                    <div className="space-y-0.5">
                      <label className="text-[9px] font-bold text-muted-foreground uppercase">Workspace Context</label>
                      <select
                        value={auditSelectedWorkspaceId}
                        onChange={(e) => handleAuditWorkspaceChange(e.target.value)}
                        className="text-xs py-1.5 px-3 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:border-primary transition-all font-semibold"
                      >
                        <option value="" disabled>Select Workspace</option>
                        {workspaces.map(ws => (
                          <option key={ws.id} value={ws.id}>{ws.name}</option>
                        ))}
                      </select>
                    </div>
                    
                    <Badge variant="outline" className="text-[9px] bg-secondary text-muted-foreground border-border rounded-full py-0.5 px-2 font-mono">
                      {workspaceAuditLogs.length} logs
                    </Badge>
                  </div>

                  {/* Audit Logs list */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
                      Workspace Action History
                    </h3>
                    <div className="max-h-[260px] overflow-y-auto space-y-2 pr-1 scrollbar-thin">
                      {!auditSelectedWorkspaceId ? (
                        <p className="text-xs text-muted-foreground p-4 border border-dashed rounded-xl text-center">Select a workspace to view its audit logs.</p>
                      ) : workspaceAuditLogs.length === 0 ? (
                        <p className="text-xs text-muted-foreground p-4 border border-dashed rounded-xl text-center">No action logs found for this workspace. Actions like document upload or search will appear here.</p>
                      ) : (
                        workspaceAuditLogs.map((log) => {
                          const logTime = new Date(log.timestamp).toLocaleString();
                          return (
                            <div 
                              key={log.id}
                              className="p-3 border border-card-border bg-card rounded-xl text-xs space-y-1.5 text-left shadow-2xs"
                            >
                              <div className="flex items-center justify-between">
                                <span className={cn("text-[9px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider", {
                                  "bg-emerald-500/10 text-emerald-600 border-emerald-500/20": log.action.includes("create") || log.action.includes("upload"),
                                  "bg-rose-500/10 text-rose-600 border-rose-500/20": log.action.includes("delete"),
                                  "bg-amber-500/10 text-amber-600 border-amber-500/20": log.action.includes("update") || log.action.includes("rename"),
                                  "bg-blue-500/10 text-blue-600 border-blue-500/20": !log.action.includes("create") && !log.action.includes("delete") && !log.action.includes("update")
                                })}>
                                  {log.action}
                                </span>
                                <span className="text-[10px] text-muted-foreground font-mono">{logTime}</span>
                              </div>
                              <p className="text-foreground leading-relaxed font-semibold">{log.details}</p>
                              <div className="flex items-center gap-4 text-[9px] text-muted-foreground pt-1 border-t border-border/30">
                                <span>User: <strong className="text-foreground">{log.user_name || log.user_id}</strong></span>
                                {log.ip_address && <span>IP: <strong className="text-foreground font-mono">{log.ip_address}</strong></span>}
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <ModalFooter className="mt-4 pt-3 border-t border-border/40 flex justify-end">
              <Button 
                onClick={() => setIsWorkspaceModalOpen(false)}
                className="text-xs font-semibold py-2 px-4 rounded-lg bg-secondary hover:bg-secondary-hover border border-border text-foreground transition-all"
              >
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </div>
    </div>
  );
}
