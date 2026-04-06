"use client";

import Link from "next/link";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/components/auth-provider";

export function ProtectedPage({ children }: { children: React.ReactNode }) {
  const { session, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !session) {
      router.replace(`/auth/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, pathname, router, session]);

  if (isLoading) {
    return (
      <main className="container" style={{ padding: "30px 0 50px" }}>
        <div className="panel" style={{ padding: 28 }}>
          <div className="pill">Checking session</div>
          <h1 className="section-title" style={{ marginTop: 18 }}>
            Loading your workspace
          </h1>
          <p className="section-copy">We are verifying your session before opening private pages.</p>
        </div>
      </main>
    );
  }

  if (!session) {
    return (
      <main className="container" style={{ padding: "30px 0 50px" }}>
        <div className="panel" style={{ padding: 28 }}>
          <div className="pill">Private workspace</div>
          <h1 className="section-title" style={{ marginTop: 18 }}>
            Sign in required
          </h1>
          <p className="section-copy">Dashboard, contracts, and wallet pages are only available after authentication.</p>
          <Link className="primary-button" href="/auth/login" prefetch={false}>
            Go to sign in
          </Link>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
