const API_URL = "https://192.168.1.236:8000";

export async function getInventory() {
  const res = await fetch(`${API_URL}/inventory/me`, {
    method: "GET",
    credentials: "include", // important for your auth cookie
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch inventory");
  }

  return res.json();
}
