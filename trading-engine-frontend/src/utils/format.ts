export const formatNumber = (value: number | null | undefined) => {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "0";
  return new Intl.NumberFormat("en-US").format(amount);
};

export const formatCurrency = (
  value: number | null | undefined,
  currency: string = "USD"
) => {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "$0.00";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatDateTime = (value: string | number | Date | null) => {
  if (!value) return "";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

export const formatRarity = (rarity?: string | null) => {
  if (!rarity) return "Common";
  return rarity
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
};

export const getErrorMessage = (error: unknown, fallback = "Something went wrong") => {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return fallback;
};
