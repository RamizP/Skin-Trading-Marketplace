import { useState } from "react";
import { loginUser } from "../api/auth";
import "../styles/Login.css";

export default function Login() {
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
      // redirect or load user context
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Sign in</h1>
        <p className="subtitle">Welcome back</p>

        <form onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}

          <div className="field">
            <input
              type="username"
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="field">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
