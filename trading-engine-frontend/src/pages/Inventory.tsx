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
  if (!inventory.length) return <div className="inventory-empty">No skins found</div>;

  return (
    <div className="inventory-grid">
      {inventory.map((item) => (
        <div key={item.id} className="inventory-card">
          <img
            src={item.entity.image_url || "/placeholder.png"}
            alt={item.entity.name}
            className="inventory-img"
          />
          <h3>{item.entity.name}</h3>
          <h3>{item.entity.entity_rarity}</h3>
          <p>Wear: {item.entity_wear}</p>
          <p>For Sale: {item.in_sale ? "Yes" : "No"}</p>
        </div>
      ))}
    </div>
  );
}
