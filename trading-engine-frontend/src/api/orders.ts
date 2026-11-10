import { ApiError, emptyOn404, request } from "./client";
import type { Order } from "./types";

export const getOrdersByEntity = (id: number) =>
  emptyOn404(() => request<Order[]>(`/orders/${id}`));
export const getMyBuyOrdersByEntity = (id: number) =>
  request<Order[]>(`/buy-orders/${id}/me`);
export async function getHighestBuyOrdersByEntity(
  id: number,
): Promise<Order | null> {
  try {
    return await request<Order>(`/buy-orders/${id}/highest`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}
export const createOrder = (payload: {
  price: string;
  side: "buy" | "sell";
  entity_id: number;
  entity_in_inventory_id?: number;
}) =>
  request<Order>("/orders", { method: "POST", body: JSON.stringify(payload) });
export const buyOrder = (id: number) =>
  request<Order>("/order/buy", {
    method: "POST",
    body: JSON.stringify({ order_id: id }),
  });
export const deleteOrder = (id: number) =>
  request<Order>("/order", {
    method: "DELETE",
    body: JSON.stringify({ order_id: id }),
  });

// The API exposes bids per entity. Bound parallel requests when collecting them.
export async function getMyOrders(
  entityIds: number[],
  listedEntityIds: number[],
  userId: number,
) {
  const output: Order[] = [];
  const listed = new Set(listedEntityIds);
  let next = 0;
  await Promise.all(
    Array.from({ length: Math.min(4, entityIds.length) }, async () => {
      while (next < entityIds.length) {
        const id = entityIds[next++];
        const [bids, asks] = await Promise.all([
          getMyBuyOrdersByEntity(id),
          listed.has(id) ? getOrdersByEntity(id) : Promise.resolve([]),
        ]);
        output.push(
          ...bids,
          ...asks.filter((order) => order.user_id === userId),
        );
      }
    }),
  );
  return output.sort((a, b) => b.id - a.id);
}
