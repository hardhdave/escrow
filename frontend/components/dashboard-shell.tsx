import Link from "next/link";

type DashboardShellProps = {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  active: "dashboard" | "rooms" | "auth";
};

const items = [
  { href: "/dashboard", label: "Overview", key: "dashboard" },
  { href: "/rooms", label: "Rooms", key: "rooms" }
] as const;

export function DashboardShell({ title, subtitle, children, active }: DashboardShellProps) {
  return (
    <main className="container">
      <div className="split-layout">
        <aside className="panel sidebar">
          <div style={{ marginBottom: 18 }}>
            <div className="pill">Escrow workspace</div>
          </div>
          <nav>
            {items.map((item) => (
              <Link key={item.href} href={item.href} data-active={active === item.key} prefetch={false}>
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
        <section className="content-stack">
          <div className="panel" style={{ padding: 28 }}>
            <h1 className="section-title">{title}</h1>
            <p className="section-copy">{subtitle}</p>
          </div>
          {children}
        </section>
      </div>
    </main>
  );
}
