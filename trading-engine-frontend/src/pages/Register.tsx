import { useState } from "react";
import { registerUser } from "../api/auth";
import { getErrorMessage } from "../utils/format";
import "../styles/Login.css";

type RegisterProps = {
  onRegistered?: () => void | Promise<void>;
  onLogin?: () => void;
};

export default function Register({ onRegistered, onLogin }: RegisterProps) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      await registerUser(username, email, password);
      await onRegistered?.();
    } catch (err) {
      setError(getErrorMessage(err, "Could not create your account"));
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
          <p className="eyebrow">Join the Market</p>
          <h1>Build your trading desk.</h1>
          <p>
            Create an account to track inventory, compare prices, and place orders
            across the skin exchange.
          </p>
        </div>

        <div className="login-showcase" aria-hidden="true">
          <div className="showcase-item rare"><span>AK</span><strong>Neon Pattern</strong><small>Rare listings</small></div>
          <div className="showcase-item covert"><span>KN</span><strong>Crimson Edge</strong><small>Private inventory</small></div>
          <div className="showcase-item restricted"><span>AWP</span><strong>Arctic Rail</strong><small>Live orders</small></div>
        </div>
      </section>

      <section className="login-form">
        <div className="form-shell">
          <div className="form-header">
            <p className="eyebrow">New Account</p>
            <h2>Create account</h2>
            <p className="muted">Set up your trading identity in seconds.</p>
          </div>

          <form onSubmit={handleSubmit}>
            {error && <div className="error">{error}</div>}

            <label className="field" htmlFor="register-username">
              <span>Username</span>
              <input id="register-username" type="text" placeholder="Trader handle" value={username} onChange={(event) => setUsername(event.target.value)} minLength={3} required />
            </label>

            <label className="field" htmlFor="register-email">
              <span>Email</span>
              <input id="register-email" type="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </label>

            <label className="field" htmlFor="register-password">
              <span>Password</span>
              <input id="register-password" type="password" placeholder="At least 8 characters" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required />
            </label>

            <label className="field" htmlFor="confirm-password">
              <span>Confirm password</span>
              <input id="confirm-password" type="password" placeholder="Repeat your password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} minLength={8} required />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Creating account" : "Create account"}
            </button>
          </form>

          <p className="form-switch">
            Already have an account?{" "}
            <button type="button" className="text-button" onClick={onLogin}>Sign in</button>
          </p>
        </div>
      </section>
    </main>
  );
}
