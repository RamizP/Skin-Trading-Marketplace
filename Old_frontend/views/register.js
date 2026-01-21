import { api } from '../api.js';

export function renderRegister(container, navigate) {
  container.innerHTML = `
    <h2>Register</h2>
    <input id="user" placeholder="Username">
    <input id="pass" type="password" placeholder="Password">
    <button id="reg-btn">Register</button>
    <p>Already have an account? <a href="#login">Login</a></p>
  `;

  document.getElementById('reg-btn').onclick = async () => {
    const username = document.getElementById('user').value;
    const password = document.getElementById('pass').value;
    try {
      await api('/register', 'POST', { username, password });
      alert('Registered! Now login.');
      navigate('login');
    } catch (err) {
      alert('Register failed');
    }
  };
}
