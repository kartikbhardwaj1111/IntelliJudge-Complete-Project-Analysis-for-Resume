/**
 * IntelliJudge — API Client
 *
 * A thin fetch wrapper that:
 *   1. Prepends NEXT_PUBLIC_API_URL to every request path
 *   2. Injects the JWT token from localStorage as Authorization: Bearer <token>
 *   3. Sets Content-Type: application/json on non-FormData requests
 *   4. Unwraps the standard { success, data, message } envelope
 *   5. Throws ApiError on non-2xx responses so callers can catch cleanly
 *
 * Usage:
 *   import { api } from "@/lib/api";
 *   const user = await api.get<User>("/auth/me");
 *   const result = await api.post<AuthResponse>("/auth/login", { email, password });
 */

import type { ApiResponse } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

// ─── Error type ────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly errors?: { field: string; message: string }[]
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ─── Token helpers ─────────────────────────────────────────────
// localStorage is only available client-side — guard every access.

const TOKEN_KEY = "ij_token";

export const tokenStore = {
  get(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  },
  set(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEY, token);
  },
  clear(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEY);
  },
};

// ─── Core fetch function ───────────────────────────────────────

// Upload requests need a long timeout (EasyOCR can take 60s+ on first use).
// All other requests timeout after 30s.
const UPLOAD_TIMEOUT_MS = 3 * 60 * 1000; // 3 minutes
const DEFAULT_TIMEOUT_MS = 30 * 1000;    // 30 seconds

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const token = tokenStore.get();

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let fetchBody: BodyInit | undefined;
  if (body instanceof FormData) {
    // Don't set Content-Type — browser sets it with the correct boundary
    fetchBody = body;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    fetchBody = JSON.stringify(body);
  }

  const isUpload = body instanceof FormData;
  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    isUpload ? UPLOAD_TIMEOUT_MS : DEFAULT_TIMEOUT_MS
  );

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: fetchBody,
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(
        408,
        isUpload
          ? "Upload timed out after 3 minutes. The OCR model may still be loading — please try again."
          : "Request timed out. Please check your connection and try again."
      );
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }

  // Handle 204 No Content
  if (res.status === 204) return undefined as T;

  const json: ApiResponse<T> = await res.json();

  if (!res.ok || !json.success) {
    throw new ApiError(
      res.status,
      json.message ?? "An unexpected error occurred",
      json.errors ?? undefined
    );
  }

  return json.data as T;
}

// ─── Public API surface ────────────────────────────────────────

export const api = {
  get<T>(path: string): Promise<T> {
    return request<T>("GET", path);
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("POST", path, body);
  },
  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("PUT", path, body);
  },
  delete<T>(path: string): Promise<T> {
    return request<T>("DELETE", path);
  },
};
