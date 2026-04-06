import "./globals.css";
import type { Metadata } from "next";

import { AuthProvider } from "@/components/auth-provider";
import { TopNav } from "@/components/top-nav";

export const metadata: Metadata = {
  title: "Escrow Dex",
  description: "Escrow-first freelance marketplace for serious client and freelancer collaboration."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <div className="page-shell">
            <TopNav />
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
