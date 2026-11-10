import { emptyOn404, request } from "./client";
import type { InventoryItem } from "./types";

export const getInventory = () =>
  emptyOn404(() => request<InventoryItem[]>("/inventory/me"));
export const chargeInventory = (entityId: number, wear: string) =>
  request<InventoryItem[]>("/inventory/me/charge", {
    method: "POST",
    body: JSON.stringify({ entity_id: entityId, entity_wear: wear }),
  });
