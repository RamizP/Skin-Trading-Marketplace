import { useEffect, useMemo, useState } from "react";
import { getMe } from "../api/auth";
import { getEntity } from "../api/entities";
import { getInventory } from "../api/inventory";
import {
  buyOrder,
  createOrder,
  deleteOrder,
  getMyBuyOrdersByEntity,
  getHighestBuyOrdersByEntity,
  getOrdersByEntity,
} from "../api/orders";
import type { Entity, InventoryItem, Order, User } from "../api/types";
import { formatCurrency, formatRarity, getErrorMessage } from "../utils/format";
import "../styles/ItemPage.css";

type ItemPageProps = {
  entityId: number;
  inventoryItemId?: number;
  user: User;
  onBack: () => void;
  onUserUpdate?: (user: User) => void;
};

type StatusMessage = {
  type: "success" | "error";
  text: string;
};

const rarityClass = (rarity?: string | null) =>
  `rarity-${(rarity || "common").replace(/_/g, "-")}`;

export default function ItemPage({
  entityId,
  inventoryItemId,
  user,
  onBack,
  onUserUpdate,
}: ItemPageProps) {
  const [entity, setEntity] = useState<Entity | null>(null);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [myBuyOrders, setMyBuyOrders] = useState<Order[]>([]);
  const [highestBuyOrder, setHighestBuyOrder] = useState<Order | null>(null);
  const [selectedInventoryId, setSelectedInventoryId] = useState<number | "">(
    inventoryItemId ?? "",
  );
  const [sellPrice, setSellPrice] = useState("");
  const [buyOrderPrice, setBuyOrderPrice] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [pendingOrderId, setPendingOrderId] = useState<number | null>(null);
  const [status, setStatus] = useState<StatusMessage | null>(null);

  const ownedCopies = useMemo(
    () => inventory.filter((item) => item.entity_id === entityId),
    [inventory, entityId],
  );

  const sellableCopies = useMemo(
    () => ownedCopies.filter((item) => !item.in_sale),
    [ownedCopies],
  );

  const selectedInventory = useMemo(
    () => sellableCopies.find((item) => item.id === Number(selectedInventoryId)),
    [sellableCopies, selectedInventoryId],
  );

  const lowestAsk = orders[0] ?? null;
  const ownListedCount = ownedCopies.filter((item) => item.in_sale).length;

  const loadPage = async () => {
    setLoading(true);
    setStatus(null);
    try {
      const [entityData, inventoryData, orderData, buyOrderData, highestOrderData] = await Promise.all([
        getEntity(entityId),
        getInventory().catch(() => []),
        getOrdersByEntity(entityId).catch((err) => {
          const message = getErrorMessage(err, "");
          if (message.toLowerCase().includes("no orders")) return [];
          throw err;
        }),
        getMyBuyOrdersByEntity(entityId).catch((err) => {
          const message = getErrorMessage(err, "");
          if (message.toLowerCase().includes("no orders")) return [];
          throw err;
        }),
        getHighestBuyOrdersByEntity(entityId).catch((err) => {
          const message = getErrorMessage(err, "");
          if (message.toLowerCase().includes("no orders")) return null;
          throw err;
        }),
      ]);
      setEntity(entityData);
      setInventory(inventoryData);
      setOrders(orderData);
      setMyBuyOrders(buyOrderData);
      setHighestBuyOrder(highestOrderData);
      const preferredCopy = inventoryData.find((item) => item.id === inventoryItemId);
      const firstSellable = inventoryData.find(
        (item) => item.entity_id === entityId && !item.in_sale,
      );
      setSelectedInventoryId(
        preferredCopy && !preferredCopy.in_sale
          ? preferredCopy.id
          : firstSellable?.id ?? "",
      );
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to load item") });
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async () => {
    if (!onUserUpdate) return;
    try {
      onUserUpdate(await getMe());
    } catch {
      // Keep the current balance if the action succeeded but the profile refresh failed.
    }
  };

  useEffect(() => {
    void loadPage();
  }, [entityId, inventoryItemId]);

  const handleSell = async () => {
    const price = Number(sellPrice);
    if (!selectedInventory || !Number.isFinite(price) || price <= 0) {
      setStatus({ type: "error", text: "Pick a sellable copy and enter a valid price." });
      return;
    }

    setActionLoading(true);
    setStatus(null);
    try {
      await createOrder({
        side: "sell",
        price,
        entity_id: selectedInventory.entity_id,
        entity_in_inventory_id: selectedInventory.id,
      });
      setSellPrice("");
      await loadPage();
      await refreshUser();
      setStatus({ type: "success", text: "Your copy is now listed for sale." });
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to list item") });
    } finally {
      setActionLoading(false);
    }
  };

  const handleBuyOrder = async () => {
    const price = Number(buyOrderPrice);
    if (!Number.isFinite(price) || price <= 0) {
      setStatus({ type: "error", text: "Enter a valid buy order price." });
      return;
    }

    setActionLoading(true);
    setStatus(null);
    try {
      await createOrder({ side: "buy", price, entity_id: entityId });
      setBuyOrderPrice("");
      await loadPage();
      await refreshUser();
      setStatus({ type: "success", text: "Buy order placed for this item." });
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to place buy order") });
    } finally {
      setActionLoading(false);
    }
  };

  const handleInstantBuy = async (orderId: number) => {
    setPendingOrderId(orderId);
    setStatus(null);
    try {
      await buyOrder(orderId);
      await loadPage();
      await refreshUser();
      setStatus({ type: "success", text: "Item bought and moved to your inventory." });
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to buy item") });
    } finally {
      setPendingOrderId(null);
    }
  };

  const handleCancelOrder = async (orderId: number) => {
    setPendingOrderId(orderId);
    setStatus(null);
    try {
      await deleteOrder(orderId);
      await loadPage();
      setStatus({ type: "success", text: "Order cancelled." });
    } catch (err) {
      setStatus({ type: "error", text: getErrorMessage(err, "Failed to cancel order") });
    } finally {
      setPendingOrderId(null);
    }
  };

  if (loading) {
    return <div className="item-loading">Loading item...</div>;
  }

  if (!entity) {
    return (
      <section className="item-empty">
        <button className="btn btn-outline" type="button" onClick={onBack}>
          Back
        </button>
        <p>{status?.text || "Item could not be loaded."}</p>
      </section>
    );
  }

  return (
    <section className="item-page fade-in">
      <button className="btn btn-outline item-back" type="button" onClick={onBack}>
        Back
      </button>

      <div className="item-hero">
        <div className={`item-art ${rarityClass(entity.entity_rarity)}`}>
          {entity.image_url ? (
            <img src={entity.image_url} alt={entity.name} />
          ) : (
            <span>{entity.symbol || "TE"}</span>
          )}
        </div>

        <div className="item-summary">
          <p className="eyebrow">Item Market</p>
          <h2>{entity.name}</h2>
          <div className="item-tags">
            <span>{formatRarity(entity.entity_rarity)}</span>
            <span>{entity.symbol || "No symbol"}</span>
            <span>{ownedCopies.length} owned</span>
          </div>
          <div className="item-stats">
            <div>
              <span>Lowest Ask</span>
              <strong>{lowestAsk ? formatCurrency(lowestAsk.price) : "No asks"}</strong>
            </div>
            <div>
              <span>Your Copies</span>
              <strong>{ownedCopies.length}</strong>
            </div>
            <div>
              <span>Listed By You</span>
              <strong>{ownListedCount}</strong>
            </div>
          </div>
        </div>
      </div>

      {status && <div className={`status ${status.type}`}>{status.text}</div>}

      <div className="item-actions">
        <div className="action-panel instant-buy">
          <div>
            <p className="eyebrow">Buy Now</p>
            <h3>{lowestAsk ? formatCurrency(lowestAsk.price) : "No active asks"}</h3>
            <p className="muted">
              {lowestAsk
                ? "Buy the cheapest current sell listing immediately."
                : "No seller has listed this item yet."}
            </p>
          </div>
          <button
            className="btn"
            type="button"
            disabled={!lowestAsk || lowestAsk.user_id === user.id || pendingOrderId === lowestAsk?.id}
            onClick={() => lowestAsk && handleInstantBuy(lowestAsk.id)}
          >
            {pendingOrderId === lowestAsk?.id ? "Buying" : "Buy Cheapest"}
          </button>
        </div>

        <div className="action-panel">
          <div>
            <p className="eyebrow">Sell</p>
            <h3>List Your Copy</h3>
          </div>
          <label>
            <span>Copy</span>
            <select
              value={selectedInventoryId}
              onChange={(event) => setSelectedInventoryId(Number(event.target.value))}
              disabled={!sellableCopies.length || actionLoading}
            >
              {sellableCopies.map((item) => (
                <option key={item.id} value={item.id}>
                  #{item.id} - Wear {item.entity_wear}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Ask Price</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={sellPrice}
              onChange={(event) => setSellPrice(event.target.value)}
              placeholder="0.00"
            />
          </label>
          <button
            className="btn"
            type="button"
            disabled={!sellableCopies.length || actionLoading}
            onClick={handleSell}
          >
            {actionLoading ? "Working" : "List For Sale"}
          </button>
          {!sellableCopies.length && <p className="helper">No unlisted copy available.</p>}
        </div>

        <div className="action-panel">
          <div>
            <p className="eyebrow">Buy Order</p>
            <h3>Set Your Bid</h3>
          </div>
          <label>
            <span>Bid Price</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={buyOrderPrice}
              onChange={(event) => setBuyOrderPrice(event.target.value)}
              placeholder="0.00"
            />
          </label>
          <button
            className="btn btn-ghost"
            type="button"
            disabled={actionLoading}
            onClick={handleBuyOrder}
          >
            {actionLoading ? "Working" : "Place Buy Order"}
          </button>
        </div>
      </div>

      <div className="asks-panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Sell Listings</p>
            <h2>Current Asks</h2>
            <p className="muted">Sorted from cheapest to most expensive.</p>
          </div>
          <div className="pill">{orders.length} asks</div>
        </div>

        <div className="asks-list">
          {orders.length === 0 && <p className="helper">No active sell listings.</p>}
          {orders.map((order) => (
            <div className="ask-row" key={order.id}>
              <div>
                <strong>{order.inventory?.entity_wear || "Unknown wear"}</strong>
                <small>Listing #{order.id}</small>
              </div>
              <div>
                <span>Seller</span>
                <strong>{order.user_id === user.id ? "You" : `User #${order.user_id}`}</strong>
              </div>
              <div>
                <span>Ask</span>
                <strong>{formatCurrency(order.price)}</strong>
              </div>
              {order.user_id === user.id ? (
                <button
                  className="btn btn-outline"
                  type="button"
                  disabled={pendingOrderId === order.id}
                  onClick={() => handleCancelOrder(order.id)}
                >
                  {pendingOrderId === order.id ? "Cancelling" : "Cancel"}
                </button>
              ) : (
                <button
                  className="btn"
                  type="button"
                  disabled={pendingOrderId === order.id}
                  onClick={() => handleInstantBuy(order.id)}
                >
                  {pendingOrderId === order.id ? "Buying" : "Buy"}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="buy-orders-panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Buy Orders</p>
            <h2>Open Bids</h2>
            <p className="muted">Cancel bids that have not matched a seller yet.</p>
          </div>
          <div className="pill">{myBuyOrders.length} bids</div>
        </div>
          Highest Bid
          {highestBuyOrder !== null &&
            <div className="ask-row buy-order-row" key={highestBuyOrder.id}>
              <div>
                <strong>{entity.name}</strong>
                <small>Buy order #{highestBuyOrder.id}</small>
              </div>
              <div>
                <span>Side</span>
                <strong>Buy</strong>
              </div>
              <div>
                <span>Bid</span>
                <strong>{formatCurrency(highestBuyOrder.price)}</strong>
              </div>
              <button
                className="btn btn-outline"
                type="button"
                disabled={pendingOrderId === highestBuyOrder.id}
                onClick={() => handleCancelOrder(highestBuyOrder.id)}
              >
                {pendingOrderId === highestBuyOrder.id ? "Cancelling" : "Cancel"}
              </button>
            </div>
          }

        Your Bid
        <div className="asks-list">
          {highestBuyOrder === null && <p className="helper">No open buy orders for this item.</p>}
          {myBuyOrders.map((order) => (
            <div className="ask-row buy-order-row" key={order.id}>
              <div>
                <strong>{entity.name}</strong>
                <small>Buy order #{order.id}</small>
              </div>
              <div>
                <span>Side</span>
                <strong>Buy</strong>
              </div>
              <div>
                <span>Bid</span>
                <strong>{formatCurrency(order.price)}</strong>
              </div>
              <button
                className="btn btn-outline"
                type="button"
                disabled={pendingOrderId === order.id}
                onClick={() => handleCancelOrder(order.id)}
              >
                {pendingOrderId === order.id ? "Cancelling" : "Cancel"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
