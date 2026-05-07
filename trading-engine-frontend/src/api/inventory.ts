import { API_URL } from "./client";
import type { InventoryItem } from "./types";

type ApiError = {
  detail?: string;
};

export async function getInventory(): Promise<InventoryItem[]> {
  const res = await fetch(`${API_URL}/inventory/me`, {
    method: "GET",
    credentials: "include", // important for your auth cookie
  });

  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    const message = err.detail || "Failed to fetch inventory";
    if (message.toLowerCase().includes("inventory not found")) {
      return [];
    }
    throw new Error(message);
  }

  return res.json() as Promise<InventoryItem[]>;
}
