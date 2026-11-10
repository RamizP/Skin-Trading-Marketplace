import { useEffect, useState } from "react";
import { claimFreeCase } from "../api/cases";
import { API_URL, ApiError } from "../api/client";
import type { CaseReward, Entity, User } from "../api/types";
import { getErrorMessage } from "../utils/format";
import { ErrorNotice } from "./Feedback";
import Icon from "./Icon";

export default function FreeCaseClaim({
  user,
  catalog,
  onAuth,
  onChanged,
  onInventory,
}: {
  user: User | null;
  catalog: Entity[];
  onAuth: () => void;
  onChanged: (message?: string) => Promise<void>;
  onInventory: () => void;
}) {
  // This is only a display hint. The API always decides whether a claim is allowed.
  const storageKey = `exchange.free-case:${API_URL}:${user?.id ?? "guest"}`;
  const [deadline, setDeadline] = useState(() => {
    const stored = Number(sessionStorage.getItem(storageKey));
    return Number.isFinite(stored) ? stored : 0;
  });
  const [now, setNow] = useState(Date.now);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reward, setReward] = useState<CaseReward | null>(null);
  const remaining = Math.max(0, Math.ceil((deadline - now) / 1000));
  const cooling = remaining > 0;
  const countdown = `${Math.floor(remaining / 60)
    .toString()
    .padStart(2, "0")}:${(remaining % 60).toString().padStart(2, "0")}`;
  const name = reward
    ? catalog.find((entity) => entity.id === reward.entity_id)?.name || "a case"
    : "";

  useEffect(() => {
    if (!cooling) return;
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [cooling]);

  function rememberCooldown(seconds: number) {
    const timestamp = Date.now();
    const next = timestamp + Math.max(0, Math.ceil(seconds)) * 1000;
    setNow(timestamp);
    setDeadline(next);
    sessionStorage.setItem(storageKey, String(next));
  }

  async function claim() {
    if (!user) {
      onAuth();
      return;
    }
    if (busy || cooling) return;
    setBusy(true);
    setError("");
    try {
      const result = await claimFreeCase();
      setReward(result);
      rememberCooldown(15 * 60);
      await onChanged("Free case claimed. It is now in your inventory.");
    } catch (reason) {
      if (reason instanceof ApiError && [400, 429].includes(reason.status)) {
        const detail = reason.detail;
        if (
          typeof detail === "object" &&
          detail !== null &&
          "remaining_seconds" in detail &&
          typeof detail.remaining_seconds === "number" &&
          Number.isFinite(detail.remaining_seconds) &&
          detail.remaining_seconds >= 0
        ) {
          rememberCooldown(detail.remaining_seconds);
          return;
        }
      }
      setError(getErrorMessage(reason));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="free-case-banner" aria-label="Free case">
      <div className="free-case-icon">
        <Icon name="case" size={28} />
      </div>
      <div className="free-case-copy">
        <span className="eyebrow">A LITTLE SOMETHING, EVERY 15 MINUTES</span>
        <h2>Your next case is on us.</h2>
        <p>
          Claim a random case for free. Keep it, trade it, or open it whenever
          you like.
        </p>
        {reward && (
          <p className="free-case-success" role="status">
            <Icon name="check" size={14} />
            Added {name} to your inventory.
          </p>
        )}
      </div>
      <div className="free-case-actions">
        <button
          className="button button-primary"
          aria-label={user ? "Claim free case" : "Sign in to claim a free case"}
          disabled={busy || cooling}
          onClick={claim}
        >
          <Icon name={cooling ? "lock" : "plus"} size={16} />
          {busy
            ? "Claiming…"
            : !user
              ? "Sign in to claim"
              : cooling
                ? `Available in ${countdown}`
                : "Claim free case"}
        </button>
        {user && cooling ? (
          <button className="text-button" onClick={onInventory}>
            View inventory
            <Icon name="arrow" size={13} />
          </button>
        ) : (
          <span className="small-muted">One case. Yours to keep.</span>
        )}
      </div>
      {error && (
        <div className="free-case-error">
          <ErrorNotice message={error} />
        </div>
      )}
    </section>
  );
}
