import { useCallback, useEffect, useState } from "react";
import { getAllEntities, getCategories, getEntities } from "../api/entities";
import { getInventory } from "../api/inventory";
import type { Entity, User, View } from "../api/types";
import { ErrorNotice } from "../components/Feedback";
import FreeCaseClaim from "../components/FreeCaseClaim";
import Icon from "../components/Icon";
import type { IconName } from "../components/Icon";
import UtilityDialog from "../components/UtilityDialog";
import useQuery from "../hooks/useQuery";
import { formatCurrency } from "../utils/format";
import Entities from "./Entities";
import Inventory from "./Inventory";
import ItemPage from "./ItemPage";
import Orders from "./Orders";

const navigation: { id: View; label: string; icon: IconName }[] = [
  { id: "market", label: "Marketplace", icon: "market" },
  { id: "inventory", label: "My inventory", icon: "inventory" },
  { id: "orders", label: "My orders", icon: "orders" },
  { id: "cases", label: "Cases", icon: "case" },
];
function initialView(): View {
  const hash = window.location.hash.slice(1);
  return navigation.some((item) => item.id === hash)
    ? (hash as View)
    : "market";
}
const loadCatalog = async () => {
  const [catalog, market, categories] = await Promise.all([
    getAllEntities(),
    getEntities(),
    getCategories(),
  ]);
  return { catalog, market, categories };
};

