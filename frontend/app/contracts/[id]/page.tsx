"use client";

import { useParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { DashboardShell } from "@/components/dashboard-shell";
import { ProtectedPage } from "@/components/protected-page";
import { fetchApi } from "@/lib/api";

type Milestone = {
  id: string;
  title: string;
  amount: number;
  status: string;
  funded_amount: number;
  released_amount: number;
};

type Message = {
  id: string;
  sender_id: string;
  message_type: string;
  body: string;
  created_at: string;
  seen_by_other_party: boolean;
};

type Activity = {
  id: string;
  actor_id: string | null;
  event_type: string;
  summary: string;
  created_at: string;
};

type ContractRoom = {
  id: string;
  title: string;
  status: string;
  currency: string;
  client_id: string;
  freelancer_id: string;
  current_user_role: "client" | "freelancer";
  milestones: Milestone[];
  messages: Message[];
  activities: Activity[];
};

export default function ContractRoomPage() {
  const params = useParams<{ id: string }>();
  const { session } = useAuth();
  const [room, setRoom] = useState<ContractRoom | null>(null);
  const [message, setMessage] = useState("");
  const [pauseReason, setPauseReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);

  const contractId = typeof params.id === "string" ? params.id : "";
  const currentUserId = session?.user.id;

  const authHeaders = useMemo(() => {
    if (!session) {
      return {};
    }
    return {
      Authorization: `Bearer ${session.accessToken}`
    };
  }, [session]);

  async function loadRoom() {
    if (!session || !contractId) {
      return;
    }

    setIsLoading(true);
    const result = await fetchApi<ContractRoom>(`/contracts/${contractId}`, {
      headers: authHeaders
    });
    setRoom(result.data);
    setError(result.error);
    setIsLoading(false);
  }

  useEffect(() => {
    void loadRoom();
  }, [contractId, session]);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !contractId || !message.trim()) {
      return;
    }

    setIsSending(true);
    const result = await fetchApi(`/contracts/${contractId}/messages`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ body: message })
    });

    if (result.error) {
      setError(result.error);
    } else {
      setMessage("");
      await loadRoom();
    }
    setIsSending(false);
  }

  async function changeContractState(action: "pause" | "resume") {
    if (!session || !contractId) {
      return;
    }

    const reason = pauseReason || (action === "pause" ? "Work paused from room controls." : "Work resumed from room controls.");
    const result = await fetchApi<ContractRoom>(`/contracts/${contractId}/${action}`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ reason })
    });

    if (result.error) {
      setError(result.error);
      return;
    }

    setRoom(result.data);
    setPauseReason("");
  }

  async function fundMilestone(milestoneId: string) {
    if (!session) {
      return;
    }

    const result = await fetchApi(`/payments/milestones/${milestoneId}/fund`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ provider: "manual", idempotency_key: `fund-${milestoneId}-${Date.now()}` })
    });

    if (result.error) {
      setError(result.error);
      return;
    }

    await loadRoom();
  }

  async function submitMilestone(milestoneId: string) {
    if (!session) {
      return;
    }

    const result = await fetchApi(`/milestones/${milestoneId}/submit`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ message: "Submitted from contract room", attachments: [] })
    });

    if (result.error) {
      setError(result.error);
      return;
    }

    await loadRoom();
  }

  async function approveMilestone(milestone: Milestone) {
    if (!session) {
      return;
    }

    const remaining = Math.max(milestone.funded_amount - milestone.released_amount, 0);
    const result = await fetchApi(`/milestones/${milestone.id}/approve`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ release_amount: remaining, note: "Released from contract room" })
    });

    if (result.error) {
      setError(result.error);
      return;
    }

    await loadRoom();
  }

  async function disputeMilestone(milestoneId: string) {
    if (!session) {
      return;
    }

    const result = await fetchApi(`/disputes/milestones/${milestoneId}`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ reason_code: "ROOM_ESCALATION", description: "Escalated from contract room" })
    });

    if (result.error) {
      setError(result.error);
      return;
    }

    await loadRoom();
  }

  return (
    <ProtectedPage>
      <DashboardShell
        active="contracts"
        title={room?.title ?? "Contract room"}
        subtitle="Client and freelancer now share one room for conversation, milestones, money movement, and operating decisions."
      >
        {isLoading ? (
          <section className="panel" style={{ padding: 24 }}>
            <p className="section-copy">Loading contract room...</p>
          </section>
        ) : error ? (
          <section className="panel" style={{ padding: 24 }}>
            <p className="form-error">{error}</p>
          </section>
        ) : room ? (
          <div className="room-grid">
            <section className="panel" style={{ padding: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <div className="pill">Shared room</div>
                  <h2 style={{ marginBottom: 8 }}>{room.title}</h2>
                  <p style={{ color: "var(--muted)", margin: 0 }}>
                    Client ID: {room.client_id} | Freelancer ID: {room.freelancer_id}
                  </p>
                </div>
                <div>
                  <span className={`status ${room.status}`}>{room.status}</span>
                </div>
              </div>
              <div className="message-stack" style={{ marginTop: 20 }}>
                {room.messages.length === 0 ? (
                  <div className="list-card">
                    <strong>No messages yet</strong>
                    <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                      Start the collaboration with a message so both sides can coordinate work and money in one place.
                    </p>
                  </div>
                ) : (
                  room.messages.map((item) => {
                    const mine = item.sender_id === currentUserId;
                    return (
                      <article key={item.id} className={`message-bubble ${mine ? "mine" : "theirs"}`}>
                        <strong>{mine ? "You" : "Counterparty"}</strong>
                        <p style={{ marginBottom: 8 }}>{item.body}</p>
                        <small>
                          {new Date(item.created_at).toLocaleString()} {mine && item.seen_by_other_party ? "| Seen" : ""}
                        </small>
                      </article>
                    );
                  })
                )}
              </div>
              <form className="form-grid" style={{ marginTop: 18 }} onSubmit={sendMessage}>
                <textarea placeholder="Message the other party" rows={4} value={message} onChange={(event) => setMessage(event.target.value)} />
                <button className="primary-button" type="submit" disabled={isSending}>
                  {isSending ? "Sending..." : "Send message"}
                </button>
              </form>
            </section>
            <div className="content-stack">
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Milestones and money</h2>
                <div className="card-list">
                  {room.milestones.map((item) => {
                    const remaining = Math.max(item.amount - item.released_amount, 0);
                    return (
                      <article key={item.id} className="list-card">
                        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                          <strong>{item.title}</strong>
                          <span className={`status ${item.status}`}>{item.status}</span>
                        </div>
                        <p style={{ color: "var(--muted)" }}>
                          Amount {item.amount.toFixed(2)} | Funded {item.funded_amount.toFixed(2)} | Released {item.released_amount.toFixed(2)}
                        </p>
                        <div className="action-row">
                          {room.current_user_role === "client" && item.status === "pending_funding" && (
                            <button className="secondary-button" type="button" onClick={() => void fundMilestone(item.id)}>
                              Fund escrow
                            </button>
                          )}
                          {room.current_user_role === "freelancer" && item.status === "funded" && (
                            <button className="secondary-button" type="button" onClick={() => void submitMilestone(item.id)}>
                              Submit delivery
                            </button>
                          )}
                          {room.current_user_role === "client" && item.status === "submitted" && remaining > 0 && (
                            <button className="secondary-button" type="button" onClick={() => void approveMilestone(item)}>
                              Release funds
                            </button>
                          )}
                          {item.status !== "released" && (
                            <button className="secondary-button" type="button" onClick={() => void disputeMilestone(item.id)}>
                              Open dispute
                            </button>
                          )}
                        </div>
                      </article>
                    );
                  })}
                </div>
              </section>
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Room controls</h2>
                <div className="form-grid">
                  <textarea placeholder="Reason for pause or resume" rows={3} value={pauseReason} onChange={(event) => setPauseReason(event.target.value)} />
                  <div className="action-row">
                    <button className="secondary-button" type="button" onClick={() => void changeContractState("pause")}>
                      Pause contract
                    </button>
                    <button className="secondary-button" type="button" onClick={() => void changeContractState("resume")}>
                      Resume contract
                    </button>
                  </div>
                </div>
              </section>
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Activity feed</h2>
                <div className="card-list">
                  {room.activities.map((item) => (
                    <article key={item.id} className="list-card">
                      <strong>{item.event_type}</strong>
                      <p style={{ color: "var(--muted)", margin: "8px 0" }}>{item.summary}</p>
                      <small>{new Date(item.created_at).toLocaleString()}</small>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          </div>
        ) : null}
      </DashboardShell>
    </ProtectedPage>
  );
}