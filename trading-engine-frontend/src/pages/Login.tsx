import { useState } from "react";
import { loginUser } from "../api/auth";
import "../styles/Login.css";

type LoginProps = {
  onLogin?: () => void | Promise<void>;
};

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await loginUser(username, password);
      if (onLogin) {
        await onLogin();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-layout fade-in">
      <section className="login-hero">
        <div className="hero-glow" aria-hidden="true"></div>
        <div className="hero-scan" aria-hidden="true"></div>
        <header className="brandline">
          <div className="brand-mark">TE</div>
          <div>
            <p className="brand-name">Trading Engine</p>
            <p className="brand-tag">Realtime execution hub</p>
          </div>
        </header>

        <h1>Operate the market with clarity.</h1>
        <p className="hero-copy">
          A sharp command deck for inventory, orders, and the live entity market.
          Built for focus, speed, and decisive moves.
        </p>

        <div className="signal-grid">
          <div className="signal-card">
            <span className="signal-label">Open Orders</span>
            <strong>142</strong>
            <p>Auto-sorted by spread and velocity.</p>
          </div>
          <div className="signal-card">
            <span className="signal-label">Live Entities</span>
            <strong>9.4k</strong>
            <p>Filter by rarity, wear, and pricing gaps.</p>
          </div>
          <div className="signal-card">
            <span className="signal-label">Portfolio Value</span>
            <strong>$58.3k</strong>
            <p>Precision balance with instant top-ups.</p>
          </div>
        </div>

        <div className="ticker">
          <span>Engine Status</span>
          <span className="ticker-dot"></span>
          <span>Stable · 32ms latency · 99.9% uptime</span>
        </div>
      </section>

      <section className="login-form">
        <div className="form-shell">
          <div className="form-header">
            <p className="eyebrow">Secure access</p>
            <h2>Sign in</h2>
            <p className="muted">Enter your credentials to launch the desk.</p>
          </div>

          <form onSubmit={handleSubmit}>
            {error && <div className="error">{error}</div>}

            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                placeholder="Trader handle"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Authenticating..." : "Enter Trading Engine"}
            </button>
          </form>

          <div className="trust-row">
            <span>Encrypted sessions</span>
            <span>Audit-ready logs</span>
            <span>Role-based access</span>
          </div>
        </div>
      </section>
    </div>
  );
}
