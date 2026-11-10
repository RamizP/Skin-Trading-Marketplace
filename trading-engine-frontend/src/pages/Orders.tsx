import { useCallback, useState } from "react";
import { deleteOrder, getMyOrders } from "../api/orders";
import type {
  Category,
  Entity,
  InventoryItem,
  Order,
  User,
} from "../api/types";
import { EmptyState, ErrorNotice } from "../components/Feedback";
import Icon from "../components/Icon";
import ItemArt from "../components/ItemArt";
import useQuery from "../hooks/useQuery";
import {
  formatCurrency,
  formatDateTime,
  getErrorMessage,
  isCase,
  rarityClass,
} from "../utils/format";

export default function Orders({
  user,
  catalog,
  inventory,
  categories,
  onAuth,
  onOpen,
  onChanged,
  onMarket,
}: {
  user: User | null;
  catalog: Entity[];
  inventory: InventoryItem[];
  categories: Category[];
  onAuth: () => void;
  onOpen: (entity: Entity) => void;
  onChanged: (message?: string) => Promise<void>;
  onMarket: () => void;
}) {
  const fetcher = useCallback(
    () =>
      user
        ? getMyOrders(
            catalog.map((entity) => entity.id),
            inventory
              .filter((item) => item.in_sale)
              .map((item) => item.entity_id),
            user.id,
          )
        : Promise.resolve([]),
    [user, catalog, inventory],
  );
  const query = useQuery(fetcher, []);
  const [filter, setFilter] = useState("all");
  const [pending, setPending] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [confirm, setConfirm] = useState<number | null>(null);
  async function cancel(order: Order) {
    setPending(order.id);
    setError("");
    try {
      await deleteOrder(order.id);
      setConfirm(null);
      query.reload();
      await onChanged(
        order.side === "sell"
          ? "Listing cancelled. Your item is available again."
          : "Buy order cancelled.",
      );
    } catch (reason) {
      setError(getErrorMessage(reason));
    } finally {
      setPending(null);
    }
  }
  if (!user)
    return (
      <EmptyState
        title="Keep your trades in sight."
        text="Sign in to manage your sell listings and buy orders."
        icon="orders"
        action="Sign in"
        onAction={onAuth}
      />
    );
  const visible = query.data.filter(
    (order) => filter === "all" || order.side === filter,
  );
  return (
    <section className="page-enter">
      <div className="page-heading">
        <div>
          <span className="eyebrow">THE TRADES YOU MAKE</span>
          <h1>
            My orders<span className="count-badge">{query.data.length}</span>
          </h1>
          <p>A clear view of your listings and open buy orders.</p>
        </div>
        <button
          className="button button-secondary"
          onClick={query.reload}
          disabled={query.loading}
        >
          <Icon name="refresh" size={16} />
          Refresh orders
        </button>
      </div>
      <div className="category-tabs" role="group" aria-label="Order filters">
        {[
          ["all", "All orders"],
          ["sell", "Sell listings"],
          ["buy", "Buy orders"],
        ].map(([value, label]) => (
          <button
            className={filter === value ? "active" : ""}
            onClick={() => setFilter(value)}
            key={value}
          >
            {label}
            <span className="tab-count">
              {
                query.data.filter(
                  (order) => value === "all" || order.side === value,
                ).length
              }
            </span>
          </button>
        ))}
      </div>
      {(query.error || error) && (
        <ErrorNotice message={query.error || error} onRetry={query.reload} />
      )}
      {query.loading ? (
        <div className="table-loading" role="status">
          <span className="spinner" />
          Loading your open orders…
        </div>
      ) : !query.error && !visible.length ? (
        <EmptyState
          title="A clean slate."
          text="You have no open orders in this view. Find something worth trading."
          icon="orders"
          action="Explore marketplace"
          onAction={onMarket}
        />
      ) : (
        <div className="orders-table">
          <div className="table-heading">
            <span>ITEM / ORDER</span>
            <span>TYPE</span>
            <span>PRICE</span>
            <span>CREATED</span>
            <span>ACTION</span>
          </div>
          {visible.map((order) => {
            const entity = catalog.find((item) => item.id === order.entity_id);
            return (
              <article className="order-row" key={order.id}>
                <button
                  className={`order-item ${entity ? rarityClass(entity) : ""}`}
                  onClick={() => {
                    if (entity) onOpen(entity);
                  }}
                >
                  <div className="order-thumb">
                    <ItemArt
                      entity={entity}
                      caseItem={entity ? isCase(entity, categories) : false}
                    />
                  </div>
                  <span>
                    <strong>
                      {entity?.name || `Item #${order.entity_id}`}
                    </strong>
                    <small>
                      Order #{order.id}
                      {order.inventory
                        ? ` · ${order.inventory.entity_wear}`
                        : ""}
                    </small>
                  </span>
                </button>
                <span className={`order-side ${order.side}`}>
                  {order.side === "sell" ? "Sell listing" : "Buy order"}
                </span>
                <strong className="mono">{formatCurrency(order.price)}</strong>
                <time dateTime={order.created_at}>
                  {formatDateTime(order.created_at)}
                </time>
                <div className="order-action">
                  {confirm === order.id ? (
                    <>
                      <button
                        className="button button-danger button-small"
                        disabled={pending !== null}
                        onClick={() => cancel(order)}
                      >
                        {pending === order.id ? "Cancelling…" : "Confirm"}
                      </button>
                      <button
                        className="icon-button"
                        aria-label="Keep order"
                        disabled={pending !== null}
                        onClick={() => setConfirm(null)}
                      >
                        <Icon name="close" size={15} />
                      </button>
                    </>
                  ) : (
                    <button
                      className="button button-secondary button-small"
                      disabled={pending !== null}
                      onClick={() => setConfirm(order.id)}
                    >
                      {order.side === "buy"
                        ? "Cancel buy order"
                        : "Cancel listing"}
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
      <div className="inline-note">
        <Icon name="info" size={16} />
        Matched orders disappear from this list. Only currently open orders are
        shown.
      </div>
    </section>
  );
}
