const API_URL = "https://192.168.1.236:8000";

export async function getEntities(skip = 0, limit = 50) {
  const res = await fetch(`${API_URL}/orders`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch entities");
  }
  return res.json();
}

export async function createEntity(entity) {
  const res = await fetch(`${API_URL}/entities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(entity),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create entity");
  }
  return res.json();
}
