import { API_URL } from "./client";

export async function getOrdersByEntity(entityId: number) {
  const res = await fetch(`${API_URL}/orders/${entityId}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch orders");
  }
  return res.json();
}

export async function createOrder(payload: {
  price: number;
  side: "buy" | "sell";
  entity_id?: number | null;
  entity_in_inventory_id?: number | null;
}) {
  const res = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Failed to create order");
  }
  return data;
}

export async function buyOrder(orderId: number) {
  const res = await fetch(`${API_URL}/order/buy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ order_id: orderId }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Failed to buy order");
  }
  return data;
}

export async function deleteOrder(orderId: number) {
  const res = await fetch(`${API_URL}/order`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ order_id: orderId }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Failed to delete order");
  }
  return data;
}
