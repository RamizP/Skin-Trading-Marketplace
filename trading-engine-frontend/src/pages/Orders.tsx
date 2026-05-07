import { useEffect, useMemo, useState } from "react";
import { getAllEntities } from "../api/entities";
import { getInventory } from "../api/inventory";
import { buyOrder, createOrder, deleteOrder, getOrdersByEntity } from "../api/orders";
import { getMe } from "../api/auth";
import type { Entity, InventoryItem, Order, User } from "../api/types";
import { formatCurrency, formatRarity, getErrorMessage } from "../utils/format";
import "../styles/Orders.css";

type OrdersProps = {
  user: User;
  onUserUpdate?: (user: User) => void;
};

type StatusMessage = {
  type: "success" | "error";
  text: string;
};

export default function OrdersTab({ user, onUserUpdate }: OrdersProps) {
  const [mode, setMode] = useState<"buy" | "sell">("sell");
  const [entities, setEntities] = useState<Entity[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [marketEntityId, setMarketEntityId] = useState<number | "">("");
  const [selectedEntityId, setSelectedEntityId] = useState<number | "">("");
  const [selectedInventoryId, setSelectedInventoryId] = useState<number | "">("");
  const [price, setPrice] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [trackedBuyOrders, setTrackedBuyOrders] = useState<Order[]>([]);
  const [loadingMarket, setLoadingMarket] = useState(false);
  const [loadingInventory, setLoadingInventory] = useState(false);
  const [creating, setCreating] = useState(false);
  const [pendingOrderId, setPendingOrderId] = useState<number | null>(null);
  const [marketError, setMarketError] = useState("");
  const [status, setStatus] = useState<StatusMessage | null>(null);

  const sellableInventory = useMemo(
    () => inventory.filter((item) => !item.in_sale),
    [inventory],
  );

  const selectedInventory = useMemo(
    () => sellableInventory.find((item) => item.id === Number(selectedInventoryId)),
    [sellableInventory, selectedInventoryId],
  );

  const selectedEntity = useMemo(
    () => entities.find((item) => item.id === Number(selectedEntityId)),
    [entities, selectedEntityId],
  );

  const marketEntity = useMemo(
    () => entities.find((item) => item.id === Number(marketEntityId)),
    [entities, marketEntityId],
  );

  const getEntityById = (entityId: number) =>
    entities.find((entity) => entity.id === entityId);

  const lowestAsk = useMemo(() => {
    const prices = orders
      .map((order) => Number(order.price))
      .filter((value) => Number.isFinite(value));
    if (!prices.length) return null;
    return Math.min(...prices);
  }, [orders]);

  const loadEntities = async () => {
    try {
      const data = await getAllEntities(0, 100);
      setEntities(data);
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to load entities") });
    }
  };

  const loadInventory = async () => {
    setLoadingInventory(true);
    try {
      const data = await getInventory();
      setInventory(data);
    } catch {
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
      const message = getErrorMessage(err, "Failed to fetch orders");
      setOrders([]);
      setMarketError(message.toLowerCase().includes("no orders") ? "" : message);
    } finally {
      setLoadingMarket(false);
    }
  };

  const refreshUser = async () => {
    if (!onUserUpdate) return;
    try {
      const updated = await getMe();
      onUserUpdate(updated);
    } catch {
      // The order action already completed; keep the existing user if refresh fails.
    }
  };

  useEffect(() => {
    void loadEntities();
    void loadInventory();
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
      void loadOrders(Number(marketEntityId));
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
          ? { price: priceValue, side: "buy" as const, entity_id: Number(selectedEntityId) }
          : {
              price: priceValue,
              side: "sell" as const,
              entity_in_inventory_id: Number(selectedInventoryId),
            };
      const createdOrder = await createOrder(payload);
      setPrice("");
      if (createdOrder.side === "buy") {
        setTrackedBuyOrders((current) => [
          createdOrder,
          ...current.filter((order) => order.id !== createdOrder.id),
        ]);
      }
      await loadInventory();
      if (marketEntityId) {
        await loadOrders(Number(marketEntityId));
      }
      setStatus({ type: "success", text: "Order created successfully." });
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to create order") });
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
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to buy order") });
    } finally {
      setPendingOrderId(null);
    }
  };

  const handleCancelOrder = async (orderId: number) => {
    setPendingOrderId(orderId);
    setStatus(null);
    try {
      await deleteOrder(orderId);
      setTrackedBuyOrders((current) =>
        current.filter((order) => order.id !== orderId),
      );
      await loadOrders(Number(marketEntityId));
      await loadInventory();
      setStatus({ type: "success", text: "Order cancelled." });
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to cancel order") });
    } finally {
      setPendingOrderId(null);
    }
  };

  return (
    <section className="orders-shell fade-in">
      <div className="order-ticket">
        <div className="section-header">
          <div>
            <p className="eyebrow">Trading</p>
            <h2>Create Order</h2>
            <p className="muted">Pick the item, set price, and publish to the book.</p>
          </div>
          <div className={`pill side-${mode}`}>{mode === "sell" ? "Sell" : "Buy"}</div>
        </div>

        <div className="order-toggle" role="group" aria-label="Order side">
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

        <div className="ticket-preview">
          <div className="ticket-art">
            {mode === "sell" && selectedInventory?.entity.image_url ? (
              <img src={selectedInventory.entity.image_url} alt={selectedInventory.entity.name} />
            ) : mode === "buy" && selectedEntity?.image_url ? (
              <img src={selectedEntity.image_url} alt={selectedEntity.name} />
            ) : (
              <span>{mode === "sell" ? selectedInventory?.entity.symbol || "TE" : selectedEntity?.symbol || "TE"}</span>
            )}
          </div>
          <div>
            <span>{mode === "sell" ? "Listing" : "Bid target"}</span>
            <strong>
              {mode === "sell"
                ? selectedInventory?.entity.name || "Select inventory"
                : selectedEntity?.name || "Select entity"}
            </strong>
            <small>
              {mode === "sell"
                ? selectedInventory?.entity.entity_rarity
                  ? formatRarity(selectedInventory.entity.entity_rarity)
                  : "No rarity"
                : selectedEntity?.entity_rarity
                  ? formatRarity(selectedEntity.entity_rarity)
                  : "No rarity"}
            </small>
          </div>
        </div>

        <div className="order-form">
          {mode === "sell" ? (
            <label>
              <span>Inventory Item</span>
              <select
                value={selectedInventoryId}
                onChange={(event) => setSelectedInventoryId(Number(event.target.value))}
                disabled={loadingInventory || !sellableInventory.length}
              >
                {sellableInventory.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.entity.name} ({item.entity.symbol}) - Wear {item.entity_wear}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <label>
              <span>Entity</span>
              <select
                value={selectedEntityId}
                onChange={(event) => setSelectedEntityId(Number(event.target.value))}
                disabled={!entities.length}
              >
                {entities.map((entity) => (
                  <option key={entity.id} value={entity.id}>
                    {entity.name} ({entity.symbol})
                  </option>
                ))}
              </select>
            </label>
          )}

          <label>
            <span>Limit Price</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={price}
              onChange={(event) => setPrice(event.target.value)}
              placeholder="0.00"
            />
          </label>

          <button className="btn" type="button" onClick={handleCreateOrder} disabled={creating}>
            {creating ? "Submitting" : mode === "sell" ? "List For Sale" : "Place Buy Order"}
          </button>
        </div>

        {loadingInventory && <p className="helper">Loading inventory...</p>}
        {!loadingInventory && mode === "sell" && !sellableInventory.length && (
          <p className="helper">No available inventory to sell.</p>
        )}

        {status && <div className={`status ${status.type}`}>{status.text}</div>}

        {trackedBuyOrders.length > 0 && (
          <div className="my-buy-orders">
            <div>
              <p className="eyebrow">Your Buy Orders</p>
              <h3>Open bids</h3>
            </div>
            {trackedBuyOrders.map((order) => {
              const entity = getEntityById(order.entity_id);
              return (
                <div className="my-buy-row" key={order.id}>
                  <div>
                    <strong>{entity?.name || `Entity #${order.entity_id}`}</strong>
                    <small>{formatRarity(entity?.entity_rarity)}</small>
                  </div>
                  <div>
                    <span>Bid</span>
                    <strong>{formatCurrency(order.price)}</strong>
                  </div>
                  <button
                    className="btn btn-outline"
                    type="button"
                    onClick={() => handleCancelOrder(order.id)}
                    disabled={pendingOrderId === order.id}
                  >
                    {pendingOrderId === order.id ? "Cancelling" : "Cancel"}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="book-panel">
        <div className="book-header">
          <div>
            <p className="eyebrow">Market</p>
            <h2>Order Book</h2>
            <p className="muted">Live asks for the selected skin.</p>
          </div>
          <div className="book-price">
            <span>Lowest Ask</span>
            <strong>{lowestAsk ? formatCurrency(lowestAsk) : "-"}</strong>
          </div>
        </div>

        <div className="market-controls">
          <label>
            <span>Entity</span>
            <select
              value={marketEntityId}
              onChange={(event) => setMarketEntityId(Number(event.target.value))}
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

        <div className="book-feature">
          <div className="book-feature-art">
            {marketEntity?.image_url ? (
              <img src={marketEntity.image_url} alt={marketEntity.name} />
            ) : (
              <span>{marketEntity?.symbol || "TE"}</span>
            )}
          </div>
          <div>
            <span>Selected Market</span>
            <strong>{marketEntity?.name || "Select entity"}</strong>
            <small>{marketEntity?.entity_rarity ? formatRarity(marketEntity.entity_rarity) : "No rarity"}</small>
          </div>
        </div>

        {loadingMarket && <p className="helper">Loading orders...</p>}
        {!loadingMarket && marketError && <p className="helper error">{marketError}</p>}

        {!loadingMarket && !marketError && (
          <div className="order-book-list">
            {orders.length === 0 && <p className="helper">No active sell orders.</p>}
            {orders.map((order) => (
              <div key={order.id} className="book-row">
                <div className="book-item">
                  <strong>{order.inventory?.entity?.name || marketEntity?.name || "Entity"}</strong>
                  <small>
                    {order.inventory?.entity?.entity_rarity
                      ? formatRarity(order.inventory.entity.entity_rarity)
                      : formatRarity(marketEntity?.entity_rarity)}
                  </small>
                </div>
                <div>
                  <span>Wear</span>
                  <strong>{order.inventory?.entity_wear ?? "-"}</strong>
                </div>
                <div>
                  <span>Ask</span>
                  <strong>{formatCurrency(order.price)}</strong>
                </div>
                {order.user_id === user.id ? (
                  <button
                    className="btn btn-outline"
                    type="button"
                    onClick={() => handleCancelOrder(order.id)}
                    disabled={pendingOrderId === order.id}
                  >
                    {pendingOrderId === order.id ? "Cancelling" : "Cancel"}
                  </button>
                ) : (
                  <button
                    className="btn"
                    type="button"
                    onClick={() => handleBuyOrder(order.id)}
                    disabled={pendingOrderId === order.id}
                  >
                    {pendingOrderId === order.id ? "Buying" : "Buy"}
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
