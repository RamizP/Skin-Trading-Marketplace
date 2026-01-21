import { api } from '../api.js';

export function renderOrders(container, navigate) {
  container.innerHTML = `
    <h2>My Orders</h2>
    <ul id="order-list"></ul>
    <h3>Create Order</h3>
    <input id="order-entity-id" placeholder="Entity ID">
    <input id="order-amount" placeholder="Amount">
    <input id="order-price" placeholder="Price">
    <button id="order-btn">Create Order</button>

    <h3>Market Orders</h3>
    <input id="market-entity-id" placeholder="Entity ID to View Market">
    <button id="market-btn">View Orders</button>
    <ul id="market-list"></ul>
  `;

  // Fetch user orders
  api('/orders')
    .then(orders => {
      const list = document.getElementById('order-list');
      orders.forEach(order => {
        const li = document.createElement('li');
        li.textContent = `Entity ${order.entity.name}: ${order.amount} @ ${order.price}`;
        list.appendChild(li);
      });
    })
    .catch(() => {
      container.innerHTML += '<p>Could not load your orders.</p>';
    });

  // Create new order
  document.getElementById('order-btn').onclick = async () => {

    const entity_id = parseInt(document.getElementById('order-entity-id').value);
    const amount = parseInt(document.getElementById('order-amount').value);
    const price = parseFloat(document.getElementById('order-price').value);

    try {
      await api('/orders', 'POST', { entity_id, amount, price });
      alert('Order created');
      navigate('orders');
    } catch {
      alert('Failed to create order');
    }
  };

  // View market orders for an entity
  document.getElementById('market-btn').onclick = async () => {
    const entity_id = document.getElementById('market-entity-id').value;
    try {
      const orders = await api(`/orders/${entity_id}`);
      const list = document.getElementById('market-list');
      list.innerHTML = '';
      orders.forEach(order => {
        const li = document.createElement('li');
        li.innerHTML = `Buy <strong>${order.amount}</strong> of <em>${order.entity.name}</em> @ <strong>${order.price}</strong>
          <button data-id="${order.id}" class="buy-btn">Buy</button>`;
        list.appendChild(li);
      });

      document.querySelectorAll('.buy-btn').forEach(btn => {
        btn.onclick = async () => {
          const id = parseInt(btn.getAttribute('data-id'));
          try {
            await api('/order-buy', 'POST', { order_id: id });
            alert('Order bought!');
            navigate('orders');
          } catch {
            alert('Buy failed');
          }
        };
      });
    } catch {
      alert('Failed to fetch market orders');
    }
  };
}
