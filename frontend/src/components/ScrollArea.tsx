import React from "react";
import { cn } from "../lib/utils";

export const ScrollArea = ({ className, children }: { className?: string; children: React.ReactNode }) => (
  <div className={cn("overflow-y-auto overflow-x-hidden", className)}>
    {children}
  </div>
);
