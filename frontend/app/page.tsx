import Link from "next/link";

export default function HomePage() {
  return (
    <main className="container">
      <section className="hero">
        <div className="hero-grid">
          <div className="panel hero-copy">
            <span className="pill">Room-code escrow workflow</span>
            <h1>Create a room. Join by code. Hold money safely in the middle.</h1>
            <p>
              Client creates a room and gets a code. Freelancer joins with the code. Client puts money on hold inside the app. When the job is done, client releases it. If they disagree, the money freezes into dispute.
            </p>
            <div className="hero-actions">
              <Link href="/rooms" className="primary-button">
                Open rooms
              </Link>
              <Link href="/auth/register" className="secondary-button">
                Create account
              </Link>
            </div>
          </div>
          <div className="panel hero-panel">
            <h2>Core rules</h2>
            <div className="list-card">Client cannot pull held money back alone.</div>
            <div className="list-card">Freelancer must approve refund of unreleased money.</div>
            <div className="list-card">If both sides disagree, money remains frozen until dispute resolution.</div>
          </div>
        </div>
      </section>
    </main>
  );
}
