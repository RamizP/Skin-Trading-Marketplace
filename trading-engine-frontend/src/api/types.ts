export type Money = string | number;
export type User = {
  id: number;
  username: string;
  email: string | null;
  role: string;
  status: string;
  balance: Money;
  image_url?: string | null;
};
export type Entity = {
  id: number;
  name: string;
  symbol: string;
  image_url?: string | null;
  entity_rarity: string;
  category_id: number | null;
  sub_category_id?: number | null;
};
export type Category = { id: number; name: string };
export type MarketEntity = { entity: Entity; lowest_price: Money | null };
export type InventoryItem = {
  id: number;
  user_id: number;
  entity_id: number;
  entity_wear: string;
  in_sale: boolean;
  entity: Entity;
};
export type Order = {
  id: number;
  user_id: number;
  entity_id: number;
  price: Money;
  side: "buy" | "sell";
  inventory?: InventoryItem | null;
  created_at: string;
};
export type CaseDrop = {
  id: number;
  case_entity_id: number;
  reward_entity_id: number;
  weight: number;
  entity: Entity;
};
export type CaseReward = { entity_id: number; entity_wear: string };
export type View = "market" | "inventory" | "orders" | "cases";
