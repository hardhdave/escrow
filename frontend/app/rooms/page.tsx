"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { DashboardShell } from "@/components/dashboard-shell";
import { ProtectedPage } from "@/components/protected-page";
import { fetchApi } from "@/lib/api";

type RoomListItem = {
  room_code: string;
  title: string;
  status: string;
  current_user_role: string;
  counterparty_connected: boolean;
  hold_amount: number;
  released_amount: number;
};

type RoomResponse = {
  room_code: string;
};

export default function RoomsPage() {
  const router = useRouter();
  const { session } = useAuth();
  const [rooms, setRooms] = useState<RoomListItem[]>([]);
  const [title, setTitle] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function loadRooms() {
    if (!session) {
      return;
    }

    const result = await fetchApi<RoomListItem[]>("/rooms", {
      headers: {
        Authorization: `Bearer ${session.accessToken}`
      }
    });
    setRooms(result.data ?? []);
  }

  useEffect(() => {
    void loadRooms();
  }, [session]);

  async function createRoom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session) {
      return;
    }

    const result = await fetchApi<RoomResponse>("/rooms", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.accessToken}`
      },
      body: JSON.stringify({ title, currency: "USD" })
    });

    if (result.error || !result.data) {
      setError(result.error ?? "Unable to create room");
      return;
    }

    setTitle("");
    router.push(`/rooms/${result.data.room_code}`);
  }

  async function joinRoom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session) {
      return;
    }

    const result = await fetchApi<RoomResponse>("/rooms/join", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.accessToken}`
      },
      body: JSON.stringify({ room_code: joinCode })
    });

    if (result.error || !result.data) {
      setError(result.error ?? "Unable to join room");
      return;
    }

    setJoinCode("");
    router.push(`/rooms/${result.data.room_code}`);
  }

  return (
    <ProtectedPage>
      <DashboardShell
        active="rooms"
        title="Escrow rooms"
        subtitle="Client or freelancer can create a room. The room code is auto-generated and unique. The other party joins with that code."
      >
        <section className="panel" style={{ padding: 24 }}>
          <div className="grid two-col">
            <form className="form-grid" onSubmit={createRoom}>
              <strong>Create room</strong>
              <input placeholder="Project title" value={title} onChange={(event) => setTitle(event.target.value)} required />
              <button className="primary-button" type="submit">
                Create room
              </button>
            </form>
            <form className="form-grid" onSubmit={joinRoom}>
              <strong>Join room by code</strong>
              <input placeholder="Room code" value={joinCode} onChange={(event) => setJoinCode(event.target.value.toUpperCase())} required />
              <button className="secondary-button" type="submit">
                Join room
              </button>
            </form>
          </div>
          {error && <p className="form-error" style={{ marginTop: 14 }}>{error}</p>}
        </section>
        <section className="panel" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Your rooms</h2>
          <div className="card-list">
            {rooms.length === 0 ? (
              <article className="list-card">
                <strong>No rooms yet</strong>
                <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                  Create a room and share the code with the other party.
                </p>
              </article>
            ) : (
              rooms.map((room) => (
                <Link key={room.room_code} href={`/rooms/${room.room_code}`} className="list-card room-link" prefetch={false}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                    <strong>{room.title}</strong>
                    <span className={`status ${room.status}`}>{room.status}</span>
                  </div>
                  <p style={{ color: "var(--muted)", marginBottom: 0 }}>
                    Code {room.room_code} | role {room.current_user_role} | both joined {room.counterparty_connected ? "yes" : "no"} | on hold {room.hold_amount.toFixed(2)} | released {room.released_amount.toFixed(2)}
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
