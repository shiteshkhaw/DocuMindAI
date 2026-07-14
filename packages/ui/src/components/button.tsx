import * as React from "react";
import { cn } from "../utils/cn.js";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "glass";
  size?: "sm" | "md" | "lg" | "icon";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading = false, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-all duration-200 ease-out-expo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
          {
            // Variants
            "bg-primary text-primary-foreground hover:bg-primary/95 shadow-sm hover:shadow shadow-primary/10":
              variant === "primary",
            "bg-secondary text-secondary-foreground border border-border/60 hover:bg-secondary/80 hover:border-border shadow-xs":
              variant === "secondary",
            "border border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground hover:border-border/80":
              variant === "outline",
            "text-muted-foreground hover:bg-accent hover:text-accent-foreground":
              variant === "ghost",
            "bg-background/50 border border-border/40 backdrop-blur-md text-foreground hover:bg-background/80 hover:border-border/60 shadow-xs":
              variant === "glass",

            // Sizes
            "h-8 px-3 text-xs rounded-sm": size === "sm",
            "h-10 px-4 text-sm rounded-md": size === "md",
            "h-12 px-6 text-base rounded-md": size === "lg",
            "h-10 w-10 p-0 rounded-md": size === "icon",
          },
          className,
        )}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2 flex h-4 w-4 items-center justify-center">
            <svg
              className="h-4 w-4 animate-spin text-current"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </span>
        ) : null}
        {children}
      </button>
    );
  },
);

Button.displayName = "Button";
