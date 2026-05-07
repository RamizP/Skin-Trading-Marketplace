import { API_URL } from "./client";
import type { Entity, MarketEntity } from "./types";

type ApiError = {
  detail?: string;
};

export async function getEntities(): Promise<MarketEntity[]> {
  const res = await fetch(`${API_URL}/orders`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    const message = err.detail || "Failed to fetch entities";
    if (message.toLowerCase().includes("no orders")) {
      return [];
    }
    throw new Error(message);
  }
  return res.json() as Promise<MarketEntity[]>;
}

export async function getAllEntities(skip = 0, limit = 50): Promise<Entity[]> {
  const res = await fetch(`${API_URL}/entities?skip=${skip}&limit=${limit}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    throw new Error(err.detail || "Failed to fetch entities");
  }
  return res.json() as Promise<Entity[]>;
}

export async function getEntity(entityId: number): Promise<Entity> {
  const res = await fetch(`${API_URL}/entities/${entityId}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    throw new Error(err.detail || "Failed to fetch entity");
  }
  return res.json() as Promise<Entity>;
}

export async function createEntity(entity: {
  name: string;
  symbol: string;
  entity_rarity: string;
  image_url?: string | null;
  category_id?: number | null;
  sub_category_id?: number | null;
}): Promise<Entity> {
  const res = await fetch(`${API_URL}/entities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(entity),
  });
  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    throw new Error(err.detail || "Failed to create entity");
  }
  return res.json() as Promise<Entity>;
}
