import { API_URL } from "./client";
import type { Order } from "./types";

type ApiError = {
  detail?: string;
};

export async function getOrdersByEntity(entityId: number): Promise<Order[]> {
  const res = await fetch(`${API_URL}/orders/${entityId}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    throw new Error(err.detail || "Failed to fetch orders");
  }
  return res.json() as Promise<Order[]>;
}

export async function getMyBuyOrdersByEntity(entityId: number): Promise<Order[]> {
  const res = await fetch(`${API_URL}/buy-orders/${entityId}/me`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    throw new Error(err.detail || "Failed to fetch buy orders");
  }
  return res.json() as Promise<Order[]>;
}

export async function createOrder(payload: {
  price: number;
  side: "buy" | "sell";
  entity_id?: number | null;
  entity_in_inventory_id?: number | null;
}): Promise<Order> {
  const res = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const data = (await res.json()) as Order & ApiError;
  if (!res.ok) {
    throw new Error(data.detail || "Failed to create order");
  }
  return data;
}

export async function buyOrder(orderId: number): Promise<unknown> {
  const res = await fetch(`${API_URL}/order/buy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ order_id: orderId }),
  });
  const data = (await res.json()) as ApiError;
  if (!res.ok) {
    throw new Error(data.detail || "Failed to buy order");
  }
  return data;
}

export async function deleteOrder(orderId: number): Promise<unknown> {
  const res = await fetch(`${API_URL}/order`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ order_id: orderId }),
  });
  const data = (await res.json()) as ApiError;
  if (!res.ok) {
    throw new Error(data.detail || "Failed to delete order");
  }
  return data;
}
