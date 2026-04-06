"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { DashboardShell } from "@/components/dashboard-shell";
import { ProtectedPage } from "@/components/protected-page";
import { fetchApi } from "@/lib/api";

type ContractSummary = {
  id: string;
  title: string;
  status: string;
  currency: string;
  current_user_role: string;
  counterparty_id: string;
  counterparty_role: string;
  message_count: number;
};

type ContractCreateResponse = {
  id: string;
};

export default function ContractsPage() {
  const router = useRouter();
  const { session } = useAuth();
  const [contracts, setContracts] = useState<ContractSummary[]>([]);
  const [title, setTitle] = useState("");
  const [freelancerId, setFreelancerId] = useState("");
  const [milestoneTitle, setMilestoneTitle] = useState("");
  const [milestoneAmount, setMilestoneAmount] = useState("500");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function loadContracts() {
    if (!session) {
      return;
    }

    const result = await fetchApi<ContractSummary[]>("/contracts/mine", {
      headers: {
        Authorization: `Bearer ${session.accessToken}`
      }
    });

    setContracts(result.data ?? []);
  }

  useEffect(() => {
    void loadContracts();
  }, [session]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    const result = await fetchApi<ContractCreateResponse>("/contracts", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.accessToken}`
      },
      body: JSON.stringify({
        title,
        freelancer_id: freelancerId,
        currency: "USD",
        milestones: [
          {
            title: milestoneTitle,
            amount: Number(milestoneAmount)
          }
        ]
      })
    });

    if (result.error || !result.data) {
      setError(result.error ?? "Unable to create contract");
      setIsSubmitting(false);
      return;
    }

    setTitle("");
    setFreelancerId("");
    setMilestoneTitle("");
    setMilestoneAmount("500");
    await loadContracts();
    router.push(`/contracts/${result.data.id}`);
  }

  return (
    <ProtectedPage>
      <DashboardShell
        active="contracts"
        title="Contracts and rooms"
        subtitle="Each contract now acts as a shared workspace where client and freelancer can message, fund, submit, release, pause, and dispute."
      >
        <section className="panel" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Create a contract room</h2>
          <p className="section-copy" style={{ marginTop: 0 }}>
            Create a room by entering the freelancer account ID, project title, and first milestone.
          </p>
          <form className="form-grid" onSubmit={handleCreate}>
            <input placeholder="Project title" value={title} onChange={(event) => setTitle(event.target.value)} required />
            <input placeholder="Freelancer user ID" value={freelancerId} onChange={(event) => setFreelancerId(event.target.value)} required />
            <div className="grid two-col">
              <input placeholder="First milestone title" value={milestoneTitle} onChange={(event) => setMilestoneTitle(event.target.value)} required />
              <input placeholder="Milestone amount" type="number" min="1" step="1" value={milestoneAmount} onChange={(event) => setMilestoneAmount(event.target.value)} required />
            </div>
            {error && <p className="form-error">{error}</p>}
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating room..." : "Create contract room"}
            </button>
          </form>
        </section>
        <section className="panel" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Your rooms</h2>
          <div className="card-list">
            {contracts.length === 0 ? (
              <article className="list-card">
                <strong>No contract rooms yet</strong>
                <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                  Create one above, then sign in with the other account to see the shared room from both sides.
                </p>
              </article>
            ) : (
              contracts.map((item) => (
                <Link className="list-card room-link" href={`/contracts/${item.id}`} key={item.id} prefetch={false}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                    <strong>{item.title}</strong>
                    <span className={`status ${item.status}`}>{item.status}</span>
                  </div>
                  <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                    You are the {item.current_user_role}. Counterparty {item.counterparty_role} ID: {item.counterparty_id}. Messages: {item.message_count}
                  </p>
                </Link>
              ))
            )}
          </div>
        </section>
      </DashboardShell>
    </ProtectedPage>
  );
}
