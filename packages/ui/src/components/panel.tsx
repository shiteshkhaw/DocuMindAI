import * as React from "react";
import { cn } from "../utils/cn.js";

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "flat" | "bordered" | "raised";
}

export const Panel = React.forwardRef<HTMLDivElement, PanelProps>(
  ({ className, variant = "flat", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-lg overflow-hidden transition-all duration-200",
          {
            "bg-muted/40 border border-border/40": variant === "flat",
            "bg-background border border-border shadow-xs": variant === "bordered",
            "bg-card border border-card-border shadow-sm hover:shadow-md": variant === "raised",
          },
          className
        )}
        {...props}
      />
    );
  }
);

Panel.displayName = "Panel";
