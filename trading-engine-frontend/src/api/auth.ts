import { API_URL } from "./client";
import type { User } from "./types";

type ApiError = {
  detail?: string;
};

export async function loginUser(username: string, password: string) {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // IMPORTANT for cookies
    body: JSON.stringify({
      username,
      password,
    }),
  });

  const data = (await response.json()) as ApiError;

  if (!response.ok) {
    throw new Error(data.detail || "Invalid credentials");
  }

  return data;
}

export async function logoutUser() {
  await fetch(`${API_URL}/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function getMe(): Promise<User> {
  const response = await fetch(`${API_URL}/user/me`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Not authenticated");
  }

  return response.json() as Promise<User>;
}

export async function chargeBalance(amount: number): Promise<User> {
  const response = await fetch(`${API_URL}/me/balance/charge`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ amount }),
  });

  const data = (await response.json()) as User & ApiError;

  if (!response.ok) {
    throw new Error(data.detail || "Failed to charge balance");
  }

  return data;
}

export async function registerUser(
  username: string,
  email: string,
  password: string,
  bio?: string,
  location?: string,
) {
  const response = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({
      username,
      email,
      password,
      bio: bio || undefined,
      location: location || undefined,
    }),
  });

  const data = (await response.json()) as ApiError;

  if (!response.ok) {
    throw new Error(data.detail || "Could not create your account");
  }

  return data;
}
