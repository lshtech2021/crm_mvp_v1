"use client";

import { useAuth } from "@/lib/auth/context";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function TopNav() {
  const { user, role, logout } = useAuth();

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-end border-b border-neutral-200 bg-white px-6">
      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-neutral-700">
              {user.first_name} {user.last_name}
            </span>
            {role && <Badge variant="info">{role}</Badge>}
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={logout}>
          Logout
        </Button>
      </div>
    </header>
  );
}
