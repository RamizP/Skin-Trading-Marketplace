const API_URL = "https://127.0.0.1:8000";

export async function getInventory() {
  const res = await fetch(`${API_URL}/inventory/me`, {
    method: "GET",
    credentials: "include", // important for your auth cookie
  });

  if (!res.ok) {
    const err = await res.json();
    const message = err.detail || "Failed to fetch inventory";
    if (message.toLowerCase().includes("inventory not found")) {
      return [];
    }
    throw new Error(message);
  }

  return res.json();
}
