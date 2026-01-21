import { renderLogin } from './views/login.js';
import { renderRegister } from './views/register.js';
import { renderDashboard } from './views/dashboard.js';
import { renderEntities } from './views/entities.js';
import { renderInventory } from './views/inventory.js';
import { renderOrders } from './views/orders.js';

const routes = {
  login: renderLogin,
  register: renderRegister,
  dashboard: renderDashboard,
  entities: renderEntities,
  inventory: renderInventory,
  orders: renderOrders,
};

function navigate(route) {
  window.history.pushState({}, '', `#${route}`);
  render(route);
}

function render(route) {
  const app = document.getElementById('app');
  app.innerHTML = '';
  const view = routes[route] || renderLogin;
  view(app, navigate);
}

window.addEventListener('popstate', () => {
  const route = window.location.hash.slice(1);
  render(route);
});

document.addEventListener('DOMContentLoaded', () => {
  const route = window.location.hash.slice(1);
  render(route);
});
