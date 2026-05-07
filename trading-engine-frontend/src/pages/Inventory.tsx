import { useEffect, useMemo, useState } from "react";
import { getInventory } from "../api/inventory";
import type { InventoryItem } from "../api/types";
import { formatRarity } from "../utils/format";
import "../styles/Inventory.css";

const saleFilters = [
  { value: "all", label: "All" },
  { value: "available", label: "Available" },
  { value: "listed", label: "Listed" },
];

type InventoryProps = {
  onOpenItem?: (selection: { entityId: number; inventoryItemId: number }) => void;
};

export default function InventoryTab({ onOpenItem }: InventoryProps) {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [saleFilter, setSaleFilter] = useState("all");

  useEffect(() => {
    getInventory()
      .then(setInventory)
      .catch(() => setError("Failed to load inventory"))
      .finally(() => setLoading(false));
  }, []);

  const filteredInventory = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return inventory.filter((item) => {
      const matchesQuery =
        !normalizedQuery ||
        item.entity.name.toLowerCase().includes(normalizedQuery) ||
        (item.entity.symbol || "").toLowerCase().includes(normalizedQuery) ||
        item.entity_wear.toLowerCase().includes(normalizedQuery);
      const matchesSale =
        saleFilter === "all" ||
        (saleFilter === "listed" && item.in_sale) ||
        (saleFilter === "available" && !item.in_sale);
      return matchesQuery && matchesSale;
    });
  }, [inventory, query, saleFilter]);

  const listedCount = inventory.filter((item) => item.in_sale).length;

  if (loading) return <div className="inventory-loading">Loading inventory...</div>;
  if (error) return <div className="inventory-error">{error}</div>;

  return (
    <section className="inventory-section fade-in">
      <div className="section-header">
        <div>
          <p className="eyebrow">Portfolio</p>
          <h2>Your Inventory</h2>
          <p className="muted">Manage owned skins by wear, rarity, and listing status.</p>
        </div>
        <div className="pill">{inventory.length} items</div>
      </div>

      <div className="inventory-summary">
        <div>
          <span>Total Items</span>
          <strong>{inventory.length}</strong>
        </div>
        <div>
          <span>Listed</span>
          <strong>{listedCount}</strong>
        </div>
        <div>
          <span>Ready To Sell</span>
          <strong>{inventory.length - listedCount}</strong>
        </div>
      </div>

      <div className="market-toolbar">
        <label>
          <span>Search inventory</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Name, symbol, wear..."
          />
        </label>
        <div className="segmented-control" role="group" aria-label="Sale status filter">
          {saleFilters.map((filter) => (
            <button
              key={filter.value}
              className={saleFilter === filter.value ? "active" : ""}
              type="button"
              onClick={() => setSaleFilter(filter.value)}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      {!filteredInventory.length ? (
        <div className="inventory-empty">No inventory items match the current filters.</div>
      ) : (
        <div className="inventory-table" role="table" aria-label="Inventory items">
          <div className="inventory-table-head" role="row">
            <span>Item</span>
            <span>Rarity</span>
            <span>Wear</span>
            <span>Status</span>
          </div>
          {filteredInventory.map((item, index) => (
            <button
              key={item.id}
              className={`inventory-row ${item.in_sale ? "listed" : ""}`}
              role="row"
              type="button"
              style={{ animationDelay: `${index * 35}ms` }}
              onClick={() =>
                onOpenItem?.({ entityId: item.entity_id, inventoryItemId: item.id })
              }
            >
              <div className="inventory-item-cell">
                <div className="inventory-thumb">
                  {item.entity.image_url ? (
                    <img src={item.entity.image_url} alt={item.entity.name} />
                  ) : (
                    <span>{item.entity.symbol || "TE"}</span>
                  )}
                </div>
                <div>
                  <strong>{item.entity.name}</strong>
                  <small>{item.entity.symbol || "No symbol"}</small>
                </div>
              </div>
              <span>{formatRarity(item.entity.entity_rarity)}</span>
              <span>{item.entity_wear}</span>
              <strong className={item.in_sale ? "status-listed" : "status-ready"}>
                {item.in_sale ? "Listed" : "Ready"}
              </strong>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
