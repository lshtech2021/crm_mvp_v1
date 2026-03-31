"use client";

import type { ReactNode } from "react";
import { Sidebar } from "./sidebar";
import { TopNav } from "./top-nav";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Sidebar />
      <div className="lg:pl-64">
        <TopNav />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
