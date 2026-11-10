import { useCallback, useEffect, useState } from "react";
import { getMe, logoutUser } from "./api/auth";
import { ApiError, clearToken } from "./api/client";
import type { User } from "./api/types";
import AuthDialog from "./components/AuthDialog";
import Dashboard from "./pages/Dashboard";
import { getErrorMessage } from "./utils/format";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "register" | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [sessionMessage, setSessionMessage] = useState("");
  useEffect(() => {
    let active = true;
    getMe()
      .then((profile) => {
        if (active) setUser(profile);
      })
      .catch((error) => {
        if (active && !(error instanceof ApiError && error.status === 401))
          setSessionMessage(getErrorMessage(error));
      })
      .finally(() => {
        if (active) setRestoring(false);
      });
    const expired = () => {
      setUser(null);
      setSessionMessage("Your session has expired. Sign in to continue.");
    };
    window.addEventListener("exchange:session-expired", expired);
    return () => {
      active = false;
      window.removeEventListener("exchange:session-expired", expired);
    };
  }, []);
  const refreshUser = useCallback(async () => {
    try {
      setUser(await getMe());
    } catch (error) {
      setSessionMessage(getErrorMessage(error));
    }
  }, []);
  async function logout() {
    try {
      await logoutUser();
    } catch {
      setSessionMessage(
        "Signed out on this device. The server could not be reached.",
      );
    } finally {
      clearToken();
      setUser(null);
    }
  }
  return (
    <>
      <Dashboard
        user={user}
        restoring={restoring}
        onAuth={(mode = "login") => setAuthMode(mode)}
        onLogout={logout}
        onRefreshUser={refreshUser}
        sessionMessage={sessionMessage}
        onDismissMessage={() => setSessionMessage("")}
      />
      {authMode && (
        <AuthDialog
          initialMode={authMode}
          onClose={() => setAuthMode(null)}
          onSuccess={(profile) => {
            setUser(profile);
            setAuthMode(null);
            setSessionMessage("");
          }}
        />
      )}
    </>
  );
}
