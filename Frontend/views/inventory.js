import { api } from '../api.js';

export function renderInventory(container, navigate) {
  container.innerHTML = `<h2>My Inventory</h2><ul id="inventory-list"></ul>`;

  api('/myinventory')
    .then(items => {
      const list = document.getElementById('inventory-list');
      items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.entity.name} x ${item.quantity}`;
        list.appendChild(li);
      });

      container.innerHTML += `
        <h3>Charge Inventory</h3>
        <input id="inv-entity-id" placeholder="Entity ID">
        <input id="inv-amount" placeholder="Amount">
        <button id="charge-btn">Charge</button>
      `;

      document.getElementById('charge-btn').onclick = async () => {
        const entity_id = parseInt(document.getElementById('inv-entity-id').value);
        const amount = parseInt(document.getElementById('inv-amount').value);
        try {
          await api('/inventory-charge', 'POST', { entity_id, amount });
          alert('Inventory charged');
          navigate('inventory');
        } catch (err) {
          alert('Failed to charge inventory');
        }
      };
    })
    .catch(() => {
      container.innerHTML = 'Could not load inventory.';
    });
}
