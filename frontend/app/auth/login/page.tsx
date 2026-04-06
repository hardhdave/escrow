"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { fetchApi } from "@/lib/api";
import { parseSessionFromToken } from "@/lib/session";

type TokenResponse = {
  access_token: string;
  token_type: string;
};

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const result = await fetchApi<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    if (result.error || !result.data) {
      setError(result.error ?? "Unable to sign in");
      setIsSubmitting(false);
      return;
    }

    login(parseSessionFromToken(result.data.access_token, email));
    const next = searchParams.get("next") || "/dashboard";
    router.push(next);
  }

  return (
    <main className="container" style={{ padding: "30px 0 50px" }}>
      <div className="panel" style={{ maxWidth: 620, margin: "0 auto", padding: 28 }}>
        <div className="pill">Sign in</div>
        <h1 className="section-title" style={{ marginTop: 18 }}>
          Return to your workspace
        </h1>
        <p className="section-copy">
          Authentication is now real enough to gate private routes. Sign in stores a local session and unlocks dashboard pages.
        </p>
        <form className="form-grid" style={{ marginTop: 24 }} onSubmit={handleSubmit}>
          <input placeholder="Email address" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <input placeholder="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p style={{ color: "var(--muted)" }}>
          Need an account? <Link href="/auth/register">Create one</Link>
        </p>
      </div>
    </main>
  );
}
