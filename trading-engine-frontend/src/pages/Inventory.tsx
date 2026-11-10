import { useState } from "react";
import type { Category, Entity, InventoryItem, User } from "../api/types";
import { EmptyState, ErrorNotice, SkeletonCards } from "../components/Feedback";
import Icon from "../components/Icon";
import ItemArt from "../components/ItemArt";
import {
  categoryName,
  formatRarity,
  isCase,
  rarityClass,
} from "../utils/format";

export default function Inventory({
  user,
  items,
  categories,
  loading,
  error,
  onRetry,
  onAuth,
  onOpen,
  onAdd,
  onMarket,
}: {
  user: User | null;
  items: InventoryItem[];
  categories: Category[];
  loading: boolean;
  error: string;
  onRetry: () => void;
  onAuth: () => void;
  onOpen: (entity: Entity, inventoryId?: number) => void;
  onAdd: () => void;
  onMarket: () => void;
}) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  if (!user)
    return (
      <EmptyState
        title="Your collection starts here."
        text="Sign in to see your items, manage listings, and open your cases."
        icon="inventory"
        action="Sign in"
        onAction={onAuth}
      />
    );
  const visible = items.filter(
    (item) =>
      `${item.entity.name} ${item.entity.symbol}`
        .toLowerCase()
        .includes(search.toLowerCase()) &&
      (filter === "all" ||
        (filter === "listed"
          ? item.in_sale
          : filter === "cases"
            ? isCase(item.entity, categories)
            : !item.in_sale)),
  );
  return (
    <section className="page-enter">
      <div className="page-heading">
        <div>
          <span className="eyebrow">OWN YOUR NEXT MOVE</span>
          <h1>
            My inventory<span className="count-badge">{items.length}</span>
          </h1>
          <p>Your collection, ready for whatever comes next.</p>
        </div>
        <button className="button button-secondary" onClick={onAdd}>
          <Icon name="plus" size={17} />
          Get a test item
        </button>
      </div>
      <div className="stat-row">
        <div>
          <span>Total items</span>
          <strong>{items.length.toString().padStart(2, "0")}</strong>
          <Icon name="inventory" />
        </div>
        <div>
          <span>Available to trade</span>
          <strong>
            {items
              .filter((item) => !item.in_sale)
              .length.toString()
              .padStart(2, "0")}
          </strong>
          <Icon name="bolt" />
        </div>
        <div>
          <span>Listed for sale</span>
          <strong>
            {items
              .filter((item) => item.in_sale)
              .length.toString()
              .padStart(2, "0")}
          </strong>
          <Icon name="market" />
        </div>
        <div>
          <span>Cases to discover</span>
          <strong>
            {items
              .filter(
                (item) => isCase(item.entity, categories) && !item.in_sale,
              )
              .length.toString()
              .padStart(2, "0")}
          </strong>
          <Icon name="case" />
        </div>
      </div>
      <div className="catalog-toolbar">
        <label className="search-field">
          <Icon name="search" size={18} />
          <input
            aria-label="Search inventory"
            placeholder="Find something in your collection…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <button
          className="button button-secondary"
          onClick={onRetry}
          disabled={loading}
        >
          <Icon name="refresh" size={16} />
          Refresh
        </button>
      </div>
      <div
        className="category-tabs"
        role="group"
        aria-label="Inventory filters"
      >
        {[
          ["all", "All items"],
          ["available", "Available"],
          ["listed", "Listed for sale"],
          ["cases", "Cases"],
        ].map(([value, label]) => (
          <button
            className={filter === value ? "active" : ""}
            key={value}
            onClick={() => setFilter(value)}
          >
            {label}
          </button>
        ))}
      </div>
      {error ? (
        <ErrorNotice message={error} onRetry={onRetry} />
      ) : loading ? (
        <SkeletonCards />
      ) : visible.length ? (
        <div className="item-grid inventory-grid">
          {visible.map((item) => (
            <button
              key={item.id}
              className={`item-card ${rarityClass(item.entity)}`}
              onClick={() => onOpen(item.entity, item.id)}
              aria-label={`Manage ${item.entity.name}`}
            >
              <div className="item-card-top">
                <span>{categoryName(item.entity, categories)}</span>
                <span className={`item-state ${item.in_sale ? "listed" : ""}`}>
                  {item.in_sale ? "Listed" : "Available"}
                </span>
              </div>
              <div className="card-art">
                <ItemArt
                  entity={item.entity}
                  caseItem={isCase(item.entity, categories)}
                />
              </div>
              <div className="item-card-copy">
                <span className="item-symbol">{item.entity.symbol}</span>
                <h3>{item.entity.name}</h3>
                <span className="item-rarity">
                  <span className="rarity-dot" />
                  {formatRarity(item.entity.entity_rarity)}
                </span>
                <div className="item-card-footer">
                  <span className="wear-label">
                    {item.entity_wear === "NONE"
                      ? isCase(item.entity, categories)
                        ? "Unopened case"
                        : "No wear"
                      : item.entity_wear}
                  </span>
                  <span className="inventory-action">
                    {item.in_sale
                      ? "Manage"
                      : isCase(item.entity, categories)
                        ? "Open case"
                        : "Sell item"}
                    <Icon name="arrow" size={15} />
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <EmptyState
          title={
            items.length ? "No items match." : "A collection waiting to happen."
          }
          text={
            items.length
              ? "Choose another filter or search for a different item."
              : "Pick up your first collectible on the market, or add a test item to explore trading."
          }
          action={items.length ? "Clear filters" : "Browse marketplace"}
          onAction={
            items.length
              ? () => {
                  setFilter("all");
                  setSearch("");
                }
              : onMarket
          }
        />
      )}
    </section>
  );
}
