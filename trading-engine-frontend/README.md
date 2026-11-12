# Trading Engine — The Player’s Exchange

A responsive React / TypeScript interface for this repository’s FastAPI trading engine. Browse collectibles, manage an inventory, place and cancel orders, buy listings, and open cases using the real API.

## Run locally

From the repository root, with the Python dependencies and `src/.env` configured:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --app-dir src/v1 --reload
```

In a second terminal:

```powershell
cd trading-engine-frontend
npm ci
npm run dev
```

Open the Local URL printed by Vite (normally `http://localhost:5173`). Vite forwards `/api` to `http://127.0.0.1:8000`, so a local HTTPS certificate is unnecessary. Database creation and updates are managed by the backend’s Alembic migrations.

The backend uses `src/v1/demo.db` by default. On the first startup of an empty database, it adds demo accounts, catalog items, inventories, orders, and case rewards. See the [demo logins](../README.md#try-the-demo) to try it. This data lives in the database and can be traded through the API; restarting does not reset it. Existing databases are left alone. Set `DEMO_DATA=false` in `src/.env` before first startup to keep a new database empty.

Administrators can add catalog items; categories must already exist in the API. Existing item image URLs are used, with an SVG fallback when an image is missing or cannot load.

## Features

- Public marketplace with search (`/` keyboard shortcut), categories, rarity, availability, and sorting.
- Registration, sign-in, session restoration, expiry handling, and sign-out.
- Inventory with listing state, condition, and case filters.
- Item details with sell listings, highest bid, buy-order and sell-order forms.
- Purchase confirmation, insufficient-balance feedback, and cancellation confirmation.
- My orders collects the signed-in user’s open buy orders and sell listings through the existing per-entity API endpoints, with at most four entities fetched concurrently.
- Cancel buy orders from My orders or the Your buy orders section in item details. Both require confirmation and preserve the order in the interface if the API rejects cancellation.
- Case contents and chances calculated from drop weights; opening consumes an owned case and reveals the API's reward through a scrolling item reel. The reel slows to the winning item, supports "Reveal now", and reveals immediately with reduced motion enabled.
- Claim a random free case from the Cases page every 15 minutes using `POST /cases/free`. Successful claims refresh the inventory. The countdown survives reloads in the same tab and resynchronizes with the API's `remaining_seconds` on cooldown rejection; eligibility is always enforced by the server.
- Explicitly labeled sandbox tools for adding test funds and inventory items. No real payments.
- Decimal amounts stay as strings when submitted to the API.
- Native modal dialogs, keyboard focus handling, reduced-motion support, and mobile navigation.

## API configuration

The default is `/api`. For a separately hosted backend, copy `.env.example` to `.env` and set:

```dotenv
VITE_API_URL=https://your-api.example.com
```

Restart Vite after changing environment variables. The backend must allow your frontend origin in its CORS configuration. `VITE_*` variables are public build configuration: never put secrets in them. A deployed frontend using `/api` needs its web server to forward that path to FastAPI; the Vite development proxy is not included in the static build.

Login uses the API’s returned JWT in the `Authentication` header. The token is stored in `sessionStorage`, survives reloads, and is cleared on sign-out or an authenticated `401` response. Sessions are scoped to the browser tab. Cookies remain enabled for compatibility with the backend.

## Checks

```powershell
npm run lint
npm run build
npm run format
```

## Browser tests

Install Chromium once:

```powershell
npx playwright install chromium
```

Then run:

```powershell
npm run test:e2e
```

Playwright starts a separate FastAPI server on port `8765` and Vite on `5174`. The API uses a seeded database in a temporary directory and resets it between tests. It does not use or modify the application's database. Its reset endpoint exists only in `e2e/serve_api.py`, never in the normal app.

The tests exercise desktop and mobile layouts, public browsing, registration, login, session restoration, wallet updates, listing/cancellation, buying, case opening, and error recovery. Screenshots and failure traces go to ignored `test-results/`.

The browser-test server uses the repository’s `venv` by default. If Python is elsewhere, set `PYTHON` to the executable path before running the tests. Keep ports `8765` and `5174` free; the tests deliberately do not reuse an existing server.
