export const API_URL = (import.meta.env.VITE_API_URL || "/api").replace(
  /\/$/,
  "",
);
const TOKEN_KEY = "exchange.session";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export const getToken = () => sessionStorage.getItem(TOKEN_KEY);
export const setToken = (token: string) =>
  sessionStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => sessionStorage.removeItem(TOKEN_KEY);

function errorDetail(data: unknown): string {
  if (typeof data !== "object" || data === null || !("detail" in data)) {
    return "The request could not be completed. Please try again.";
  }
  const detail = data.detail;
  if (typeof detail === "string") return detail;
  if (
    typeof detail === "object" &&
    detail !== null &&
    "message" in detail &&
    typeof detail.message === "string"
  )
    return detail.message;
  if (Array.isArray(detail)) {
    return detail
      .map((item: { loc?: string[]; msg?: string }) => {
        const field = item.loc?.filter((part) => part !== "body").join(" · ");
        return `${field ? `${field}: ` : ""}${item.msg || "Invalid value"}`;
      })
      .join(". ");
  }
  return "Check your details and try again.";
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authentication", token);

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
      credentials: "include",
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError")
      throw error;
    throw new ApiError(
      "Cannot reach the exchange. Check that the API is running and try again.",
      0,
    );
  }
  const text = await response.text();
  let data: unknown;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new ApiError(
      "The API returned an unexpected response. Check your API URL.",
      response.status,
    );
  }
  if (!response.ok) {
    if (
      response.status === 401 &&
      token &&
      !["/login", "/register"].includes(path)
    ) {
      clearToken();
      window.dispatchEvent(new Event("exchange:session-expired"));
    }
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? data.detail
        : undefined;
    throw new ApiError(errorDetail(data), response.status, detail);
  }
  return data as T;
}

export async function emptyOn404<T>(operation: () => Promise<T[]>) {
  try {
    return await operation();
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return [];
    throw error;
  }
}
