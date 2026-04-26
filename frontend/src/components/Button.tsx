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

export const Button = ({ className, variant = "default", size = "default", children, ...props }: any) => {
  const variants = {
    default: "bg-orange-600 text-white hover:bg-orange-700 shadow-lg shadow-orange-600/20",
    outline: "border border-white/10 bg-white/5 text-slate-200 hover:bg-white/10",
    ghost: "bg-transparent text-slate-400 hover:bg-white/5",
  };
  const sizes = {
    default: "px-4 py-2 text-sm",
    sm: "px-3 py-1.5 text-xs",
    lg: "px-6 py-3 text-base",
  };
  return (
    <button className={cn("inline-flex items-center justify-center rounded-xl font-bold transition-all disabled:opacity-50", variants[variant as keyof typeof variants], sizes[size as keyof typeof sizes], className)} {...props}>
      {children}
    </button>
  );
};
