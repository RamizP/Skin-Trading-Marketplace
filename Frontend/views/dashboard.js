import { api } from '../api.js';

export function renderDashboard(container, navigate) {
  container.innerHTML = `<h2>Loading...</h2>`;

  api('/me').then(user => {
    container.innerHTML = `
      <h2>Welcome, ${user.username}</h2>
      <p>Balance: ${user.balance}</p>
      <input id="charge-amount" type="number" placeholder="Charge amount">
      <button id="charge-btn">Charge</button>
      <button id="logout-btn">Logout</button>
    `;

    document.getElementById('logout-btn').onclick = async () => {
      await api('/logout', 'POST');
      navigate('login');
    };

    document.getElementById('charge-btn').onclick = async () => {
      const amount = parseFloat(document.getElementById('charge-amount').value);
      await api('/balance-charge', 'POST', { amount });
      alert('Balance updated.');
      navigate('dashboard');
    };
  }).catch(() => {
    alert('Not logged in');
    navigate('login');
  });
}
