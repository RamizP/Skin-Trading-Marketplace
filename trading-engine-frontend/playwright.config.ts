import { defineConfig, devices } from "@playwright/test";
import { resolve } from "node:path";

const python =
  process.env.PYTHON ||
  resolve(
    "..",
    "venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
  );

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:5174",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "desktop",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 1080 },
      },
    },
    {
      name: "mobile",
      use: { ...devices["Pixel 7"], defaultBrowserType: "chromium" },
    },
  ],
  webServer: [
    {
      command: `"${python}" e2e/serve_api.py`,
      url: "http://127.0.0.1:8765/entities",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5174 --strictPort",
      url: "http://127.0.0.1:5174",
      env: { API_PROXY_TARGET: "http://127.0.0.1:8765", VITE_API_URL: "/api" },
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
