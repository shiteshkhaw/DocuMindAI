"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "../utils/cn.js";

interface DropdownContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  triggerRef: React.RefObject<HTMLButtonElement | null>;
  contentRef: React.RefObject<HTMLDivElement | null>;
}

const DropdownContext = React.createContext<DropdownContextType | undefined>(undefined);

export function useDropdown() {
  const context = React.useContext(DropdownContext);
  if (!context) throw new Error("useDropdown must be used within Dropdown");
  return context;
}

export interface DropdownProps {
  children: React.ReactNode;
}

export const Dropdown: React.FC<DropdownProps> = ({ children }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const triggerRef = React.useRef<HTMLButtonElement>(null);
  const contentRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        isOpen &&
        contentRef.current &&
        !contentRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  React.useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && isOpen) {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  return (
    <DropdownContext.Provider value={{ isOpen, setIsOpen, triggerRef, contentRef }}>
      <div className="relative inline-block text-left">{children}</div>
    </DropdownContext.Provider>
  );
};

export interface DropdownTriggerProps {
  children: React.ReactElement;
}

export const DropdownTrigger = React.forwardRef<HTMLButtonElement, DropdownTriggerProps>(
  ({ children }, ref) => {
    const { isOpen, setIsOpen, triggerRef } = useDropdown();

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        e.preventDefault();
        setIsOpen(true);
      }
    };

    const setRef = React.useCallback(
      (node: HTMLButtonElement | null) => {
        // @ts-ignore
        triggerRef.current = node;
        if (typeof ref === "function") {
          ref(node);
        } else if (ref) {
          // @ts-ignore
          ref.current = node;
        }
      },
      [ref, triggerRef]
    );

    const child = React.Children.only(children) as React.ReactElement<any>;

    return React.cloneElement(child, {
      ref: setRef,
      onClick: (e: React.MouseEvent) => {
        e.preventDefault();
        setIsOpen(!isOpen);
        child.props.onClick?.(e);
      },
      onKeyDown: (e: React.KeyboardEvent) => {
        handleKeyDown(e);
        child.props.onKeyDown?.(e);
      },
      "aria-haspopup": "menu",
      "aria-expanded": isOpen,
    });
  }
);
DropdownTrigger.displayName = "DropdownTrigger";

export interface DropdownContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: "left" | "right";
}

export const DropdownContent = React.forwardRef<HTMLDivElement, DropdownContentProps>(
  ({ children, className, align = "right", ...props }, ref) => {
    const { isOpen, contentRef } = useDropdown();

    return (
      <AnimatePresence>
        {isOpen && (
          <div ref={contentRef} className={cn("absolute z-50", align === "right" ? "right-0" : "left-0")}>
            <motion.div
              ref={ref}
              initial={{ opacity: 0, scale: 0.95, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -4 }}
              transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
              className={cn(
                "mt-2 w-56 rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-lg focus:outline-none ring-1 ring-black/5 origin-top-right",
                align === "right" ? "right-0" : "left-0",
                className
              )}
              role="menu"
              aria-orientation="vertical"
              {...(props as any)}
            >
              {children}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    );
  }
);
DropdownContent.displayName = "DropdownContent";

export interface DropdownItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactNode;
}

export const DropdownItem = React.forwardRef<HTMLButtonElement, DropdownItemProps>(
  ({ children, className, icon, onClick, ...props }, ref) => {
    const { setIsOpen } = useDropdown();

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      onClick?.(e);
      setIsOpen(false);
    };

    return (
      <button
        ref={ref}
        type="button"
        role="menuitem"
        onClick={handleClick}
        className={cn(
          "flex w-full items-center rounded-sm px-3 py-2 text-xs text-left text-foreground hover:bg-accent hover:text-accent-foreground focus-visible:bg-accent focus-visible:text-accent-foreground outline-none transition-colors duration-150 disabled:pointer-events-none disabled:opacity-50",
          className
        )}
        {...props}
      >
        {icon && <span className="mr-2 h-3.5 w-3.5 flex items-center justify-center text-muted-foreground">{icon}</span>}
        {children}
      </button>
    );
  }
);
DropdownItem.displayName = "DropdownItem";

export const DropdownSeparator: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => {
  return <div className={cn("-mx-1 my-1 h-px bg-border/60", className)} {...props} />;
};
DropdownSeparator.displayName = "DropdownSeparator";
