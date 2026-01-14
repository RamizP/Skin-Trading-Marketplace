const API_URL = "https://127.0.0.1:8000"; // adjust if needed

export async function loginUser(username, password) {
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

  const data = await response.json();

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

export async function getMe() {
  const response = await fetch(`${API_URL}/user/me`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Not authenticated");
  }

  return response.json();
}

export async function chargeBalance(amount: number) {
  const response = await fetch(`${API_URL}/me/balance/charge`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ amount }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to charge balance");
  }

  return data;
}
