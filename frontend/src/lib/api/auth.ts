import type { User } from "@/types";
import { api } from "./client";

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

interface RefreshResponse {
  access_token: string;
  refresh_token: string;
}

export function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  return api.post<LoginResponse>("/api/auth/login", { email, password });
}

export function refresh(refreshToken: string): Promise<RefreshResponse> {
  return api.post<RefreshResponse>("/api/auth/refresh", {
    refresh_token: refreshToken,
  });
}

export function logout(): Promise<void> {
  return api.post<void>("/api/auth/logout");
}

export function getMe(): Promise<User> {
  return api.get<User>("/api/auth/me");
}
