"use client";

import Link from "next/link";

import { useAuth } from "@/components/auth-provider";
import { DashboardShell } from "@/components/dashboard-shell";
import { ProtectedPage } from "@/components/protected-page";

export default function DashboardPage() {
  const { session } = useAuth();

  return (
    <ProtectedPage>
      <DashboardShell
        active="dashboard"
        title="Minimal control panel"
        subtitle="Only the valuable things stay here: your role, your user ID, and the next step into an escrow room."
      >
        <section className="panel" style={{ padding: 24 }}>
          <div className="card-list">
            <article className="list-card">
              <strong>Signed in account</strong>
              <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                {session?.user.email} | role {session?.user.role} | user ID {session?.user.id}
              </p>
            </article>
            <article className="list-card">
              <strong>How connection works now</strong>
              <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                Client creates a room and gets a room code. Freelancer joins using that code. After that, both meet in one room for hold, release, refund requests, and disputes.
              </p>
            </article>
            <Link href="/rooms" className="primary-button" prefetch={false}>
              Go to rooms
            </Link>
          </div>
        </section>
      </DashboardShell>
    </ProtectedPage>
  );
}
