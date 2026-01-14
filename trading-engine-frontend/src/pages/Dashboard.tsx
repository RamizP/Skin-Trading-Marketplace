import { useState } from "react";
import { chargeBalance, logoutUser } from "../api/auth";
import InventoryTab from "./Inventory";
import EntitiesTab from "./Entities";
import OrdersTab from "./Orders";
import "../styles/Dashboard.css";

type DashboardProps = {
  user: any;
  onLogout?: () => void;
  onUserUpdate?: (user: any) => void;
};

export default function Dashboard({ user, onLogout, onUserUpdate }: DashboardProps) {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [topUpAmount, setTopUpAmount] = useState("");
  const [topUpError, setTopUpError] = useState("");
  const [topUpLoading, setTopUpLoading] = useState(false);

  const displayName = user?.username || user?.email || "Trader";
  const balance = Number(user?.balance ?? 0);
  const balanceDisplay = Number.isFinite(balance)
    ? balance.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    : "0.00";
  const tabTitle =
    activeTab === "dashboard"
      ? "Dashboard"
      : activeTab === "inventory"
      ? "Inventory"
      : activeTab === "orders"
      ? "Orders"
      : "Market";
  const tabSubtitle =
    activeTab === "dashboard"
      ? "Monitor account status, balances, and quick insights."
      : activeTab === "inventory"
      ? "Review your holdings, rarity tiers, and sale status."
      : activeTab === "orders"
      ? "Create buy/sell orders and act on market listings."
      : "Explore available entities and current pricing.";

  const handleLogout = async () => {
    await logoutUser();
    if (onLogout) onLogout();
  };

  const handleTopUp = async () => {
    const amount = Number(topUpAmount);
    if (!Number.isFinite(amount) || amount <= 0 || !Number.isInteger(amount)) {
      setTopUpError("Enter a whole number amount.");
      return;
    }

    setTopUpLoading(true);
    setTopUpError("");
    try {
      const updated = await chargeBalance(amount);
      if (onUserUpdate) {
        onUserUpdate(updated);
      }
      setTopUpAmount("");
    } catch (err) {
      setTopUpError(err.message);
    } finally {
      setTopUpLoading(false);
    }
  };

  if (!user) return <div className="dashboard-error">You are not logged in.</div>;

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">TE</div>
          <div>
            <p className="brand-name">Trading Engine</p>
            <p className="brand-tag">Command center</p>
          </div>
        </div>
        <nav>
          <p className="nav-label">Navigation</p>
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
            <li
              className={activeTab === "orders" ? "active" : ""}
              onClick={() => setActiveTab("orders")}
            >
              Orders
            </li>
          </ul>
        </nav>
        <div className="sidebar-footer">
          <p className="sidebar-label">Signed in as</p>
          <p className="sidebar-user">{displayName}</p>
        </div>
      </aside>

      <div className="main-content fade-in">
        <header className="topbar">
          <div className="topbar-title">
            <p className="eyebrow">Trading Engine</p>
            <h1>{tabTitle}</h1>
            <p className="muted">{tabSubtitle}</p>
          </div>
          <button className="btn btn-outline" onClick={handleLogout}>
            Logout
          </button>
        </header>

        {activeTab === "dashboard" && (
          <section className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Balance</div>
              <div className="stat-value">${balanceDisplay}</div>
              <p className="stat-caption">Available for new orders.</p>
              <div className="stat-inputs">
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={topUpAmount}
                  onChange={(e) => setTopUpAmount(e.target.value)}
                  placeholder="Amount"
                />
                <button
                  className="btn btn-ghost"
                  type="button"
                  onClick={handleTopUp}
                  disabled={topUpLoading}
                >
                  {topUpLoading ? "Processing..." : "Top Up"}
                </button>
              </div>
              {topUpError && <p className="form-error">{topUpError}</p>}
            </div>
            <div className="stat-card">
              <div className="stat-label">Account</div>
              <div className="stat-value">{displayName}</div>
              <div className="stat-row">
                <span>Email</span>
                <strong>{user?.email || "-"}</strong>
              </div>
              <div className="stat-row">
                <span>ID</span>
                <strong>{user?.id ?? "-"}</strong>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Access</div>
              <div className="stat-value">{user?.role || "-"}</div>
              <div className="stat-row">
                <span>Status</span>
                <strong>{user?.status || "-"}</strong>
              </div>
              <div className="stat-row">
                <span>Location</span>
                <strong>{user?.location || "-"}</strong>
              </div>
            </div>
          </section>
        )}

        {activeTab === "inventory" && <InventoryTab />}

        {activeTab === "entities" && <EntitiesTab user={user} />}

        {activeTab === "orders" && (
          <OrdersTab user={user} onUserUpdate={onUserUpdate} />
        )}
      </div>

    </div>
  );
}
