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
      // redirect or load user context
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-shell fade-in">
      <section className="login-hero">
        <div className="hero-orb orb-one" aria-hidden="true"></div>
        <div className="hero-orb orb-two" aria-hidden="true"></div>
        <div className="brand">
          <div className="brand-mark">TE</div>
          <div>
            <p className="brand-name">Trading Engine</p>
            <p className="brand-tag">Precision order flow</p>
          </div>
        </div>
        <h1>Trade with a clear signal.</h1>
        <p className="hero-copy">
          Track inventory, spot market moves, and act fast with your command
          center for digital assets.
        </p>
        <div className="hero-grid">
          <div className="hero-card">
            <span className="eyebrow">Inventory</span>
            <p>Instant visibility into every holding.</p>
          </div>
          <div className="hero-card">
            <span className="eyebrow">Entities</span>
            <p>Scan market listings and rarity tiers.</p>
          </div>
          <div className="hero-card">
            <span className="eyebrow">Orders</span>
            <p>Place, track, and manage open orders.</p>
          </div>
        </div>
      </section>

      <section className="login-card">
        <div className="card-header">
          <p className="eyebrow">Member access</p>
          <h2>Sign in</h2>
          <p className="subtitle">Use your Trading Engine account.</p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}

          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your handle"
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
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </section>
    </div>
  );
}
