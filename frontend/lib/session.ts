import type { AuthSession, UserRole } from "@/types/auth";

type JwtPayload = {
  sub?: string;
  role?: UserRole;
};

export function parseSessionFromToken(token: string, email: string, fallbackRole: UserRole = "client"): AuthSession {
  let payload: JwtPayload | null = null;

  try {
    const [, encodedPayload] = token.split(".");
    if (encodedPayload) {
      const normalized = encodedPayload.replace(/-/g, "+").replace(/_/g, "/");
      const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
      payload = JSON.parse(window.atob(padded)) as JwtPayload;
    }
  } catch {
    payload = null;
  }

  return {
    accessToken: token,
    user: {
      id: payload?.sub ?? "unknown-user",
      email,
      role: payload?.role ?? fallbackRole
    }
  };
}
