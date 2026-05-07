import { useState } from "react";
import { chargeBalance, logoutUser } from "../api/auth";
import type { User } from "../api/types";
import { formatCurrency, getErrorMessage } from "../utils/format";
import InventoryTab from "./Inventory";
import EntitiesTab from "./Entities";
import ItemPage from "./ItemPage";
import "../styles/Dashboard.css";

type DashboardProps = {
  user: User;
  onLogout?: () => void;
  onUserUpdate?: (user: User) => void;
};

type ActiveTab = "dashboard" | "inventory" | "entities" | "item";

type ItemSelection = {
  entityId: number;
  inventoryItemId?: number;
};

const navItems: Array<{ id: ActiveTab; label: string; meta: string }> = [
  { id: "dashboard", label: "Overview", meta: "Account" },
  { id: "entities", label: "Market", meta: "Listings" },
  { id: "inventory", label: "Inventory", meta: "Portfolio" },
];

const marketSignals = [
  { label: "Active Lanes", value: "24", tone: "cyan" },
  { label: "Avg. Spread", value: "4.8%", tone: "amber" },
  { label: "Fill Speed", value: "32 ms", tone: "green" },
];

export default function Dashboard({ user, onLogout, onUserUpdate }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<ActiveTab>("dashboard");
  const [selectedItem, setSelectedItem] = useState<ItemSelection | null>(null);
  const [topUpAmount, setTopUpAmount] = useState("");
  const [topUpError, setTopUpError] = useState("");
  const [topUpLoading, setTopUpLoading] = useState(false);

  const displayName = user.username || user.email || "Trader";
  const balance = Number(user.balance ?? 0);
  const balanceDisplay = formatCurrency(Number.isFinite(balance) ? balance : 0);

  const handleLogout = async () => {
    await logoutUser();
    onLogout?.();
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
      onUserUpdate?.(updated);
      setTopUpAmount("");
    } catch (err) {
      setTopUpError(getErrorMessage(err, "Failed to top up balance"));
    } finally {
      setTopUpLoading(false);
    }
  };

  const openItem = (selection: ItemSelection) => {
    setSelectedItem(selection);
    setActiveTab("item");
  };

  const showTab = (tab: ActiveTab) => {
    if (tab !== "item") {
      setSelectedItem(null);
    }
    setActiveTab(tab);
  };

  const tabTitle =
    activeTab === "dashboard"
      ? "Market Overview"
      : activeTab === "inventory"
        ? "Inventory"
        : activeTab === "item"
          ? "Item Details"
          : "Skin Market";

  const tabSubtitle =
    activeTab === "dashboard"
      ? "Wallet, profile, and live market pressure in one compact view."
      : activeTab === "inventory"
        ? "Click a skin to sell it or inspect its current market."
        : activeTab === "item"
          ? "Buy the cheapest ask, list your copy, or place a buy order from one screen."
          : "Click a skin to open its item page with asks, sell controls, and buy orders.";

  return (
    <div className="market-shell">
      <aside className="market-sidebar">
        <div className="market-brand">
          <div className="brand-mark">TE</div>
          <div>
            <p className="brand-name">Trading Engine</p>
            <p className="brand-tag">Skin exchange</p>
          </div>
        </div>

        <div className="wallet-block">
          <span>Wallet Balance</span>
          <strong>{balanceDisplay}</strong>
          <small>Ready for instant buys</small>
        </div>

        <nav className="market-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={activeTab === item.id ? "active" : ""}
              type="button"
              onClick={() => showTab(item.id)}
            >
              <span>{item.label}</span>
              <small>{item.meta}</small>
            </button>
          ))}
        </nav>

        <div className="sidebar-account">
          <span className="sidebar-label">Signed in</span>
          <strong>{displayName}</strong>
          <small>{user.role || "member"}</small>
          <button className="btn btn-outline" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      <main className="market-main fade-in">
        <header className="market-topbar">
          <div>
            <p className="eyebrow">CS Market Interface</p>
            <h1>{tabTitle}</h1>
            <p className="muted">{tabSubtitle}</p>
          </div>
          <div className="topbar-wallet">
            <span>Available</span>
            <strong>{balanceDisplay}</strong>
          </div>
        </header>

        {activeTab === "dashboard" && (
          <section className="overview-layout">
            <div className="overview-hero">
              <div>
                <p className="eyebrow">Trading Command</p>
                <h2>Price, list, and buy without leaving the desk.</h2>
                <p className="muted">
                  Built around the core market loop: scan listings, compare wear,
                  place orders, and keep balance visible at every step.
                </p>
              </div>
              <div className="weapon-showcase" aria-hidden="true">
                <div className="weapon-line top"></div>
                <div className="weapon-line barrel"></div>
                <div className="weapon-line body"></div>
                <div className="weapon-line grip"></div>
              </div>
            </div>

            <div className="overview-cards">
              <div className="market-card wallet-card">
                <span className="card-label">Wallet</span>
                <strong>{balanceDisplay}</strong>
                <div className="topup-row">
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={topUpAmount}
                    onChange={(event) => setTopUpAmount(event.target.value)}
                    placeholder="Top-up amount"
                    aria-label="Top-up amount"
                  />
                  <button
                    className="btn"
                    type="button"
                    onClick={handleTopUp}
                    disabled={topUpLoading}
                  >
                    {topUpLoading ? "Processing" : "Top Up"}
                  </button>
                </div>
                {topUpError && <p className="form-error">{topUpError}</p>}
              </div>

              <div className="market-card profile-card">
                <span className="card-label">Profile</span>
                <strong>{displayName}</strong>
                <dl>
                  <div>
                    <dt>Email</dt>
                    <dd>{user.email || "-"}</dd>
                  </div>
                  <div>
                    <dt>User ID</dt>
                    <dd>{user.id}</dd>
                  </div>
                  <div>
                    <dt>Status</dt>
                    <dd>{user.status || "active"}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <div className="signal-strip">
              {marketSignals.map((signal) => (
                <div className={`signal-tile ${signal.tone}`} key={signal.label}>
                  <span>{signal.label}</span>
                  <strong>{signal.value}</strong>
                </div>
              ))}
            </div>
          </section>
        )}

        {activeTab === "inventory" && <InventoryTab onOpenItem={openItem} />}
        {activeTab === "entities" && <EntitiesTab user={user} onOpenItem={openItem} />}
        {activeTab === "item" && selectedItem && (
          <ItemPage
            entityId={selectedItem.entityId}
            inventoryItemId={selectedItem.inventoryItemId}
            user={user}
            onBack={() => showTab(selectedItem.inventoryItemId ? "inventory" : "entities")}
            onUserUpdate={onUserUpdate}
          />
        )}
      </main>
    </div>
  );
}
