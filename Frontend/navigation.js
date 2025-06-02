export async function loadHeaderAndFooter() {
  document.getElementById('header').innerHTML = await (await fetch('header.html')).text();
  document.getElementById('footer').innerHTML = await (await fetch('footer.html')).text();
}

<script type="module">
  import { loadHeaderAndFooter } from './navigation.js';
  loadHeaderAndFooter();
</script>