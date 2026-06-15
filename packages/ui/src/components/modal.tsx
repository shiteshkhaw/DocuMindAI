"use client";

import * as React from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "../utils/cn.js";

interface ModalContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const ModalContext = React.createContext<ModalContextType | undefined>(undefined);

export function useModal() {
  const context = React.useContext(ModalContext);
  if (!context) throw new Error("useModal must be used within Modal");
  return context;
}

export interface ModalProps {
  children: React.ReactNode;
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export const Modal: React.FC<ModalProps> = ({ children, isOpen: customIsOpen, onOpenChange }) => {
  const [localIsOpen, setLocalIsOpen] = React.useState(false);
  const isControlled = customIsOpen !== undefined;
  const isOpen = isControlled ? customIsOpen : localIsOpen;

  const setIsOpen = React.useCallback(
    (open: boolean) => {
      if (!isControlled) {
        setLocalIsOpen(open);
      }
      onOpenChange?.(open);
    },
    [isControlled, onOpenChange]
  );

  return (
    <ModalContext.Provider value={{ isOpen, setIsOpen }}>
      {children}
    </ModalContext.Provider>
  );
};

export interface ModalTriggerProps {
  children: React.ReactElement;
}

export const ModalTrigger = React.forwardRef<HTMLElement, ModalTriggerProps>(
  ({ children }, ref) => {
    const { setIsOpen } = useModal();
    const child = React.Children.only(children) as React.ReactElement<any>;

    return React.cloneElement(child, {
      // @ts-ignore
      ref,
      onClick: (e: React.MouseEvent) => {
        e.preventDefault();
        setIsOpen(true);
        child.props.onClick?.(e);
      },
    });
  }
);
ModalTrigger.displayName = "ModalTrigger";

interface PortalProps {
  children: React.ReactNode;
}

const SafePortal: React.FC<PortalProps> = ({ children }) => {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  if (!mounted) return null;
  return createPortal(children, document.body);
};

export interface ModalContentProps extends React.HTMLAttributes<HTMLDivElement> {
  showCloseButton?: boolean;
}

export const ModalContent = React.forwardRef<HTMLDivElement, ModalContentProps>(
  ({ children, className, showCloseButton = true, ...props }, ref) => {
    const { isOpen, setIsOpen } = useModal();

    React.useEffect(() => {
      if (isOpen) {
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "";
      }
      return () => {
        document.body.style.overflow = "";
      };
    }, [isOpen]);

    // Escape listener
    React.useEffect(() => {
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Escape" && isOpen) {
          setIsOpen(false);
        }
      };
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }, [isOpen, setIsOpen]);

    return (
      <SafePortal>
        <AnimatePresence>
          {isOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-10">
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
                className="fixed inset-0 bg-background/80 backdrop-blur-sm"
                onClick={() => setIsOpen(false)}
              />

              {/* Dialog Panel */}
              <motion.div
                ref={ref}
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                className={cn(
                  "relative z-50 w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-xl focus:outline-none",
                  className
                )}
                role="dialog"
                aria-modal="true"
                {...(props as any)}
              >
                {showCloseButton && (
                  <button
                    onClick={() => setIsOpen(false)}
                    className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-4 w-4" />
                    <span className="sr-only">Close</span>
                  </button>
                )}
                {children}
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </SafePortal>
    );
  }
);
ModalContent.displayName = "ModalContent";

export const ModalHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn("flex flex-col space-y-1.5 text-center sm:text-left mb-4", className)}
    {...props}
  />
);
ModalHeader.displayName = "ModalHeader";

export const ModalTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h2
    ref={ref}
    className={cn("text-lg font-semibold leading-none tracking-tight text-foreground", className)}
    {...props}
  />
));
ModalTitle.displayName = "ModalTitle";

export const ModalDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-xs text-muted-foreground leading-normal mt-1.5", className)}
    {...props}
  />
));
ModalDescription.displayName = "ModalDescription";

export const ModalFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 border-t border-border/40 pt-4 mt-6", className)}
    {...props}
  />
);
ModalFooter.displayName = "ModalFooter";
