import { emptyOn404, request } from "./client";
import type { Category, Entity, MarketEntity } from "./types";

export const getEntities = () =>
  emptyOn404(() => request<MarketEntity[]>("/orders"));
export const getCategories = () => request<Category[]>("/category");
export async function getAllEntities(): Promise<Entity[]> {
  const entities: Entity[] = [];
  let page: Entity[];
  do {
    page = await request<Entity[]>(
      `/entities?skip=${entities.length}&limit=100`,
    );
    entities.push(...page);
  } while (page.length === 100);
  return entities;
}
export const getEntity = (id: number) => request<Entity>(`/entities/${id}`);
export const createEntity = (entity: Omit<Entity, "id">) =>
  request<string>("/entities", {
    method: "POST",
    body: JSON.stringify(entity),
  });
