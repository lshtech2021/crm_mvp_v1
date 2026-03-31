import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { AuthProvider, useAuth } from "@/lib/auth/context";
import { getAccessToken, getRefreshToken, setTokens } from "@/lib/auth/tokens";
import type { User } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const mockUser: User = {
  id: "user-1",
  email: "rep@example.com",
  first_name: "Test",
  last_name: "User",
  role: "rep",
  tenant_id: "tenant-1",
};

function accessTokenValidFor(secondsFromNow = 3600): string {
  const exp = Math.floor(Date.now() / 1000) + secondsFromNow;
  const payload = btoa(JSON.stringify({ exp }));
  return `hdr.${payload}.sig`;
}

function TestConsumer() {
  const { user, isLoading, login, logout } = useAuth();
  if (isLoading) return <div data-testid="auth-loading">loading</div>;
  return (
    <div>
      <span data-testid="user-email">{user?.email ?? ""}</span>
      <button type="button" onClick={() => login("rep@example.com", "secret")}>
        do-login
      </button>
      <button type="button" onClick={() => void logout()}>
        do-logout
      </button>
    </div>
  );
}

function parseUrl(input: RequestInfo | URL): string {
  if (typeof input === "string") return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe("AuthProvider", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("on mount with valid tokens in localStorage, restores user session (calls getMe)", async () => {
    const access = accessTokenValidFor();
    const refresh = "refresh-token-value";
    setTokens(access, refresh);

    globalThis.fetch = vi.fn(async (input, init) => {
      const url = parseUrl(input);
      const method = init?.method ?? "GET";
      if (method === "GET" && url === `${API_BASE}/api/auth/me`) {
        return new Response(JSON.stringify(mockUser), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response("unexpected", { status: 500 });
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("user-email")).toHaveTextContent(mockUser.email);
    });

    const fetchMock = vi.mocked(globalThis.fetch);
    expect(fetchMock).toHaveBeenCalled();
    const meCall = fetchMock.mock.calls.find(
      (call) => parseUrl(call[0]) === `${API_BASE}/api/auth/me`,
    );
    expect(meCall).toBeDefined();
    expect(meCall?.[1]?.method ?? "GET").toBe("GET");
  });

  it("on mount with no tokens, user remains null", async () => {
    globalThis.fetch = vi.fn(() =>
      Promise.reject(new Error("fetch should not run without tokens")),
    );

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.queryByTestId("auth-loading")).not.toBeInTheDocument();
    });

    expect(screen.getByTestId("user-email")).toHaveTextContent("");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("login sets user state and stores tokens", async () => {
    const user = userEvent.setup();
    const loginBody = {
      access_token: accessTokenValidFor(),
      refresh_token: "new-refresh",
      user: mockUser,
    };

    globalThis.fetch = vi.fn(async (input, init) => {
      const url = parseUrl(input);
      const method = init?.method ?? "GET";
      if (method === "POST" && url === `${API_BASE}/api/auth/login`) {
        return new Response(JSON.stringify(loginBody), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response("unexpected", { status: 500 });
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.queryByTestId("auth-loading")).not.toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /do-login/i }));

    await waitFor(() => {
      expect(screen.getByTestId("user-email")).toHaveTextContent(mockUser.email);
    });

    expect(getAccessToken()).toBe(loginBody.access_token);
    expect(getRefreshToken()).toBe(loginBody.refresh_token);
  });

  it("logout clears user state and tokens", async () => {
    const user = userEvent.setup();
    const access = accessTokenValidFor();
    setTokens(access, "rt");

    const locationStub = { href: "http://localhost:3000/" };
    vi.stubGlobal("location", locationStub as Location);

    globalThis.fetch = vi.fn(async (input, init) => {
      const url = parseUrl(input);
      const method = init?.method ?? "GET";
      if (method === "GET" && url === `${API_BASE}/api/auth/me`) {
        return new Response(JSON.stringify(mockUser), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (method === "POST" && url === `${API_BASE}/api/auth/logout`) {
        return new Response(null, { status: 204 });
      }
      return new Response("unexpected", { status: 500 });
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("user-email")).toHaveTextContent(mockUser.email);
    });

    await user.click(screen.getByRole("button", { name: /do-logout/i }));

    await waitFor(() => {
      expect(screen.getByTestId("user-email")).toHaveTextContent("");
    });

    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
    expect(locationStub.href).toBe("/login");
  });

  it("401 response on getMe clears tokens (and api client redirects to login)", async () => {
    const access = accessTokenValidFor();
    setTokens(access, "rt");

    const locationStub = { href: "http://localhost:3000/" };
    vi.stubGlobal("location", locationStub as Location);

    globalThis.fetch = vi.fn(async (input, init) => {
      const url = parseUrl(input);
      const method = init?.method ?? "GET";
      if (method === "GET" && url === `${API_BASE}/api/auth/me`) {
        return new Response(JSON.stringify({ detail: "Unauthorized" }), {
          status: 401,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response("unexpected", { status: 500 });
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(getAccessToken()).toBeNull();
      expect(getRefreshToken()).toBeNull();
    });

    expect(locationStub.href).toBe("/login");
  });
});
