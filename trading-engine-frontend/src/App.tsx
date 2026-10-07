import { useState, useEffect } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import { getMe } from "./api/auth";
import type { User } from "./api/types";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  const refreshUser = async () => {
    try {
      const profile = await getMe();
      setUser(profile);
    } catch {
      setUser(null);
    }
  };

  useEffect(() => {
    refreshUser().finally(() => setLoading(false));
  }, []);

  const handleLogout = () => setUser(null);
  const handleLogin = async () => {
    setLoading(true);
    await refreshUser();
    setLoading(false);
  };

  if (loading) return <div className="app-loading fade-in">Loading Trading Engine...</div>;
  if (!user) {
    return showRegister ? (
      <Register onRegistered={handleLogin} onLogin={() => setShowRegister(false)} />
    ) : (
      <Login onLogin={handleLogin} onRegister={() => setShowRegister(true)} />
    );
  }

  return <Dashboard user={user} onLogout={handleLogout} onUserUpdate={setUser} />;
}
