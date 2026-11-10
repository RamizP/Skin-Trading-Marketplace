import { clearToken, request, setToken } from "./client";
import type { User } from "./types";

export async function loginUser(username: string, password: string) {
  const data = await request<{ token: string }>("/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setToken(data.token);
}
export async function registerUser(
  username: string,
  email: string,
  password: string,
) {
  const data = await request<{ token: string }>("/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
  setToken(data.token);
}
export async function logoutUser() {
  try {
    await request("/logout", { method: "POST" });
  } finally {
    clearToken();
  }
}
export const getMe = () => request<User>("/user/me");
export const chargeBalance = (amount: string) =>
  request<User>("/me/balance/charge", {
    method: "POST",
    body: JSON.stringify({ amount }),
  });
