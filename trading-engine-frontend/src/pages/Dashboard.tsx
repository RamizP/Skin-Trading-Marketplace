import { useEffect, useState } from "react";
import { getMe, logoutUser } from "../api/auth";
import InventoryTab from "./Inventory";
import EntitiesTab from "./Entities";
import "../styles/Dashboard.css";

export default function Dashboard({ onLogout }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("dashboard");

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => setError("You are not logged in"))
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    if (onLogout) onLogout();
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>Trading</h2>
        <nav>
          <ul>
            <li
              className={activeTab === "dashboard" ? "active" : ""}
              onClick={() => setActiveTab("dashboard")}
            >
              Dashboard
            </li>
            <li
              className={activeTab === "inventory" ? "active" : ""}
              onClick={() => setActiveTab("inventory")}
            >
              Inventory
            </li>
            <li
              className={activeTab === "entities" ? "active" : ""}
              onClick={() => setActiveTab("entities")}
            >
               Market
            </li>
          </ul>
        </nav>
      </aside>

<div className="main-content">
  <header>
    <h1>
      {activeTab === "dashboard"
        ? "Dashboard"
        : activeTab === "inventory"
        ? "Inventory"
        : "Entities"}
    </h1>
    <button onClick={handleLogout}>Logout</button>
  </header>

  {activeTab === "dashboard" && (
    <section className="cards">
      <div className="card">
        <h3>User Info</h3>
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Role:</strong> {user?.role}</p>
        <p><strong>ID:</strong> {user?.id}</p>
      </div>
      <div className="card">
        <h3>Balance</h3>
        <p><strong>Current Balance:</strong> ${user?.balance}</p>
        <button>Top Up</button>
      </div>
    </section>
  )}

  {activeTab === "inventory" && <InventoryTab />}

  {activeTab === "entities" && <EntitiesTab user={user} />}
</div>

    </div>
  );
}
