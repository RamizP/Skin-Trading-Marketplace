import { useState } from "react";
import type { FormEvent } from "react";
import { getMe, loginUser, registerUser } from "../api/auth";
import type { User } from "../api/types";
import { getErrorMessage } from "../utils/format";
import { ErrorNotice } from "./Feedback";
import Icon from "./Icon";
import Modal from "./Modal";

export default function AuthDialog({
  initialMode,
  onClose,
  onSuccess,
}: {
  initialMode: "login" | "register";
  onClose: () => void;
  onSuccess: (user: User) => void;
}) {
  const [mode, setMode] = useState(initialMode);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setError("");
    if (new TextEncoder().encode(password).length > 72) {
      setError("Use a password of at most 72 UTF-8 bytes.");
      return;
    }
    if (mode === "register" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setBusy(true);
    try {
      if (mode === "login") await loginUser(username.trim(), password);
      else await registerUser(username.trim(), email.trim(), password);
      onSuccess(await getMe());
    } catch (reason) {
      setError(getErrorMessage(reason));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal
      title={mode === "login" ? "Welcome back." : "Make your first move."}
      onClose={onClose}
      busy={busy}
    >
      <div className="auth-intro">
        <span className="brand-symbol">
          <Icon name="bolt" size={24} />
        </span>
        <p>
          {mode === "login"
            ? "Your collection. Your next trade. All in one place."
            : "Create an account and start building your collection."}
        </p>
      </div>
      <form className="stack-form" onSubmit={submit}>
        {error && <ErrorNotice message={error} />}
        <label>
          Username
          <input
            autoComplete="username"
            required
            minLength={mode === "register" ? 3 : 1}
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="Your player name"
          />
        </label>
        {mode === "register" && (
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
          </label>
        )}
        <label>
          Password
          <div className="password-field">
            <input
              type={showPassword ? "text" : "password"}
              autoComplete={
                mode === "login" ? "current-password" : "new-password"
              }
              required
              minLength={mode === "register" ? 8 : 1}
              maxLength={72}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder={
                mode === "register" ? "At least 8 characters" : "Your password"
              }
            />
            <button
              type="button"
              className="icon-button"
              aria-label={showPassword ? "Hide password" : "Show password"}
              onClick={() => setShowPassword(!showPassword)}
            >
              <Icon name="eye" size={18} />
            </button>
          </div>
        </label>
        {mode === "register" && (
          <label>
            Confirm password
            <input
              type="password"
              autoComplete="new-password"
              required
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="One more time"
            />
          </label>
        )}
        <button className="button button-primary button-full" disabled={busy}>
          {busy
            ? "Connecting…"
            : mode === "login"
              ? "Sign in"
              : "Create account"}
          <Icon name="arrow" size={17} />
        </button>
      </form>
      <p className="auth-switch">
        {mode === "login" ? "New to the exchange?" : "Already have an account?"}{" "}
        <button
          className="text-button"
          disabled={busy}
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError("");
          }}
        >
          {mode === "login" ? "Create an account" : "Sign in"}
        </button>
      </p>
    </Modal>
  );
}
