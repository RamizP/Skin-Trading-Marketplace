import { api } from '../api.js';

export function renderEntities(container, navigate) {
  container.innerHTML = `<h2>Entities</h2><ul id="entity-list"></ul>`;

  api('/entities')
    .then(entities => {
      const list = document.getElementById('entity-list');
      entities.forEach(ent => {
        const item = document.createElement('li');
        item.textContent = `${ent.name} (ID: ${ent.id})`;
        list.appendChild(item);
      });

      // Optional admin-only entity creation
      container.innerHTML += `
        <h3>Create Entity</h3>
        <input id="new-entity-name" placeholder="Entity name" />
        <button id="create-entity-btn">Create</button>
      `;

      document.getElementById('create-entity-btn').onclick = async () => {
        const name = document.getElementById('new-entity-name').value;
        try {
          await api('/entities', 'POST', { name });
          alert('Entity created');
          navigate('entities'); // Reload view
        } catch (err) {
          alert('Entity creation failed (maybe not admin?)');
        }
      };
    })
    .catch(() => {
      container.innerHTML = 'Failed to load entities.';
    });
}
