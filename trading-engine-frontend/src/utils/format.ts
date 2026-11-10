import type { Category, Entity, Money } from "../api/types";

export const formatCurrency = (value: Money | null | undefined) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value ?? 0));
export const formatDateTime = (value: string) =>
  new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(
    new Date(
      value.endsWith("Z") || /[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`,
    ),
  );
export const formatRarity = (value = "common") => value.replace(/_/g, " ");
export const getErrorMessage = (error: unknown) =>
  error instanceof Error
    ? error.message
    : "Something went wrong. Please try again.";
export const rarityClass = (entity: Entity) =>
  `rarity-${entity.entity_rarity || "common"}`;
export const isCase = (entity: Entity, categories: Category[]) =>
  categories.some(
    (category) =>
      category.id === entity.category_id &&
      category.name.toLowerCase() === "case",
  );
export const categoryName = (entity: Entity, categories: Category[]) =>
  categories.find((category) => category.id === entity.category_id)?.name ||
  "Collectible";
export const wearOptions = [
  "NONE",
  "Factory New",
  "Minimal Wear",
  "Field-Tested",
  "Well-Worn",
  "Battle-Scarred",
];
export const rarities = [
  "common",
  "uncommon",
  "rare",
  "mythical",
  "legendary",
  "exceedingly_rare",
];

// Keep the decimal string intact on its journey to Pydantic/Decimal.
export function moneyInput(value: string) {
  if (
    !/^\d+(\.\d{1,2})?$/.test(value) ||
    Number(value) <= 0 ||
    Number(value) >= 10_000_000_000
  ) {
    throw new Error("Enter a positive amount with at most two decimal places.");
  }
  return value;
}
