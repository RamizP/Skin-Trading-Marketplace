import { useEffect, useMemo, useState } from "react";
import { getAllEntities } from "../api/entities";
import { getInventory } from "../api/inventory";
import { buyOrder, createOrder, deleteOrder, getOrdersByEntity } from "../api/orders";
import { getMe } from "../api/auth";
import "../styles/Orders.css";

type OrdersProps = {
  user: any;
  onUserUpdate?: (user: any) => void;
};

type StatusMessage = {
  type: "success" | "error";
  text: string;
};

export default function OrdersTab({ user, onUserUpdate }: OrdersProps) {
  const [mode, setMode] = useState<"buy" | "sell">("sell");
  const [entities, setEntities] = useState<any[]>([]);
  const [inventory, setInventory] = useState<any[]>([]);
  const [marketEntityId, setMarketEntityId] = useState<number | "">("");
  const [selectedEntityId, setSelectedEntityId] = useState<number | "">("");
  const [selectedInventoryId, setSelectedInventoryId] = useState<number | "">("");
  const [price, setPrice] = useState("");
  const [orders, setOrders] = useState<any[]>([]);
  const [loadingMarket, setLoadingMarket] = useState(false);
  const [loadingInventory, setLoadingInventory] = useState(false);
  const [creating, setCreating] = useState(false);
  const [pendingOrderId, setPendingOrderId] = useState<number | null>(null);
  const [marketError, setMarketError] = useState("");
  const [status, setStatus] = useState<StatusMessage | null>(null);

  const sellableInventory = useMemo(
    () => inventory.filter((item) => !item.in_sale),
    [inventory]
  );

  const selectedInventory = useMemo(
    () => sellableInventory.find((item) => item.id === Number(selectedInventoryId)),
    [sellableInventory, selectedInventoryId]
  );

  const selectedEntity = useMemo(
    () => entities.find((item) => item.id === Number(selectedEntityId)),
    [entities, selectedEntityId]
  );

  const marketEntity = useMemo(
    () => entities.find((item) => item.id === Number(marketEntityId)),
    [entities, marketEntityId]
  );

  const formatPrice = (value: number) =>
    Number.isFinite(value)
      ? value.toLocaleString("en-US", { minimumFractionDigits: 2 })
      : "0.00";

  const loadEntities = async () => {
    try {
      const data = await getAllEntities(0, 100);
      setEntities(data);
    } catch (err) {
      setStatus({ type: "error", text: err.message });
    }
  };

  const loadInventory = async () => {
    setLoadingInventory(true);
    try {
      const data = await getInventory();
      setInventory(data);
    } catch (err) {
      setInventory([]);
    } finally {
      setLoadingInventory(false);
    }
  };

  const loadOrders = async (entityId: number) => {
    setLoadingMarket(true);
    setMarketError("");
    try {
      const data = await getOrdersByEntity(entityId);
      setOrders(data);
    } catch (err) {
      const message = err.message || "Failed to fetch orders";
      setOrders([]);
      if (message.toLowerCase().includes("no orders")) {
        setMarketError("");
      } else {
        setMarketError(message);
      }
    } finally {
      setLoadingMarket(false);
    }
  };

  const refreshUser = async () => {
    if (!onUserUpdate) return;
    try {
      const updated = await getMe();
      onUserUpdate(updated);
    } catch (err) {
      // ignore refresh errors
    }
  };

  useEffect(() => {
    loadEntities();
    loadInventory();
  }, []);

  useEffect(() => {
    if (entities.length && !selectedEntityId) {
      setSelectedEntityId(entities[0].id);
    }
    if (entities.length && !marketEntityId) {
      setMarketEntityId(entities[0].id);
    }
  }, [entities, selectedEntityId, marketEntityId]);

  useEffect(() => {
    if (sellableInventory.length && !selectedInventoryId) {
      setSelectedInventoryId(sellableInventory[0].id);
    }
  }, [sellableInventory, selectedInventoryId]);

  useEffect(() => {
    if (mode === "buy" && selectedEntityId) {
      setMarketEntityId(Number(selectedEntityId));
    }
  }, [mode, selectedEntityId]);

  useEffect(() => {
    if (mode === "sell" && selectedInventory) {
      setMarketEntityId(Number(selectedInventory.entity_id));
    }
  }, [mode, selectedInventory]);

  useEffect(() => {
    if (marketEntityId) {
      loadOrders(Number(marketEntityId));
    }
  }, [marketEntityId]);

  const handleCreateOrder = async () => {
    const priceValue = Number(price);
    if (!Number.isFinite(priceValue) || priceValue <= 0) {
      setStatus({ type: "error", text: "Enter a valid price." });
      return;
    }

    if (mode === "buy" && !selectedEntityId) {
      setStatus({ type: "error", text: "Select an entity to buy." });
      return;
    }

    if (mode === "sell" && !selectedInventoryId) {
      setStatus({ type: "error", text: "Select inventory to sell." });
      return;
    }

    setCreating(true);
    setStatus(null);
    try {
      const payload =
        mode === "buy"
          ? { price: priceValue, side: "buy", entity_id: Number(selectedEntityId) }
          : {
              price: priceValue,
              side: "sell",
              entity_in_inventory_id: Number(selectedInventoryId),
            };
      await createOrder(payload);
      setPrice("");
      await loadInventory();
      if (marketEntityId) {
        await loadOrders(Number(marketEntityId));
      }
      setStatus({ type: "success", text: "Order created successfully." });
    } catch (err) {
      setStatus({ type: "error", text: err.message });
    } finally {
      setCreating(false);
    }
  };

  const handleBuyOrder = async (orderId: number) => {
    setPendingOrderId(orderId);
    setStatus(null);
    try {
      await buyOrder(orderId);
      await loadOrders(Number(marketEntityId));
      await loadInventory();
      await refreshUser();
      setStatus({ type: "success", text: "Order purchased successfully." });
    } catch (err) {
      setStatus({ type: "error", text: err.message });
    } finally {
      setPendingOrderId(null);
    }
  };

  const handleCancelOrder = async (orderId: number) => {
    setPendingOrderId(orderId);
    setStatus(null);
    try {
      await deleteOrder(orderId);
      await loadOrders(Number(marketEntityId));
      await loadInventory();
      setStatus({ type: "success", text: "Order cancelled." });
    } catch (err) {
      setStatus({ type: "error", text: err.message });
    } finally {
      setPendingOrderId(null);
    }
  };

  return (
    <section className="orders-shell fade-in">
      <div className="orders-panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Trading</p>
            <h2>Create Order</h2>
            <p className="muted">Place buy or sell orders instantly.</p>
          </div>
          <div className="pill">{mode === "sell" ? "Sell" : "Buy"}</div>
        </div>

        <div className="order-toggle">
          <button
            className={mode === "sell" ? "active" : ""}
            type="button"
            onClick={() => setMode("sell")}
          >
            Sell
          </button>
          <button
            className={mode === "buy" ? "active" : ""}
            type="button"
            onClick={() => setMode("buy")}
          >
            Buy
          </button>
        </div>

        {mode === "sell" ? (
          <div className="order-form">
            <label>
              Inventory Item
              <select
                value={selectedInventoryId}
                onChange={(e) => setSelectedInventoryId(Number(e.target.value))}
                disabled={loadingInventory || !sellableInventory.length}
              >
                {sellableInventory.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.entity?.name} ({item.entity?.symbol}) · Wear {item.entity_wear}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Price
              <input
                type="number"
                min="0"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="0.00"
              />
            </label>
            <div className="order-actions">
              <button className="btn" onClick={handleCreateOrder} disabled={creating}>
                {creating ? "Listing..." : "List For Sale"}
              </button>
              {selectedInventory && (
                <div className="order-preview">
                  <span>{selectedInventory.entity?.name}</span>
                  <strong>{selectedInventory.entity?.entity_rarity}</strong>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="order-form">
            <label>
              Entity
              <select
                value={selectedEntityId}
                onChange={(e) => setSelectedEntityId(Number(e.target.value))}
                disabled={!entities.length}
              >
                {entities.map((entity) => (
                  <option key={entity.id} value={entity.id}>
                    {entity.name} ({entity.symbol})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Price
              <input
                type="number"
                min="0"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="0.00"
              />
            </label>
            <div className="order-actions">
              <button className="btn" onClick={handleCreateOrder} disabled={creating}>
                {creating ? "Submitting..." : "Place Buy Order"}
              </button>
              {selectedEntity && (
                <div className="order-preview">
                  <span>{selectedEntity.name}</span>
                  <strong>{selectedEntity.entity_rarity}</strong>
                </div>
              )}
            </div>
          </div>
        )}

        {loadingInventory && <p className="helper">Loading inventory...</p>}
        {!loadingInventory && mode === "sell" && !sellableInventory.length && (
          <p className="helper">No available inventory to sell.</p>
        )}

        {status && (
          <div className={`status ${status.type}`}>{status.text}</div>
        )}
      </div>

      <div className="orders-panel market-panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Market</p>
            <h2>Order Book</h2>
            <p className="muted">Live sell listings for the selected entity.</p>
          </div>
          <div className="pill">
            {marketEntity ? marketEntity.name : "Select entity"}
          </div>
        </div>

        <div className="market-controls">
          <label>
            Entity
            <select
              value={marketEntityId}
              onChange={(e) => setMarketEntityId(Number(e.target.value))}
              disabled={!entities.length}
            >
              {entities.map((entity) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name} ({entity.symbol})
                </option>
              ))}
            </select>
          </label>
        </div>

        {loadingMarket && <p className="helper">Loading orders...</p>}
        {!loadingMarket && marketError && (
          <p className="helper error">{marketError}</p>
        )}

        {!loadingMarket && !marketError && (
          <div className="order-list">
            {orders.length === 0 && (
              <p className="helper">No active sell orders.</p>
            )}
            {orders.map((order) => (
              <div key={order.id} className="order-row">
                <div className="order-info">
                  <div className="order-entity">
                    <span>{order.inventory?.entity?.name || "Entity"}</span>
                    <strong>{order.inventory?.entity?.entity_rarity || "-"}</strong>
                  </div>
                  <div className="order-meta">
                    <span>Price</span>
                    <strong>${formatPrice(order.price)}</strong>
                  </div>
                  <div className="order-meta">
                    <span>Wear</span>
                    <strong>{order.inventory?.entity_wear ?? "-"}</strong>
                  </div>
                </div>
                <div className="order-actions">
                  {order.user_id === user?.id ? (
                    <button
                      className="btn btn-outline"
                      onClick={() => handleCancelOrder(order.id)}
                      disabled={pendingOrderId === order.id}
                    >
                      {pendingOrderId === order.id ? "Cancelling..." : "Cancel"}
                    </button>
                  ) : (
                    <button
                      className="btn"
                      onClick={() => handleBuyOrder(order.id)}
                      disabled={pendingOrderId === order.id}
                    >
                      {pendingOrderId === order.id ? "Buying..." : "Buy"}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
