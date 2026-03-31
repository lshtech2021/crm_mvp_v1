import type { ApiError } from "@/types";
import { clearTokens, getAccessToken } from "@/lib/auth/tokens";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null as T;
  }

  if (response.status === 401) {
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw { detail: "Unauthorized", status: 401 } satisfies ApiError;
  }

  if (response.status === 403) {
    throw { detail: "Permission denied", status: 403 } satisfies ApiError;
  }

  if (response.status === 409) {
    throw {
      detail: "Conflict — resource was modified",
      status: 409,
    } satisfies ApiError;
  }

  if (response.status === 422) {
    const body = await response.json();
    const message =
      body?.detail
        ?.map(
          (e: { loc: string[]; msg: string }) =>
            `${e.loc.join(".")}: ${e.msg}`,
        )
        .join("; ") ?? "Validation error";
    throw { detail: message, status: 422 } satisfies ApiError;
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw {
      detail: body?.detail ?? response.statusText,
      status: response.status,
    } satisfies ApiError;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return apiClient<T>(endpoint, { ...options, method: "GET" });
  },

  post<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return apiClient<T>(endpoint, {
      ...options,
      method: "POST",
      body: body != null ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return apiClient<T>(endpoint, {
      ...options,
      method: "PUT",
      body: body != null ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return apiClient<T>(endpoint, { ...options, method: "DELETE" });
  },
};
