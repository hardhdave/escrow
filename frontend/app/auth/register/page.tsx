"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { fetchApi } from "@/lib/api";
import { parseSessionFromToken } from "@/lib/session";
import type { UserRole } from "@/types/auth";

type TokenResponse = {
  access_token: string;
  token_type: string;
};

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("client");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const result = await fetchApi<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, role })
    });

    if (result.error || !result.data) {
      setError(result.error ?? "Unable to create account");
      setIsSubmitting(false);
      return;
    }

    login(parseSessionFromToken(result.data.access_token, email, role));
    router.push("/dashboard");
  }

  return (
    <main className="container" style={{ padding: "30px 0 50px" }}>
      <div className="panel" style={{ maxWidth: 720, margin: "0 auto", padding: 28 }}>
        <div className="pill">Create account</div>
        <h1 className="section-title" style={{ marginTop: 18 }}>
          Start with a cleaner contract
        </h1>
        <p className="section-copy">
          Registration now creates a backend user, stores the returned token locally, and moves straight into the private workspace.
        </p>
        <form className="form-grid" style={{ marginTop: 24 }} onSubmit={handleSubmit}>
          <input placeholder="Email address" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <div className="grid two-col">
            <select value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
              <option value="client">Client</option>
              <option value="freelancer">Freelancer</option>
              <option value="admin">Admin</option>
            </select>
            <input placeholder="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating account..." : "Create account"}
          </button>
        </form>
        <p style={{ color: "var(--muted)" }}>
          Already onboarded? <Link href="/auth/login">Sign in</Link>
        </p>
      </div>
    </main>
  );
}
