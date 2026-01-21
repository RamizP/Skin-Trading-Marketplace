const BASE = 'https://192.168.1.236:8000';

export async function api(path, method = 'GET', body = null) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : null,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
