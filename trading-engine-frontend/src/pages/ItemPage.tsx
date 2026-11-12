import { useCallback, useRef, useState } from "react";
import type { FormEvent } from "react";
import { getCaseDrops, openCase } from "../api/cases";
import {
  buyOrder,
  createOrder,
  deleteOrder,
  getHighestBuyOrdersByEntity,
  getMyBuyOrdersByEntity,
  getOrdersByEntity,
} from "../api/orders";
import type {
  CaseDrop,
  CaseReward,
  Category,
  Entity,
  InventoryItem,
  Order,
  User,
} from "../api/types";
import { EmptyState, ErrorNotice } from "../components/Feedback";
import CaseOpening from "../components/CaseOpening";
import Icon from "../components/Icon";
import ItemArt from "../components/ItemArt";
import Modal from "../components/Modal";
import useQuery from "../hooks/useQuery";
import {
  categoryName,
  formatCurrency,
  formatRarity,
  getErrorMessage,
  isCase,
  moneyInput,
  rarityClass,
} from "../utils/format";

export default function ItemPage({
  entity,
  inventoryItemId,
  catalog,
  categories,
  inventory,
  user,
  onClose,
  onAuth,
  onChanged,
}: {
  entity: Entity;
  inventoryItemId?: number;
  catalog: Entity[];
  categories: Category[];
  inventory: InventoryItem[];
  user: User | null;
  onClose: () => void;
  onAuth: () => void;
  onChanged: (message?: string) => Promise<void>;
}) {
  const caseItem = isCase(entity, categories);
  const userId = user?.id;
  const fetcher = useCallback(async () => {
    const [orders, highestBid, drops, myBuyOrders] = await Promise.all([
      getOrdersByEntity(entity.id),
      getHighestBuyOrdersByEntity(entity.id),
      caseItem ? getCaseDrops(entity.id) : Promise.resolve([] as CaseDrop[]),
      userId
        ? getMyBuyOrdersByEntity(entity.id)
        : Promise.resolve([] as Order[]),
    ]);
    return { orders, highestBid, drops, myBuyOrders };
  }, [entity.id, caseItem, userId]);
  const query = useQuery(fetcher, {
    orders: [],
    highestBid: null as Order | null,
    drops: [],
    myBuyOrders: [],
  });
  const [mode, setMode] = useState<"buy" | "sell">(
    inventoryItemId ? "sell" : "buy",
  );
  const [price, setPrice] = useState("");
  const [selectedId, setSelectedId] = useState(inventoryItemId || 0);
  const [pending, setPending] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [confirmation, setConfirmation] = useState<Order | null>(null);
  const [cancelId, setCancelId] = useState<number | null>(null);
  const [reward, setReward] = useState<CaseReward | null>(null);
  const [opening, setOpening] = useState<{
    inventoryId: number;
    drops: CaseDrop[];
    reward: CaseReward | null;
  } | null>(null);
  const openingInProgress = useRef(false);
  const [openedCaseIds, setOpenedCaseIds] = useState<number[]>([]);
  const available = inventory.filter(
    (item) =>
      item.entity_id === entity.id &&
      !item.in_sale &&
      !openedCaseIds.includes(item.id),
  );
  const chosenItem =
    available.find((item) => item.id === selectedId) || available[0];
  const { orders, highestBid, drops, myBuyOrders } = query.data;
  const lowestAsk = orders.length
    ? orders.reduce((best, order) =>
        Number(order.price) < Number(best.price) ? order : best,
      )
    : null;
  const rewardEntity = reward
    ? catalog.find((item) => item.id === reward.entity_id)
    : undefined;
  const totalWeight = drops.reduce((total, drop) => total + drop.weight, 0);

  async function perform(
    key: string,
    operation: () => Promise<unknown>,
    message: string,
  ) {
    if (pending) return;
    setPending(key);
    setError("");
    setNotice("");
    try {
      await operation();
      setConfirmation(null);
      setCancelId(null);
      setNotice(message);
      query.reload();
      await onChanged(message);
    } catch (reason) {
      setError(getErrorMessage(reason));
    } finally {
      setPending("");
    }
  }
  async function submitOrder(event: FormEvent) {
    event.preventDefault();
    if (!user) {
      onAuth();
      return;
    }
    let validPrice: string;
    try {
      validPrice = moneyInput(price);
    } catch (reason) {
      setError(getErrorMessage(reason));
      return;
    }
    if (mode === "sell" && !chosenItem) {
      setError("Choose an available item from your inventory.");
      return;
    }
    await perform(
      "order",
      () =>
        createOrder({
          entity_id: entity.id,
          price: validPrice,
          side: mode,
          ...(mode === "sell" ? { entity_in_inventory_id: chosenItem.id } : {}),
        }),
      mode === "sell"
        ? "Listing submitted. If matched, your item has already traded."
        : "Buy order submitted. Check My orders for open bids.",
    );
  }
  async function reveal() {
    if (!user) {
      onAuth();
      return;
    }
    if (!chosenItem || pending || openingInProgress.current) return;
    const id = chosenItem.id;
    openingInProgress.current = true;
    setPending("open");
    setError("");
    setNotice("");
    setReward(null);
    setOpening({ inventoryId: id, drops: [...drops], reward: null });
    try {
      const received = await openCase(id);
      setOpenedCaseIds((current) => [...current, id]);
      setOpening((current) =>
        current ? { ...current, reward: received } : current,
      );
    } catch (reason) {
      setOpening(null);
      setError(getErrorMessage(reason));
      setPending("");
      openingInProgress.current = false;
    }
  }

  async function finishOpening(received: CaseReward) {
    const message = "Case opened. Your reward is now in your inventory.";
    setReward(received);
    setNotice(message);
    query.reload();
    try {
      await onChanged(message);
    } catch (reason) {
      setError(
        `Your reward was added, but the inventory could not refresh. ${getErrorMessage(reason)}`,
      );
    } finally {
      setPending("");
      openingInProgress.current = false;
    }
  }

  if (opening) {
    return (
      <Modal
        title="Case opening"
        onClose={onClose}
        wide
        busy={Boolean(pending)}
      >
        <CaseOpening
          key={opening.inventoryId}
          caseEntity={entity}
          drops={opening.drops}
          reward={opening.reward}
          rewardEntity={
            opening.reward
              ? catalog.find((item) => item.id === opening.reward?.entity_id) ||
                opening.drops.find(
                  (drop) => drop.entity.id === opening.reward?.entity_id,
                )?.entity
              : undefined
          }
          busy={Boolean(pending)}
          error={error}
          onComplete={finishOpening}
          onBack={() => setOpening(null)}
          onDone={onClose}
        />
      </Modal>
    );
  }
  return (
    <Modal title="Item details" onClose={onClose} wide busy={Boolean(pending)}>
      <div className="detail-layout">
        <section className={`detail-art-panel ${rarityClass(entity)}`}>
          <div className="detail-category">
            <span>{categoryName(entity, categories)}</span>
            <span>#{entity.id.toString().padStart(4, "0")}</span>
          </div>
          <div className="detail-art">
            <ItemArt entity={entity} caseItem={caseItem} />
          </div>
          <span className="item-symbol">{entity.symbol}</span>
          <h2>{entity.name}</h2>
          <span className="item-rarity">
            <span className="rarity-dot" />
            {formatRarity(entity.entity_rarity)}
          </span>
          <div className="detail-price-grid">
            <div>
              <span>Lowest ask</span>
              <strong>
                {lowestAsk ? formatCurrency(lowestAsk.price) : "—"}
              </strong>
            </div>
            <div>
              <span>Highest bid</span>
              <strong>
                {highestBid ? formatCurrency(highestBid.price) : "—"}
              </strong>
            </div>
          </div>
          <p className="detail-caption">
            {available.length
              ? `${available.length} available in your inventory`
              : "Make it part of your collection."}
          </p>
        </section>
        <section className="detail-actions">
          {error && <ErrorNotice message={error} />}
          {notice && (
            <div className="success-notice" role="status">
              <Icon name="check" size={17} />
              {notice}
            </div>
          )}
          {query.error && (
            <ErrorNotice message={query.error} onRetry={query.reload} />
          )}
          {caseItem && (
            <div className="case-open-panel">
              <div>
                <span className="eyebrow">A NEW DISCOVERY</span>
                <h3>What’s inside yours?</h3>
                <p>
                  Opening consumes one case and adds a reward to your inventory.
                </p>
              </div>
              {reward && (
                <div
                  className={`reward-reveal ${rewardEntity ? rarityClass(rewardEntity) : ""}`}
                  role="status"
                >
                  <span className="eyebrow">YOU UNBOXED</span>
                  <ItemArt entity={rewardEntity} />
                  <h3>{rewardEntity?.name || `Item #${reward.entity_id}`}</h3>
                  <p>{reward.entity_wear}</p>
                </div>
              )}
              {user && available.length > 1 && (
                <label className="compact-label">
                  Your case
                  <select
                    aria-label="Case to open"
                    value={chosenItem?.id}
                    onChange={(event) =>
                      setSelectedId(Number(event.target.value))
                    }
                  >
                    {available.map((item) => (
                      <option value={item.id} key={item.id}>
                        Inventory item #{item.id}
                      </option>
                    ))}
                  </select>
                </label>
              )}
              <button
                className="button button-primary button-full"
                disabled={
                  Boolean(pending) ||
                  (Boolean(user) &&
                    (!chosenItem ||
                      !drops.length ||
                      query.loading ||
                      Boolean(query.error)))
                }
                onClick={user ? reveal : onAuth}
              >
                <Icon name="case" size={17} />
                {pending === "open"
                  ? "Opening your case…"
                  : !user
                    ? "Sign in to open a case"
                    : !chosenItem
                      ? "No available case in inventory"
                      : !drops.length
                        ? "This case has no rewards yet"
                        : "Open one case"}
              </button>
            </div>
          )}
          <div className="trade-tabs" role="group" aria-label="Order type">
            <button
              className={mode === "buy" ? "active" : ""}
              disabled={Boolean(pending)}
              onClick={() => setMode("buy")}
            >
              Buy order
            </button>
            <button
              className={mode === "sell" ? "active" : ""}
              disabled={Boolean(pending)}
              onClick={() => setMode("sell")}
            >
              Sell an item
            </button>
          </div>
          <form className="stack-form order-form" onSubmit={submitOrder}>
            <p className="small-muted">
              {mode === "buy"
                ? "Set your limit price. A matching sell listing may fill your order immediately."
                : "List an item from your inventory. A matching buy order may fill it immediately."}
            </p>
            {mode === "sell" && (
              <label>
                Inventory item
                <select
                  aria-label="Item to sell"
                  value={chosenItem?.id || ""}
                  onChange={(event) =>
                    setSelectedId(Number(event.target.value))
                  }
                  disabled={!available.length}
                >
                  <option value="" disabled>
                    {available.length ? "Choose an item" : "No available items"}
                  </option>
                  {available.map((item) => (
                    <option key={item.id} value={item.id}>
                      #{item.id} ·{" "}
                      {item.entity_wear === "NONE"
                        ? caseItem
                          ? "Unopened case"
                          : "No wear"
                        : item.entity_wear}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <div className="order-input-row">
              <label>
                Price (test USD)
                <input
                  aria-label="Order price"
                  type="number"
                  min="0.01"
                  step="0.01"
                  required
                  value={price}
                  onChange={(event) => setPrice(event.target.value)}
                  placeholder="0.00"
                />
              </label>
              <button
                className="button button-primary"
                disabled={
                  Boolean(pending) ||
                  (Boolean(user) && mode === "sell" && !chosenItem)
                }
              >
                {pending === "order"
                  ? "Submitting…"
                  : mode === "buy"
                    ? "Place buy order"
                    : "List for sale"}
                <Icon name="arrow" size={16} />
              </button>
            </div>
          </form>
          {user && (
            <section className="item-buy-orders" aria-label="Your buy orders">
              <div className="section-heading compact">
                <h3>
                  Your buy orders
                  <span className="count-badge">{myBuyOrders.length}</span>
                </h3>
              </div>
              {query.loading ? (
                <p className="small-muted" role="status">
                  Loading your buy orders…
                </p>
              ) : query.error ? (
                <p className="small-muted">
                  Buy orders could not be loaded. Try refreshing the item
                  details.
                </p>
              ) : myBuyOrders.length === 0 ? (
                <p className="small-muted">No open buy orders for this item.</p>
              ) : (
                myBuyOrders.map((order) => (
                  <div className="item-bid-row" key={order.id}>
                    <div>
                      <strong>{formatCurrency(order.price)}</strong>
                      <span>Buy order #{order.id}</span>
                    </div>
                    {cancelId === order.id ? (
                      <div className="item-bid-confirmation">
                        <span>Cancel this buy order?</span>
                        <div>
                          <button
                            className="button button-secondary button-small"
                            disabled={Boolean(pending)}
                            onClick={() => setCancelId(null)}
                          >
                            Keep buy order
                          </button>
                          <button
                            className="button button-danger button-small"
                            disabled={Boolean(pending)}
                            onClick={() =>
                              perform(
                                `cancel-bid-${order.id}`,
                                () => deleteOrder(order.id),
                                "Buy order cancelled.",
                              )
                            }
                          >
                            {pending === `cancel-bid-${order.id}`
                              ? "Cancelling…"
                              : "Confirm cancellation"}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        className="button button-secondary button-small"
                        disabled={Boolean(pending)}
                        onClick={() => setCancelId(order.id)}
                      >
                        Cancel buy order
                      </button>
                    )}
                  </div>
                ))
              )}
            </section>
          )}
        </section>
      </div>
      <section className="order-book">
        <div className="section-heading compact">
          <div>
            <span className="eyebrow">ON THE EXCHANGE</span>
            <h3>
              Available listings
              <span className="count-badge">{orders.length}</span>
            </h3>
          </div>
          <button
            className="icon-button"
            aria-label="Refresh listings"
            onClick={query.reload}
            disabled={query.loading || Boolean(pending)}
          >
            <Icon name="refresh" size={17} />
          </button>
        </div>
        {query.loading ? (
          <div className="table-loading" role="status">
            <span className="spinner" />
            Loading listings…
          </div>
        ) : !orders.length ? (
          <EmptyState
            title="Be the first to make a move."
            text="No sell listings yet. Place a buy order or list your own item."
            icon="orders"
          />
        ) : (
          <div className="book-list">
            {orders.map((order) => (
              <div className="book-row" key={order.id}>
                <div>
                  <strong>
                    {order.inventory?.entity_wear === "NONE"
                      ? caseItem
                        ? "Unopened case"
                        : "No wear"
                      : order.inventory?.entity_wear || "Collectible"}
                  </strong>
                  <small>
                    Listing #{order.id}
                    {order.user_id === user?.id ? " · Your listing" : ""}
                  </small>
                </div>
                <strong className="mono">{formatCurrency(order.price)}</strong>
                {order.user_id === user?.id ? (
                  cancelId === order.id ? (
                    <button
                      className="button button-danger button-small"
                      disabled={Boolean(pending)}
                      onClick={() =>
                        perform(
                          `cancel-${order.id}`,
                          () => deleteOrder(order.id),
                          "Listing cancelled.",
                        )
                      }
                    >
                      {pending ? "Cancelling…" : "Confirm cancel"}
                    </button>
                  ) : (
                    <button
                      className="button button-secondary button-small"
                      disabled={Boolean(pending)}
                      onClick={() => setCancelId(order.id)}
                    >
                      Cancel listing
                    </button>
                  )
                ) : (
                  <button
                    className="button button-secondary button-small"
                    disabled={Boolean(pending)}
                    onClick={() => (user ? setConfirmation(order) : onAuth())}
                  >
                    Buy item
                    <Icon name="arrow" size={14} />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
        {confirmation && (
          <div className="purchase-confirmation">
            <div>
              <strong>
                Buy {entity.name} for {formatCurrency(confirmation.price)}?
              </strong>
              <p>
                {user && Number(user.balance) < Number(confirmation.price)
                  ? "Not enough test funds. Add funds using your wallet, then try again."
                  : "The item will move to your inventory and the price will be deducted from your wallet."}
              </p>
            </div>
            <div>
              <button
                className="button button-secondary button-small"
                disabled={Boolean(pending)}
                onClick={() => setConfirmation(null)}
              >
                Go back
              </button>
              <button
                className="button button-primary button-small"
                disabled={
                  Boolean(pending) ||
                  !user ||
                  Number(user.balance) < Number(confirmation.price)
                }
                onClick={() =>
                  perform(
                    `buy-${confirmation.id}`,
                    () => buyOrder(confirmation.id),
                    "Purchase complete. Your new item is in your inventory.",
                  )
                }
              >
                {pending.startsWith("buy-") ? "Buying…" : "Confirm purchase"}
              </button>
            </div>
          </div>
        )}
      </section>
      {caseItem && (
        <section className="case-contents">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">THE POSSIBILITIES</span>
              <h3>Inside this case</h3>
            </div>
            <span className="small-muted">
              Chances calculated from API weights
            </span>
          </div>
          {drops.length ? (
            <div className="drop-grid">
              {drops.map((drop) => (
                <div
                  className={`drop-item ${rarityClass(drop.entity)}`}
                  key={drop.id}
                >
                  <ItemArt entity={drop.entity} />
                  <strong>{drop.entity.name}</strong>
                  <span>
                    {totalWeight > 0
                      ? `${((drop.weight / totalWeight) * 100).toLocaleString("en-US", { maximumFractionDigits: 2 })}% chance`
                      : "Unavailable"}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="small-muted">
              No rewards have been configured for this case.
            </p>
          )}
        </section>
      )}
    </Modal>
  );
}
