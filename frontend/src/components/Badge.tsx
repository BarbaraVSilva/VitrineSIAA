import React from "react";
import { cn } from "../lib/utils";

export const Badge = ({ className, variant = "default", children }: { className?: string; variant?: "default" | "outline"; children: React.ReactNode }) => (
  <span className={cn(
    "px-2 py-0.5 rounded-full text-[10px] font-bold inline-flex items-center justify-center",
    variant === "default" ? "bg-orange-600 text-white" : "border border-white/10 bg-white/5 text-slate-400",
    className
  )}>
    {children}
  </span>
);
