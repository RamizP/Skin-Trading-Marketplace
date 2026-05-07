import { useEffect, useMemo, useState } from "react";
import { createEntity, getEntities } from "../api/entities";
import type { MarketEntity, User } from "../api/types";
import { formatCurrency, formatRarity, getErrorMessage } from "../utils/format";
import "../styles/Entities.css";

type EntitiesProps = {
  user: User;
  onOpenItem?: (selection: { entityId: number }) => void;
};

const rarityOptions = [
  "common",
  "uncommon",
  "rare",
  "mythical",
  "legendary",
  "exceedingly_rare",
];

const rarityClass = (rarity?: string | null) =>
  `rarity-${(rarity || "common").replace(/_/g, "-")}`;

export default function EntitiesTab({ user, onOpenItem }: EntitiesProps) {
  const [entities, setEntities] = useState<MarketEntity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [rarityFilter, setRarityFilter] = useState("all");
  const [newEntityName, setNewEntityName] = useState("");
  const [newEntitySymbol, setNewEntitySymbol] = useState("");
  const [newEntityRarity, setNewEntityRarity] = useState("uncommon");
  const [newEntityImage, setNewEntityImage] = useState("");
  const [newEntityCategoryId, setNewEntityCategoryId] = useState("");
  const [newEntitySubCategoryId, setNewEntitySubCategoryId] = useState("");
  const [creating, setCreating] = useState(false);

  const fetchEntities = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getEntities();
      setEntities(data);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to fetch entities"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchEntities();
  }, []);

  const filteredEntities = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return entities.filter((item) => {
      const entity = item.entity;
      const matchesQuery =
        !normalizedQuery ||
        entity.name.toLowerCase().includes(normalizedQuery) ||
        (entity.symbol || "").toLowerCase().includes(normalizedQuery);
      const matchesRarity =
        rarityFilter === "all" || entity.entity_rarity === rarityFilter;
      return matchesQuery && matchesRarity;
    });
  }, [entities, query, rarityFilter]);

  const handleCreate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!newEntityName || !newEntitySymbol || !newEntityRarity) return;

    setCreating(true);
    try {
      await createEntity({
        name: newEntityName.trim(),
        symbol: newEntitySymbol.trim(),
        entity_rarity: newEntityRarity,
        image_url: newEntityImage.trim() || null,
        category_id: newEntityCategoryId ? Number(newEntityCategoryId) : null,
        sub_category_id: newEntitySubCategoryId
          ? Number(newEntitySubCategoryId)
          : null,
      });
      setNewEntityName("");
      setNewEntitySymbol("");
      setNewEntityRarity("uncommon");
      setNewEntityImage("");
      setNewEntityCategoryId("");
      setNewEntitySubCategoryId("");
      await fetchEntities();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create entity"));
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="entities-loading">Loading market...</div>;
  if (error) return <div className="entities-error">{error}</div>;

  return (
    <section className="entities-tab fade-in">
      <div className="section-header">
        <div>
          <p className="eyebrow">Marketplace</p>
          <h2>Skin Listings</h2>
          <p className="muted">Scan listed items by rarity, symbol, and floor price.</p>
        </div>
        <div className="pill">{filteredEntities.length} visible</div>
      </div>

      <div className="market-toolbar">
        <label>
          <span>Search</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="AK, knife, dragon..."
          />
        </label>
        <label>
          <span>Rarity</span>
          <select
            value={rarityFilter}
            onChange={(event) => setRarityFilter(event.target.value)}
          >
            <option value="all">All rarities</option>
            {rarityOptions.map((rarity) => (
              <option key={rarity} value={rarity}>
                {formatRarity(rarity)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {user.role === "admin" && (
        <form className="create-entity" onSubmit={handleCreate}>
          <label>
            <span>New skin</span>
            <input
              type="text"
              placeholder="Item name"
              value={newEntityName}
              onChange={(event) => setNewEntityName(event.target.value)}
            />
          </label>
          <label>
            <span>Symbol</span>
            <input
              type="text"
              placeholder="Symbol"
              value={newEntitySymbol}
              onChange={(event) => setNewEntitySymbol(event.target.value)}
            />
          </label>
          <label>
            <span>Rarity</span>
            <select
              value={newEntityRarity}
              onChange={(event) => setNewEntityRarity(event.target.value)}
            >
              {rarityOptions.map((rarity) => (
                <option key={rarity} value={rarity}>
                  {formatRarity(rarity)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Image URL</span>
            <input
              type="text"
              placeholder="https://"
              value={newEntityImage}
              onChange={(event) => setNewEntityImage(event.target.value)}
            />
          </label>
          <label>
            <span>Category</span>
            <input
              type="number"
              placeholder="Optional"
              value={newEntityCategoryId}
              onChange={(event) => setNewEntityCategoryId(event.target.value)}
            />
          </label>
          <label>
            <span>Sub-category</span>
            <input
              type="number"
              placeholder="Optional"
              value={newEntitySubCategoryId}
              onChange={(event) => setNewEntitySubCategoryId(event.target.value)}
            />
          </label>
          <button
            className="btn"
            type="submit"
            disabled={creating || !newEntityName || !newEntitySymbol}
          >
            {creating ? "Creating" : "Create"}
          </button>
        </form>
      )}

      <div className="skin-grid">
          {filteredEntities.map((item, index) => (
            <button
              key={item.entity.id}
              className={`skin-card ${rarityClass(item.entity.entity_rarity)}`}
              type="button"
              style={{ animationDelay: `${index * 35}ms` }}
              onClick={() => onOpenItem?.({ entityId: item.entity.id })}
            >
              <div className="skin-image-frame">
                {item.entity.image_url ? (
                  <img src={item.entity.image_url} alt={item.entity.name} />
                ) : (
                  <span className="skin-placeholder">{item.entity.symbol || "TE"}</span>
                )}
              </div>
              <span className="skin-rarity">{formatRarity(item.entity.entity_rarity)}</span>
              <strong>{item.entity.name}</strong>
              <div className="skin-price">
                <span>Floor</span>
                <b>{item.lowest_price ? formatCurrency(item.lowest_price) : "No asks"}</b>
              </div>
              <span className="skin-action">Open Item</span>
            </button>
          ))}
      </div>
      {!filteredEntities.length && (
        <p className="entities-empty">No market listings match your filters.</p>
      )}
    </section>
  );
}
