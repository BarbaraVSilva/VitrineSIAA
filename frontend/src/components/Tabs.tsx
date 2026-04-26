import React from "react";
import { cn } from "../lib/utils";

export const ScrollArea = ({ className, children }: { className?: string; children: React.ReactNode }) => (
  <div className={cn("overflow-y-auto scrollbar-thin scrollbar-thumb-white/10", className)}>
    {children}
  </div>
);

export const Tabs = ({ children, className }: any) => <div className={cn("w-full", className)}>{children}</div>;
export const TabsList = ({ children, className }: any) => <div className={cn("flex bg-white/5 p-1 rounded-xl", className)}>{children}</div>;
export const TabsTrigger = ({ children, active, onClick, className }: any) => (
  <button onClick={onClick} className={cn("flex-1 px-4 py-2 text-xs font-bold rounded-lg transition-all", active ? "bg-orange-600 text-white shadow-lg" : "text-slate-500 hover:text-slate-300", className)}>
    {children}
  </button>
);
export const TabsContent = ({ children, active }: any) => (active ? <div className="mt-6">{children}</div> : null);
