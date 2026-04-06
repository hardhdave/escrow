const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001/v1";
const STORAGE_KEY = "escrow-dex-session";

export type ApiResult<T> = {
  data: T | null;
  error: string | null;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

async function readError(response: Response): Promise<string> {
  const text = await response.text();

  if (!text) {
    return `Request failed with ${response.status}`;
  }

  try {
    const parsed = JSON.parse(text) as unknown;
    if (isRecord(parsed) && typeof parsed.detail === "string") {
      return parsed.detail;
    }
  } catch {
    return text;
  }

  return text;
}

function handleUnauthorized(error: string): void {
  if (typeof window === "undefined") {
    return;
  }

  if (error === "Invalid or expired token") {
    window.localStorage.removeItem(STORAGE_KEY);
    if (window.location.pathname !== "/auth/login") {
      window.location.href = "/auth/login";
    }
  }
}

export async function fetchApi<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {})
      },
      cache: "no-store"
    });

    if (!response.ok) {
      const error = await readError(response);
      if (response.status === 401) {
        handleUnauthorized(error);
      }
      return { data: null, error };
    }

    return { data: (await response.json()) as T, error: null };
  } catch (error) {
    return { data: null, error: error instanceof Error ? error.message : "Unknown error" };
  }
}
