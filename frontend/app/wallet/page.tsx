"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { DashboardShell } from "@/components/dashboard-shell";
import { ProtectedPage } from "@/components/protected-page";
import { fetchApi } from "@/lib/api";

type WalletSummary = {
  currency: string;
  available_balance: number;
  pending_balance: number;
  reserve_balance: number;
};

export default function WalletPage() {
  const { session } = useAuth();
  const [wallet, setWallet] = useState<WalletSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadWallet() {
      if (!session) {
        return;
      }

      const result = await fetchApi<WalletSummary>("/wallets/me", {
        headers: {
          Authorization: `Bearer ${session.accessToken}`
        }
      });

      setWallet(result.data);
      setError(result.error);
      setIsLoading(false);
    }

    void loadWallet();
  }, [session]);

  return (
    <ProtectedPage>
      <DashboardShell
        active="wallet"
        title="Wallet and money movement"
        subtitle="This page now asks the backend for the signed-in user's wallet instead of showing fake balances to everyone."
      >
        <section className="panel" style={{ padding: 24 }}>
          {isLoading ? (
            <p className="section-copy">Loading wallet balances...</p>
          ) : error ? (
            <div className="list-card">
              <strong>Wallet unavailable</strong>
              <p style={{ color: "var(--muted)", marginBottom: 0 }}>{error}</p>
            </div>
          ) : wallet ? (
            <div className="grid three-col">
              <article className="panel metric">
                <span className="pill">Available</span>
                <h2 style={{ margin: "14px 0 0", fontSize: 40 }}>
                  {wallet.currency} {wallet.available_balance.toFixed(2)}
                </h2>
                <p>Withdrawable balance for the authenticated account.</p>
              </article>
              <article className="panel metric">
                <span className="pill">Pending</span>
                <h2 style={{ margin: "14px 0 0", fontSize: 40 }}>
                  {wallet.currency} {wallet.pending_balance.toFixed(2)}
                </h2>
                <p>Funds waiting on release windows, review, or hold periods.</p>
              </article>
              <article className="panel metric">
                <span className="pill">Reserve</span>
                <h2 style={{ margin: "14px 0 0", fontSize: 40 }}>
                  {wallet.currency} {wallet.reserve_balance.toFixed(2)}
                </h2>
                <p>Risk reserve retained by the platform if applicable.</p>
              </article>
            </div>
          ) : (
            <p className="section-copy">No wallet data returned yet.</p>
          )}
        </section>
      </DashboardShell>
    </ProtectedPage>
  );
}
