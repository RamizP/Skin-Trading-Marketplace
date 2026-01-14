import { useEffect, useState } from "react";
import { getInventory } from "../api/inventory";
import "../styles/Inventory.css";

export default function InventoryTab() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getInventory()
      .then(setInventory)
      .catch(() => setError("Failed to load inventory"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="inventory-loading">Loading...</div>;
  if (error) return <div className="inventory-error">{error}</div>;
  if (!inventory.length) return <div className="inventory-empty">No inventory items found</div>;

  return (
    <section className="inventory-section fade-in">
      <div className="section-header">
        <div>
          <p className="eyebrow">Portfolio</p>
          <h2>Your Inventory</h2>
          <p className="muted">Track holdings, condition, and sale status.</p>
        </div>
        <div className="pill">{inventory.length} items</div>
      </div>
      <div className="inventory-grid">
        {inventory.map((item, index) => (
          <div
            key={item.id}
            className="inventory-card"
            style={{ animationDelay: `${index * 80}ms` }}
          >
            <img
              src={item.entity.image_url || "/placeholder.png"}
              alt={item.entity.name}
              className="inventory-img"
            />
            <div className="inventory-body">
              <h3>{item.entity.name}</h3>
              <p className="inventory-rarity">{item.entity.entity_rarity}</p>
              <div className="inventory-meta">
                <span>Wear</span>
                <strong>{item.entity_wear}</strong>
              </div>
              <div className="inventory-meta">
                <span>For Sale</span>
                <strong>{item.in_sale ? "Yes" : "No"}</strong>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
