export type User = {
  id: number;
  username?: string | null;
  email?: string | null;
  role?: string | null;
  status?: string | null;
  location?: string | null;
  balance?: number | null;
};

export type Entity = {
  id: number;
  name: string;
  symbol?: string | null;
  image_url?: string | null;
  entity_rarity?: string | null;
  category_id?: number | null;
  sub_category_id?: number | null;
};

export type MarketEntity = {
  entity: Entity;
  lowest_price: number | null;
};

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
  price: number;
  side: "buy" | "sell";
  inventory?: InventoryItem | null;
  created_at: string;
};
