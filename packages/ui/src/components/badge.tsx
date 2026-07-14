import * as React from "react";
import { cn } from "../utils/cn.js";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "primary" | "secondary" | "outline" | "success" | "warning" | "error" | "info";
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = "secondary", ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-medium tracking-wide uppercase transition-colors duration-200",
          {
            "bg-primary/10 text-primary border border-primary/20": variant === "primary",
            "bg-secondary text-secondary-foreground border border-border/40":
              variant === "secondary",
            "border border-border text-foreground bg-transparent": variant === "outline",
            "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20":
              variant === "success",
            "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 animate-pulse-subtle":
              variant === "warning",
            "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20":
              variant === "error",
            "bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20":
              variant === "info",
          },
          className,
        )}
        {...props}
      />
    );
  },
);

Badge.displayName = "Badge";
