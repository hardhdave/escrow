"use client";

import { useParams, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { DashboardShell } from "@/components/dashboard-shell";
import { ProtectedPage } from "@/components/protected-page";
import { fetchApi } from "@/lib/api";

type Message = {
  id: string;
  sender_id: string;
  body: string;
  created_at: string;
};

type Activity = {
  id: string;
  event_type: string;
  summary: string;
  created_at: string;
};

type Room = {
  room_code: string;
  title: string;
  status: string;
  currency: string;
  client_id: string | null;
  freelancer_id: string | null;
  current_user_role: "client" | "freelancer";
  hold_amount: number;
  released_amount: number;
  remaining_hold_amount: number;
  refund_status: string;
  refund_note: string | null;
  messages: Message[];
  activities: Activity[];
};

type StripeCheckoutResponse = {
  checkout_url: string;
  provider_session_id: string;
};

export default function RoomPage() {
  const params = useParams<{ code: string }>();
  const searchParams = useSearchParams();
  const { session } = useAuth();
  const [room, setRoom] = useState<Room | null>(null);
  const [message, setMessage] = useState("");
  const [holdAmount, setHoldAmount] = useState("500");
  const [releaseAmount, setReleaseAmount] = useState("500");
  const [refundNote, setRefundNote] = useState("");
  const [disputeNote, setDisputeNote] = useState("");
  const [error, setError] = useState<string | null>(null);

  const roomCode = typeof params.code === "string" ? params.code : "";
  const sessionId = searchParams.get("session_id");

  const authHeaders = useMemo(() => {
    if (!session) {
      return {};
    }
    return {
      Authorization: `Bearer ${session.accessToken}`
    };
  }, [session]);

  async function loadRoom() {
    if (!session || !roomCode) {
      return;
    }

    const result = await fetchApi<Room>(`/rooms/${roomCode}`, {
      headers: authHeaders
    });
    setRoom(result.data);
    setError(result.error);
  }

  useEffect(() => {
    void loadRoom();
  }, [roomCode, session]);

  useEffect(() => {
    async function confirmStripeHold() {
      if (!session || !roomCode || !sessionId) {
        return;
      }

      const result = await fetchApi<Room>(`/rooms/${roomCode}/stripe-confirm?session_id=${encodeURIComponent(sessionId)}`, {
        method: "POST",
        headers: authHeaders
      });
      if (result.error) {
        setError(result.error);
        return;
      }
      setRoom(result.data);
    }

    void confirmStripeHold();
  }, [roomCode, session, sessionId]);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await fetchApi<Room>(`/rooms/${roomCode}/messages`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ body: message })
    });
    if (result.error) {
      setError(result.error);
      return;
    }
    setMessage("");
    setRoom(result.data);
  }

  async function startStripeHold() {
    const result = await fetchApi<StripeCheckoutResponse>(`/rooms/${roomCode}/stripe-checkout`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ amount: Number(holdAmount) })
    });
    if (result.error || !result.data) {
      setError(result.error ?? "Unable to start Stripe checkout");
      return;
    }
    window.location.href = result.data.checkout_url;
  }

  async function releaseMoney() {
    const result = await fetchApi<Room>(`/rooms/${roomCode}/release`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ amount: Number(releaseAmount), note: "Client released money after completion." })
    });
    if (result.error) {
      setError(result.error);
      return;
    }
    setRoom(result.data);
  }

  async function requestRefund() {
    const result = await fetchApi<Room>(`/rooms/${roomCode}/refund-request`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ amount: room?.remaining_hold_amount ?? 0, note: refundNote || "Client requested refund." })
    });
    if (result.error) {
      setError(result.error);
      return;
    }
    setRoom(result.data);
  }

  async function decideRefund(approve: boolean) {
    const result = await fetchApi<Room>(`/rooms/${roomCode}/refund-decision`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ approve, note: refundNote || (approve ? "Refund approved." : "Refund rejected; dispute required.") })
    });
    if (result.error) {
      setError(result.error);
      return;
    }
    setRoom(result.data);
  }

  async function openDispute() {
    const result = await fetchApi<Room>(`/rooms/${roomCode}/dispute`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({ body: disputeNote || "Service delivery and client acceptance are contested. Funds remain frozen pending admin review." })
    });
    if (result.error) {
      setError(result.error);
      return;
    }
    setRoom(result.data);
  }

  return (
    <ProtectedPage>
      <DashboardShell
        active="rooms"
        title={room ? `${room.title} | ${room.room_code}` : "Room"}
        subtitle="Both client and freelancer can create rooms. The code is unique. Messages stay in the room, Stripe funds the hold, the client releases money, and the client cannot take held money back without freelancer permission."
      >
        {error && (
          <section className="panel" style={{ padding: 24 }}>
            <p className="form-error">{error}</p>
          </section>
        )}
        {room && (
          <div className="room-grid">
            <section className="panel" style={{ padding: 24 }}>
              <div className="card-list">
                <article className="list-card">
                  <strong>Room code</strong>
                  <p style={{ color: "var(--muted)", marginBottom: 0 }}>{room.room_code}</p>
                </article>
                <article className="list-card">
                  <strong>Participants</strong>
                  <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                    Client {room.client_id ?? "waiting"} | Freelancer {room.freelancer_id ?? "waiting"}
                  </p>
                </article>
                <article className="list-card">
                  <strong>Escrow state</strong>
                  <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                    Status {room.status} | On hold {room.currency} {room.hold_amount.toFixed(2)} | Released {room.currency} {room.released_amount.toFixed(2)} | Remaining hold {room.currency} {room.remaining_hold_amount.toFixed(2)}
                  </p>
                </article>
                <article className="list-card">
                  <strong>Refund rule</strong>
                  <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                    Client cannot pull held money back alone. Refund status: {room.refund_status}. Note: {room.refund_note ?? "none"}
                  </p>
                </article>
              </div>
              <div className="message-stack" style={{ marginTop: 20 }}>
                {room.messages.map((item) => (
                  <article key={item.id} className={`message-bubble ${item.sender_id === session?.user.id ? "mine" : "theirs"}`}>
                    <strong>{item.sender_id === session?.user.id ? "You" : "Counterparty"}</strong>
                    <p style={{ marginBottom: 8 }}>{item.body}</p>
                    <small>{new Date(item.created_at).toLocaleString()}</small>
                  </article>
                ))}
              </div>
              <form className="form-grid" style={{ marginTop: 18 }} onSubmit={sendMessage}>
                <textarea placeholder="Send a message in this room" rows={4} value={message} onChange={(event) => setMessage(event.target.value)} />
                <button className="primary-button" type="submit">
                  Send message
                </button>
              </form>
            </section>
            <div className="content-stack">
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Payment hold through Stripe</h2>
                <div className="form-grid">
                  {room.current_user_role === "client" && (
                    <>
                      <input type="number" min="1" step="1" value={holdAmount} onChange={(event) => setHoldAmount(event.target.value)} />
                      <button className="secondary-button" type="button" onClick={startStripeHold}>
                        Put money on hold with Stripe
                      </button>
                    </>
                  )}
                  <p className="section-copy" style={{ margin: 0 }}>
                    Stripe collects the payment. After payment succeeds, the money is marked on hold inside this room.
                  </p>
                  <p style={{ margin: 0, color: "var(--muted)", fontSize: 14 }}>
                    * For now there is no live payment run because the Razorpay or Stripe subscription is out of time.
                  </p>
                </div>
              </section>
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Release and refund rules</h2>
                <div className="form-grid">
                  {room.current_user_role === "client" && (
                    <>
                      <input type="number" min="1" step="1" value={releaseAmount} onChange={(event) => setReleaseAmount(event.target.value)} />
                      <button className="secondary-button" type="button" onClick={releaseMoney}>
                        Release money to freelancer
                      </button>
                    </>
                  )}
                  <textarea placeholder="Refund note" rows={3} value={refundNote} onChange={(event) => setRefundNote(event.target.value)} />
                  {room.current_user_role === "client" && room.remaining_hold_amount > 0 && (
                    <button className="secondary-button" type="button" onClick={requestRefund}>
                      Request money back from held amount
                    </button>
                  )}
                  {room.current_user_role === "freelancer" && room.refund_status === "requested" && (
                    <div className="action-row">
                      <button className="secondary-button" type="button" onClick={() => void decideRefund(true)}>
                        Approve refund
                      </button>
                      <button className="secondary-button" type="button" onClick={() => void decideRefund(false)}>
                        Reject refund and lock dispute
                      </button>
                    </div>
                  )}
                </div>
              </section>
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Deadlock handling</h2>
                <p className="section-copy">
                  If freelancer says service was provided and client says it was not received, open dispute. Held money stays frozen until admin resolution.
                </p>
                <textarea placeholder="Dispute note" rows={3} value={disputeNote} onChange={(event) => setDisputeNote(event.target.value)} />
                <div style={{ marginTop: 12 }}>
                  <button className="secondary-button" type="button" onClick={openDispute}>
                    Open dispute
                  </button>
                </div>
              </section>
              <section className="panel" style={{ padding: 24 }}>
                <h2 style={{ marginTop: 0 }}>Activity</h2>
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
        )}
      </DashboardShell>
    </ProtectedPage>
  );
}
