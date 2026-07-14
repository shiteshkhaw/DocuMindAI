"use client";

import * as React from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Search } from "lucide-react";
import { cn } from "../utils/cn.js";

export interface CommandItem {
  id: string;
  title: string;
  description?: string;
  category: string;
  icon?: React.ReactNode;
  shortcut?: string[];
  onSelect: () => void;
}

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  items: CommandItem[];
  placeholder?: string;
}

const SafePortal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);
  if (!mounted) return null;
  return createPortal(children, document.body);
};

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  items,
  placeholder = "Search commands, actions, or documents...",
}) => {
  const [search, setSearch] = React.useState("");
  const [selectedIndex, setSelectedIndex] = React.useState(0);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Filter items
  const filteredItems = React.useMemo(() => {
    if (!search.trim()) return items;
    const query = search.toLowerCase();
    return items.filter(
      (item) =>
        item.title.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query),
    );
  }, [items, search]);

  // Reset index on search change
  React.useEffect(() => {
    setSelectedIndex(0);
  }, [search]);

  // Focus input when opened
  React.useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
      document.body.style.overflow = "hidden";
    } else {
      setSearch("");
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  // Keyboard navigation
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          filteredItems.length === 0 ? 0 : (prev + 1) % filteredItems.length,
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          filteredItems.length === 0 ? 0 : (prev - 1 + filteredItems.length) % filteredItems.length,
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filteredItems[selectedIndex]) {
          filteredItems[selectedIndex].onSelect();
          onClose();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, filteredItems, selectedIndex, onClose]);

  // Group filtered items by category
  const categories = React.useMemo(() => {
    const map: Record<string, typeof filteredItems> = {};
    filteredItems.forEach((item) => {
      if (!map[item.category]) {
        map[item.category] = [];
      }
      map[item.category].push(item);
    });
    return map;
  }, [filteredItems]);

  // Absolute item indices map
  const absoluteIndexMap = React.useMemo(() => {
    const list: string[] = [];
    Object.keys(categories).forEach((cat) => {
      categories[cat].forEach((item) => {
        list.push(item.id);
      });
    });
    return list;
  }, [categories]);

  return (
    <SafePortal>
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-[10vh] sm:p-6 md:p-10">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm"
              onClick={onClose}
            />

            {/* Dialog Panel */}
            <motion.div
              ref={containerRef}
              initial={{ opacity: 0, scale: 0.97, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: 8 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="relative z-50 w-full max-w-lg overflow-hidden rounded-xl border border-border bg-card shadow-xl flex flex-col max-h-[70vh]"
            >
              {/* Search Header */}
              <div className="flex items-center border-b border-border/60 px-4 py-3 bg-muted/20">
                <Search className="h-4 w-4 mr-3 text-muted-foreground shrink-0" />
                <input
                  ref={inputRef}
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={placeholder}
                  className="w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
                />
                <kbd className="hidden sm:inline-block pointer-events-none select-none rounded border border-border bg-muted px-1.5 font-mono text-[9px] font-medium text-muted-foreground ml-2 uppercase shrink-0">
                  ESC
                </kbd>
              </div>

              {/* Items List */}
              <div className="flex-1 overflow-y-auto p-2 space-y-4">
                {filteredItems.length === 0 ? (
                  <div className="py-8 text-center text-xs text-muted-foreground">
                    No results found for "{search}"
                  </div>
                ) : (
                  Object.keys(categories).map((catName) => (
                    <div key={catName} className="space-y-1">
                      <h4 className="px-3 py-1.5 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                        {catName}
                      </h4>
                      <div className="space-y-0.5">
                        {categories[catName].map((item) => {
                          const absIdx = absoluteIndexMap.indexOf(item.id);
                          const isSelected = absIdx === selectedIndex;

                          return (
                            <button
                              key={item.id}
                              onClick={() => {
                                item.onSelect();
                                onClose();
                              }}
                              className={cn(
                                "flex w-full items-center justify-between rounded-md px-3 py-2 text-xs text-left transition-all duration-150",
                                isSelected
                                  ? "bg-accent text-accent-foreground shadow-xs"
                                  : "text-foreground hover:bg-accent/40",
                              )}
                              role="option"
                              aria-selected={isSelected}
                            >
                              <div className="flex items-center gap-3 overflow-hidden">
                                {item.icon && (
                                  <span className="h-4 w-4 shrink-0 text-muted-foreground flex items-center justify-center">
                                    {item.icon}
                                  </span>
                                )}
                                <div className="overflow-hidden">
                                  <p className="font-medium truncate">{item.title}</p>
                                  {item.description && (
                                    <p className="text-[10px] text-muted-foreground truncate">
                                      {item.description}
                                    </p>
                                  )}
                                </div>
                              </div>

                              {item.shortcut && (
                                <div className="flex items-center gap-0.5 ml-2 shrink-0">
                                  {item.shortcut.map((key, i) => (
                                    <kbd
                                      key={i}
                                      className="pointer-events-none select-none rounded border border-border/80 bg-muted px-1 py-0.5 font-mono text-[8px] font-semibold text-muted-foreground uppercase"
                                    >
                                      {key}
                                    </kbd>
                                  ))}
                                </div>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </SafePortal>
  );
};
CommandPalette.displayName = "CommandPalette";
