"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/components/auth-provider";

export function TopNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { session, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push("/auth/login");
  };

  return (
    <header className="top-nav">
      <div className="container">
        <div className="panel top-nav-inner">
          <Link href="/" className="brand">
            Escrow Dex
          </Link>
          <nav className="nav-links">
            <Link className="pill" href="/">
              Home
            </Link>
            {session ? (
              <>
                <Link className="pill" href="/rooms" prefetch={false}>
                  Rooms
                </Link>
                <span className="pill">
                  {session.user.role} | {session.user.email}
                </span>
                <button className="secondary-button nav-button" type="button" onClick={handleLogout}>
                  Sign out
                </button>
              </>
            ) : (
              <>
                {pathname !== "/auth/login" && (
                  <Link className="pill" href="/auth/login" prefetch={false}>
                    Sign in
                  </Link>
                )}
                {pathname !== "/auth/register" && (
                  <Link className="pill" href="/auth/register" prefetch={false}>
                    Register
                  </Link>
                )}
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
