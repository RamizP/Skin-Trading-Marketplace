import { useEffect, useState } from "react";
import { getEntities, createEntity } from "../api/entities";
import "../styles/Entities.css";

export default function EntitiesTab({ user }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [newEntityName, setNewEntityName] = useState("");
  const [creating, setCreating] = useState(false);

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
    if (!newEntityName) return;
    setCreating(true);
    try {
      await createEntity({ name: newEntityName });
      setNewEntityName("");
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
    <div className="entities-tab">
      {user?.role === "admin" && (
        <div className="create-entity">
          <input
            type="text"
            placeholder="New entity name"
            value={newEntityName}
            onChange={(e) => setNewEntityName(e.target.value)}
          />
          <button onClick={handleCreate} disabled={creating}>
            {creating ? "Creating..." : "Create Entity"}
          </button>
        </div>
      )}

      <div className="entities-grid">
        {entities.map((entity) => (
          <div key={entity.entity.id} className="entity-card">
            <img
               src={entity.entity.image_url || "/placeholder.png"}
               alt={entity.entity.name}
               className="inventory-img"
             />
            <h3>{entity.entity.name}</h3>
            <h3>{entity.entity.entity_rarity}</h3>
            <p>Lowest Price: {entity.lowest_price}</p>
            {/* Optionally show more info, like category/subcategory */}
          </div>
        ))}
      </div>

    </div>
  );
}
