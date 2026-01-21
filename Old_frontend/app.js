const API_BASE = "https://192.168.1.236:8000";

// Utility to format timestamps
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString();
}

// === Register ===
async function register() {
  const username = document.getElementById("reg-username").value;
  const password = document.getElementById("reg-password").value;

  const res = await fetch(`${API_BASE}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const text = await res.text();
  alert(text);
}

// === Login ===
async function login() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const text = await res.text();
  alert(text);
}

// === Logout ===
async function logout() {
  const res = await fetch(`${API_BASE}/logout`, {
    method: "POST"
  });

  const text = await res.text();
  alert(text);
}

// === Get User Info ===
async function getMe() {
  const res = await fetch(`${API_BASE}/me`, {
    method: "GET"
  });

  if (!res.ok) {
    alert("Failed to get user info");
    return;
  }

  const user = await res.json();

  document.getElementById("user-info").innerHTML = `
    <strong>Username:</strong> ${user.username}<br>
    <strong>Email:</strong> ${user.email}<br>
    <strong>Role:</strong> ${user.role}<br>
    <strong>Status:</strong> ${user.status}<br>
    <strong>Balance:</strong> $${user.balance}<br>
    <strong>Location:</strong> ${user.location}<br>
    <strong>Joined:</strong> ${formatDate(user.created_at)}
  `;
}

// === Charge Balance ===
async function chargeBalance() {
  const amount = parseFloat(document.getElementById("charge-amount").value);
  if (isNaN(amount) || amount <= 0) {
    alert("Enter a valid amount");
    return;
  }

  const res = await fetch(`${API_BASE}/balance-charge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount })
  });

  if (!res.ok) {
    alert("Failed to charge balance");
    return;
  }

  const user = await res.json();
  alert("New balance: $" + user.balance);
}

// === Get Inventory ===
async function getInventory() {
  const res = await fetch(`${API_BASE}/myinventory`, {
    method: "GET"
  });

  if (!res.ok) {
    document.getElementById("inventory-info").textContent = "No inventory found.";
    return;
  }

  const items = await res.json();

  const html = `
    <table>
      <thead>
        <tr><th>Entity ID</th><th>Amount</th></tr>
      </thead>
      <tbody>
        ${items.map(i => `<tr><td>${i.entity_id}</td><td>${i.amount}</td></tr>`).join("")}
      </tbody>
    </table>
  `;

  document.getElementById("inventory-info").innerHTML = html;
}

// === Get Orders ===
async function getOrders() {
  const res = await fetch(`${API_BASE}/orders`, {
    method: "GET"
  });

  if (!res.ok) {
    document.getElementById("orders-info").textContent = "No orders found.";
    return;
  }

  const orders = await res.json();

  const html = `
    <table>
      <thead>
        <tr><th>ID</th><th>Entity ID</th><th>Price</th><th>Amount</th><th>Created At</th></tr>
      </thead>
      <tbody>
        ${orders.map(o => `
          <tr>
            <td>${o.id}</td>
            <td>${o.entity_id}</td>
            <td>$${o.price}</td>
            <td>${o.amount}</td>
            <td>${formatDate(o.created_at)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;

  document.getElementById("orders-info").innerHTML = html;
}
// === Create Order ===
async function createOrder() {
    const entity_id = parseInt(document.getElementById("order-entity-id").value);
    const price = parseFloat(document.getElementById("order-price").value);
    const amount = parseInt(document.getElementById("order-amount").value);

    if (!entity_id || !price || !amount || price <= 0 || amount <= 0) {
      alert("Please fill all fields with valid values.");
      return;
    }

    const res = await fetch(`${API_BASE}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entity_id, price, amount })
    });

    if (!res.ok) {
      const err = await res.text();
      alert("Error creating order: " + err);
      return;
    }

    alert("Order created successfully!");
    getOrders(); // Refresh orders list after creation
  }
// === View Market Orders ===