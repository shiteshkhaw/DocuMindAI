import * as React from "react";
import { cn } from "../utils/cn.js";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "pulse" | "shimmer";
}

export const Skeleton: React.FC<SkeletonProps> = ({ className, variant = "pulse", ...props }) => {
  return (
    <div
      className={cn(
        "rounded-md bg-muted/70",
        {
          "animate-pulse-subtle": variant === "pulse",
          "relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_2s_infinite] before:bg-gradient-to-r before:from-transparent before:via-foreground/5 before:to-transparent":
            variant === "shimmer",
        },
        className,
      )}
      {...props}
    />
  );
};
