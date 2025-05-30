import { api } from '../api.js';

export function renderLogin(container, navigate) {
  container.innerHTML = `
    <h2>Login</h2>
    <input id="user" placeholder="Username">
    <input id="pass" type="password" placeholder="Password">
    <button id="login-btn">Login</button>
    <p>No account? <a href="#register">Register</a></p>
  `;

  document.getElementById('login-btn').onclick = async () => {
    const username = document.getElementById('user').value;
    const password = document.getElementById('pass').value;
    try {
      await api('/login', 'POST', { username, password });
      navigate('dashboard');
    } catch (err) {
      alert('Login failed');
    }
  };
}
