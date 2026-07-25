import { getAccessToken } from "./auth";

const DEFAULT_API_BASE_URL = "/api/v1";
const REQUEST_TIMEOUT_MS = 10_000; // 10 seconds

export function getApiBaseUrl() {
  return (import.meta.env.VITE_API_URL as string | undefined) ?? DEFAULT_API_BASE_URL;
}

/**
 * Wraps fetch with an AbortController timeout so the browser never hangs
 * indefinitely when the backend is unreachable.
 */
function fetchWithTimeout(url: string, init: RequestInit, timeoutMs = REQUEST_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  return fetch(url, { ...init, signal: controller.signal })
    .catch((err) => {
      if (err.name === "AbortError") {
        throw new Error("Request timed out — is the backend server running?");
      }
      throw new Error(`Network error — could not reach the server. ${err.message ?? ""}`);
    })
    .finally(() => clearTimeout(timer));
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const accessToken = getAccessToken();
  if (accessToken && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetchWithTimeout(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail ?? payload?.message ?? `Request failed with status ${response.status}`;
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg ?? item).join(", ") : String(detail));
  }

  return payload as T;
}

/** Upload helper for multipart/form-data (e.g. meeting recordings, avatars) */
export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  const headers = new Headers();
  // Do NOT set Content-Type — browser sets it with the boundary for multipart
  const accessToken = getAccessToken();
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  // Uploads get a longer timeout (5 minutes)
  const response = await fetchWithTimeout(
    `${getApiBaseUrl()}${path}`,
    { method: "POST", headers, body: formData },
    300_000,
  );

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail ?? payload?.message ?? `Upload failed with status ${response.status}`;
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg ?? item).join(", ") : String(detail));
  }

  return payload as T;
}
