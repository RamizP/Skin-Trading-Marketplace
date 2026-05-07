import { useState } from "react";
import { loginUser } from "../api/auth";
import { getErrorMessage } from "../utils/format";
import "../styles/Login.css";

type LoginProps = {
  onLogin?: () => void | Promise<void>;
};

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      await loginUser(username, password);
      await onLogin?.();
    } catch (err) {
      setError(getErrorMessage(err, "Invalid credentials"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-layout fade-in">
      <section className="login-market">
        <header className="brandline">
          <div className="brand-mark">TE</div>
          <div>
            <p className="brand-name">Trading Engine</p>
            <p className="brand-tag">CS-style skin market</p>
          </div>
        </header>

        <div className="login-copy">
          <p className="eyebrow">Market Access</p>
          <h1>Enter the skin exchange.</h1>
          <p>
            Browse listed items, compare floor prices, manage inventory, and trade
            from one dark market desk.
          </p>
        </div>

        <div className="login-showcase" aria-hidden="true">
          <div className="showcase-item rare">
            <span>AK</span>
            <strong>Neon Pattern</strong>
            <small>$418.90</small>
          </div>
          <div className="showcase-item covert">
            <span>KN</span>
            <strong>Crimson Edge</strong>
            <small>$1,240.00</small>
          </div>
          <div className="showcase-item restricted">
            <span>AWP</span>
            <strong>Arctic Rail</strong>
            <small>$89.50</small>
          </div>
        </div>
      </section>

      <section className="login-form">
        <div className="form-shell">
          <div className="form-header">
            <p className="eyebrow">Secure Access</p>
            <h2>Sign in</h2>
            <p className="muted">Use your trading account to open the market.</p>
          </div>

          <form onSubmit={handleSubmit}>
            {error && <div className="error">{error}</div>}

            <label className="field" htmlFor="username">
              <span>Username</span>
              <input
                id="username"
                type="text"
                placeholder="Trader handle"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />
            </label>

            <label className="field" htmlFor="password">
              <span>Password</span>
              <input
                id="password"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Authenticating" : "Open Market"}
            </button>
          </form>

          <div className="trust-row">
            <span>Cookie sessions</span>
            <span>Role access</span>
            <span>Live orders</span>
          </div>
        </div>
      </section>
    </main>
  );
}
