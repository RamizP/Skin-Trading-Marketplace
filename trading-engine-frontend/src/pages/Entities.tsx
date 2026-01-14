import { useEffect, useState } from "react";
import { getEntities, createEntity } from "../api/entities";
import "../styles/Entities.css";

export default function EntitiesTab({ user }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [newEntityName, setNewEntityName] = useState("");
  const [newEntitySymbol, setNewEntitySymbol] = useState("");
  const [newEntityRarity, setNewEntityRarity] = useState("uncommon");
  const [newEntityImage, setNewEntityImage] = useState("");
  const [newEntityCategoryId, setNewEntityCategoryId] = useState("");
  const [newEntitySubCategoryId, setNewEntitySubCategoryId] = useState("");
  const [creating, setCreating] = useState(false);
  const rarityOptions = [
    "common",
    "uncommon",
    "rare",
    "mythical",
    "legendary",
    "exceedingly_rare",
  ];

  useEffect(() => {
    fetchEntities();
  }, []);

  const fetchEntities = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getEntities();
      setEntities(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
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
      fetchEntities(); // refresh list
    } catch (err) {
      alert(err.message);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="entities-loading">Loading...</div>;
  if (error) return <div className="entities-error">{error}</div>;

  return (
    <section className="entities-tab fade-in">
      <div className="section-header">
        <div>
          <p className="eyebrow">Marketplace</p>
          <h2>Entities</h2>
          <p className="muted">Browse listings and monitor the lowest prices.</p>
        </div>
        <div className="pill">{entities.length} listed</div>
      </div>
      {user?.role === "admin" && (
        <div className="create-entity">
          <div className="create-field">
            <label htmlFor="entityName">New entity</label>
            <input
              id="entityName"
              type="text"
              placeholder="Entity name"
              value={newEntityName}
              onChange={(e) => setNewEntityName(e.target.value)}
            />
          </div>
          <div className="create-field">
            <label htmlFor="entitySymbol">Symbol</label>
            <input
              id="entitySymbol"
              type="text"
              placeholder="Symbol"
              value={newEntitySymbol}
              onChange={(e) => setNewEntitySymbol(e.target.value)}
            />
          </div>
          <div className="create-field">
            <label htmlFor="entityRarity">Rarity</label>
            <select
              id="entityRarity"
              value={newEntityRarity}
              onChange={(e) => setNewEntityRarity(e.target.value)}
            >
              {rarityOptions.map((rarity) => (
                <option key={rarity} value={rarity}>
                  {rarity.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <div className="create-field">
            <label htmlFor="entityImage">Image URL</label>
            <input
              id="entityImage"
              type="text"
              placeholder="https://"
              value={newEntityImage}
              onChange={(e) => setNewEntityImage(e.target.value)}
            />
          </div>
          <div className="create-field">
            <label htmlFor="entityCategory">Category ID</label>
            <input
              id="entityCategory"
              type="number"
              placeholder="Optional"
              value={newEntityCategoryId}
              onChange={(e) => setNewEntityCategoryId(e.target.value)}
            />
          </div>
          <div className="create-field">
            <label htmlFor="entitySubCategory">Sub-category ID</label>
            <input
              id="entitySubCategory"
              type="number"
              placeholder="Optional"
              value={newEntitySubCategoryId}
              onChange={(e) => setNewEntitySubCategoryId(e.target.value)}
            />
          </div>
          <button
            className="btn"
            onClick={handleCreate}
            disabled={creating || !newEntityName || !newEntitySymbol}
          >
            {creating ? "Creating..." : "Create Entity"}
          </button>
        </div>
      )}

      <div className="entities-grid">
        {entities.map((entity, index) => (
          <div
            key={entity.entity.id}
            className="entity-card"
            style={{ animationDelay: `${index * 70}ms` }}
          >
            <img
              src={entity.entity.image_url || "/placeholder.png"}
              alt={entity.entity.name}
              className="entity-img"
            />
            <div className="entity-body">
              <h3>{entity.entity.name}</h3>
              <p className="entity-rarity">{entity.entity.entity_rarity}</p>
              <div className="entity-meta">
                <span>Lowest Price</span>
                <strong>{entity.lowest_price}</strong>
              </div>
            </div>
            {/* Optionally show more info, like category/subcategory */}
          </div>
        ))}
      </div>
      {!entities.length && (
        <p className="entities-empty">No market listings yet.</p>
      )}

    </section>
  );
}
