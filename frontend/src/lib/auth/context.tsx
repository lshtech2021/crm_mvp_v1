"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import type { User, UserRole } from "@/types";
import * as authApi from "@/lib/api/auth";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  isTokenExpired,
  setTokens,
} from "./tokens";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  role: UserRole | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const REFRESH_INTERVAL_MS = 4 * 60 * 1000; // refresh every 4 minutes

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  const attemptRefresh = useCallback(async () => {
    const rt = getRefreshToken();
    if (!rt) return;
    try {
      const res = await authApi.refresh(rt);
      setTokens(res.access_token, res.refresh_token);
    } catch {
      clearTokens();
      setUser(null);
      stopRefreshTimer();
    }
  }, [stopRefreshTimer]);

  const startRefreshTimer = useCallback(() => {
    stopRefreshTimer();
    refreshTimerRef.current = setInterval(attemptRefresh, REFRESH_INTERVAL_MS);
  }, [attemptRefresh, stopRefreshTimer]);

  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      const token = getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      if (isTokenExpired(token)) {
        await attemptRefresh();
      }

      try {
        const me = await authApi.getMe();
        if (!cancelled) {
          setUser(me);
          startRefreshTimer();
        }
      } catch {
        clearTokens();
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    restoreSession();
    return () => {
      cancelled = true;
      stopRefreshTimer();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authApi.login(email, password);
      setTokens(res.access_token, res.refresh_token);
      setUser(res.user);
      startRefreshTimer();
    },
    [startRefreshTimer],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      /* best-effort */
    }
    clearTokens();
    setUser(null);
    stopRefreshTimer();
    window.location.href = "/login";
  }, [stopRefreshTimer]);

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    role: user?.role ?? null,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