export default function Dashboard({
  user,
  restoring,
  onAuth,
  onLogout,
  onRefreshUser,
  sessionMessage,
  onDismissMessage,
}: {
  user: User | null;
  restoring: boolean;
  onAuth: (mode?: "login" | "register") => void;
  onLogout: () => Promise<void>;
  onRefreshUser: () => Promise<void>;
  sessionMessage: string;
  onDismissMessage: () => void;
}) {
  const [view, setView] = useState<View>(initialView);
  const [selected, setSelected] = useState<{
    entity: Entity;
    inventoryId?: number;
  } | null>(null);
  const [utility, setUtility] = useState<
    "funds" | "inventory" | "catalog" | null
  >(null);
  const [toast, setToast] = useState("");
  const [logoutBusy, setLogoutBusy] = useState(false);
  const exchange = useQuery(loadCatalog, {
    catalog: [],
    market: [],
    categories: [],
  });
  const inventoryFetcher = useCallback(
    () => (user ? getInventory() : Promise.resolve([])),
    [user],
  );
  const inventory = useQuery(inventoryFetcher, []);
  const { catalog, market, categories } = exchange.data;
  useEffect(() => {
    const changed = () => {
      const hash = window.location.hash.slice(1);
      if (navigation.some((item) => item.id === hash)) setView(hash as View);
    };
    window.addEventListener("hashchange", changed);
    return () => window.removeEventListener("hashchange", changed);
  }, []);
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view]);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 5000);
    return () => window.clearTimeout(timer);
  }, [toast]);
  function navigate(next: View) {
    window.location.hash = next;
    setView(next);
  }
  function selectItem(entity: Entity, inventoryId?: number) {
    setSelected({ entity, inventoryId });
  }
  async function changed(message?: string) {
    exchange.reload();
    inventory.reload();
    if (user) await onRefreshUser();
    if (message) setToast(message);
  }
  const inventoryItems = user ? inventory.data : [];
  const title =
    navigation.find((item) => item.id === view)?.label || "Marketplace";

  return (
    <div className="app-shell">
      <a className="skip-link" href="#content">
        Skip to content
      </a>
      <aside className="app-sidebar">
        <a className="brand" href="#market" aria-label="Trading Engine home">
          <span className="brand-symbol">
            <Icon name="bolt" size={25} />
          </span>
          <span>
            TRADING
            <span className="brand-second">
              ENGINE<span className="brand-dot">.</span>
            </span>
          </span>
        </a>
        <div className="sidebar-section-label">YOUR EXCHANGE</div>
        <nav aria-label="Main navigation">
          {navigation.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`nav-item ${view === item.id ? "active" : ""}`}
              aria-current={view === item.id ? "page" : undefined}
            >
              <Icon name={item.icon} />
              <span>{item.label}</span>
              {item.id === "inventory" && user && (
                <small>{inventoryItems.length}</small>
              )}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="label-icon">
              <Icon name="shield" size={17} /> BUILT TO TRADE
            </span>
            <p>
              Your items. Your price.
              <br />
              Your next move.
            </p>
            <span className="small-muted">
              A trading sandbox. No real money.
            </span>
          </div>
          {user ? (
            <div className="sidebar-profile">
              <span className="avatar">
                {user.username.slice(0, 2).toUpperCase()}
              </span>
              <div>
                <strong>{user.username}</strong>
                <small>
                  {user.role === "admin" ? "Administrator" : "Collector"}
                </small>
              </div>
              <button
                className="icon-button"
                aria-label="Sign out"
                disabled={logoutBusy}
                onClick={async () => {
                  setLogoutBusy(true);
                  setSelected(null);
                  try {
                    await onLogout();
                  } finally {
                    setLogoutBusy(false);
                  }
                }}
              >
                <Icon name="logout" size={18} />
              </button>
            </div>
          ) : (
            <button className="sidebar-sign-in" onClick={() => onAuth()}>
              <Icon name="lock" size={18} />
              <span>Your collection awaits</span>
              <Icon name="arrow" size={16} />
            </button>
          )}
        </div>
      </aside>
      <div className="app-workspace">
        <header className="topbar">
          <div className="breadcrumb">
            <span>EXCHANGE</span>
            <Icon name="chevron" size={12} />
            <strong>{title}</strong>
          </div>
          <div className="topbar-actions">
            <span
              className={`connection-status ${exchange.error ? "offline" : ""}`}
            >
              <span />
              {exchange.error
                ? "API unavailable"
                : exchange.loading
                  ? "Connecting"
                  : "API connected"}
            </span>
            {user ? (
              <>
                <button
                  className="wallet-button"
                  onClick={() => setUtility("funds")}
                  aria-label="Add test funds"
                >
                  <Icon name="wallet" size={17} />
                  <strong>{formatCurrency(user.balance)}</strong>
                  <span>
                    <Icon name="plus" size={14} />
                  </span>
                </button>
                <span className="avatar topbar-avatar">
                  {user.username.slice(0, 2).toUpperCase()}
                </span>
                <button
                  className="icon-button mobile-signout"
                  aria-label="Sign out"
                  disabled={logoutBusy}
                  onClick={async () => {
                    setLogoutBusy(true);
                    setSelected(null);
                    try {
                      await onLogout();
                    } finally {
                      setLogoutBusy(false);
                    }
                  }}
                >
                  <Icon name="logout" size={18} />
                </button>
              </>
            ) : (
              <>
                <button
                  className="button button-quiet"
                  disabled={restoring}
                  onClick={() => onAuth()}
                >
                  Sign in
                </button>
                <button
                  className="button button-primary"
                  disabled={restoring}
                  onClick={() => onAuth("register")}
                >
                  Get started
                  <Icon name="arrow" size={15} />
                </button>
              </>
            )}
          </div>
        </header>
        <main id="content" className="main-content">
          {sessionMessage && (
            <div className="session-notice" role="status">
              <Icon name="info" size={17} />
              <span>{sessionMessage}</span>
              <button
                className="icon-button"
                aria-label="Dismiss notification"
                onClick={onDismissMessage}
              >
                <Icon name="close" size={16} />
              </button>
            </div>
          )}
          {exchange.error && (
            <ErrorNotice message={exchange.error} onRetry={exchange.reload} />
          )}
          {(view === "market" || view === "cases") && (
            <Entities
              key={view}
              catalog={catalog}
              market={market}
              categories={categories}
              casesOnly={view === "cases"}
              loading={exchange.loading}
              user={user}
              onOpen={selectItem}
              onNavigate={navigate}
              onCreate={() => setUtility("catalog")}
              caseOffer={
                view === "cases" ? (
                  <FreeCaseClaim
                    key={user?.id ?? "guest"}
                    user={user}
                    catalog={catalog}
                    onAuth={() => onAuth()}
                    onChanged={changed}
                    onInventory={() => navigate("inventory")}
                  />
                ) : undefined
              }
            />
          )}
          {view === "inventory" && (
            <Inventory
              user={user}
              items={inventoryItems}
              categories={categories}
              loading={inventory.loading}
              error={inventory.error}
              onRetry={inventory.reload}
              onAuth={() => onAuth()}
              onOpen={selectItem}
              onAdd={() => setUtility("inventory")}
              onMarket={() => navigate("market")}
            />
          )}
          {view === "orders" && (
            <Orders
              user={user}
              catalog={catalog}
              inventory={inventoryItems}
              categories={categories}
              onAuth={() => onAuth()}
              onOpen={selectItem}
              onChanged={changed}
              onMarket={() => navigate("market")}
            />
          )}
          <footer className="page-footer">
            <span>
              <span className="footer-mark">↗</span> Trading Engine{" "}
              <span className="footer-divider">/</span> Built for the next
              trade.
            </span>
            <span>Independent project · Test funds only</span>
          </footer>
        </main>
      </div>
      {selected && (
        <ItemPage
          key={`${selected.entity.id}-${selected.inventoryId || "market"}`}
          entity={selected.entity}
          inventoryItemId={selected.inventoryId}
          catalog={catalog}
          categories={categories}
          inventory={inventoryItems}
          user={user}
          onClose={() => setSelected(null)}
          onAuth={() => {
            setSelected(null);
            onAuth();
          }}
          onChanged={changed}
        />
      )}
      {utility && user && (
        <UtilityDialog
          kind={utility}
          catalog={catalog}
          categories={categories}
          onClose={() => setUtility(null)}
          onChanged={changed}
        />
      )}
      {toast && (
        <div className="toast" role="status">
          <span className="toast-check">
            <Icon name="check" size={17} />
          </span>
          <span>{toast}</span>
          <button
            className="icon-button"
            aria-label="Dismiss success message"
            onClick={() => setToast("")}
          >
            <Icon name="close" size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
