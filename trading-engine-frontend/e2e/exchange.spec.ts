import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

test.beforeEach(async ({ request }) => {
  const reset = await request.post("/api/__test/reset");
  expect(reset.ok()).toBe(true);
});

test("free case claims refresh inventory, persist the countdown, and respect the server cooldown", async ({
  page,
}) => {
  await page.goto("/#cases");
  const offer = page.getByRole("region", { name: "Free case", exact: true });
  await offer
    .getByRole("button", { name: "Sign in to claim a free case", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByRole("button", { name: "Close dialog", exact: true }).click();
  await register(page);
  const claim = offer.getByRole("button", {
    name: "Claim free case",
    exact: true,
  });
  const firstResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/cases/free") &&
      response.request().method() === "POST",
  );
  await claim.click();
  expect((await firstResponse).status()).toBe(200);
  await expect(offer.getByRole("status")).toContainText(
    "Added After Hours Case to your inventory.",
  );
  await expect(claim).toBeDisabled();
  await expect(claim).toContainText(/Available in \d{2}:\d{2}/);
  await page.reload();
  await expect(claim).toBeDisabled();

  // Remove only the UI's timer hint. The API must still reject a repeat claim.
  await page.evaluate(() => {
    for (const key of Object.keys(sessionStorage)) {
      if (key.startsWith("exchange.free-case:")) sessionStorage.removeItem(key);
    }
  });
  await page.reload();
  await expect(claim).toBeEnabled();
  const secondResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/cases/free") &&
      response.request().method() === "POST",
  );
  await claim.click();
  const denied = await secondResponse;
  expect(denied.status()).toBe(400);
  expect((await denied.json()).detail.remaining_seconds).toBeGreaterThan(0);
  await expect(claim).toBeDisabled();
  await expect(offer.getByRole("alert")).toHaveCount(0);
  await offer
    .getByRole("button", { name: "View inventory", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Manage After Hours Case", exact: true }),
  ).toHaveCount(1);
});

test("failed free-case claims show the API error without starting a countdown", async ({
  page,
}) => {
  await page.goto("/#cases");
  await register(page);
  await page.route("**/api/cases/free", (route) =>
    route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: "No cases available" }),
    }),
  );
  const offer = page.getByRole("region", { name: "Free case", exact: true });
  const claim = offer.getByRole("button", {
    name: "Claim free case",
    exact: true,
  });
  await claim.click();
  await expect(offer.getByRole("alert")).toContainText("No cases available");
  await expect(claim).toBeEnabled();
  await page.unroute("**/api/cases/free");
  await claim.click();
  await expect(offer.getByRole("status")).toContainText(
    "Added After Hours Case to your inventory.",
  );
  await expect(offer.getByRole("alert")).toHaveCount(0);
  await expect(claim).toBeDisabled();
});

async function register(page: Page) {
  await page.getByRole("button", { name: "Get started" }).click();
  const dialog = page.getByRole("dialog");
  const id = `trader_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
  await dialog.getByLabel("Username", { exact: true }).fill(id);
  await dialog.getByLabel("Email", { exact: true }).fill(`${id}@example.com`);
  await dialog
    .getByLabel("Password", { exact: true })
    .fill("PlayerPassword123!");
  await dialog.getByLabel("Confirm password").fill("PlayerPassword123!");
  await dialog
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(dialog).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Add test funds", exact: true }),
  ).toBeVisible();
}

test("public catalog supports search, categories, item details, and mobile layout", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Your next upgrade/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Inspect Asiimov", exact: true }),
  ).toBeVisible();
  await page.getByRole("textbox", { name: "Search items" }).fill("Dragon");
  await expect(page.locator(".item-card")).toHaveCount(1);
  await page
    .getByRole("button", { name: "Inspect Dragon Lore", exact: true })
    .click();
  await expect(
    page
      .getByRole("dialog")
      .getByRole("heading", { name: "Dragon Lore", exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("textbox", { name: "Search items" }).clear();
  await page
    .getByRole("group", { name: "Item categories" })
    .getByRole("button", { name: "Pistol", exact: true })
    .click();
  await expect(page.locator(".item-card")).toHaveCount(2);
  await page
    .getByRole("group", { name: "Item categories" })
    .getByRole("button", { name: "All items", exact: true })
    .click();
  await expect(page.locator(".item-card")).toHaveCount(7);
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "Cases", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "The case collection" }),
  ).toBeVisible();
  await expect(page.locator(".item-card")).toHaveCount(1);
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "Marketplace", exact: true })
    .click();
  await expect(page.locator(".item-card")).toHaveCount(7);
  await page
    .getByRole("textbox", { name: "Search items" })
    .fill("does not exist");
  await expect(
    page.getByRole("heading", { name: "Nothing here. Yet." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await expect(page.locator(".item-card")).toHaveCount(7);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.locator("img").evaluateAll(async (images) => {
    await Promise.all(
      images.map(async (image) => {
        image.loading = "eager";
        await image.decode().catch(() => undefined);
      }),
    );
  });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.mouse.move(0, 0);
  await page.screenshot({
    path: info.outputPath("marketplace.png"),
    fullPage: true,
  });
  expect(errors).toEqual([]);
});

test("registration, wallet, listing, cancellation, purchase, and case opening use the API", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await register(page);

  await page
    .getByRole("button", { name: "Add test funds", exact: true })
    .click();
  await page.getByLabel("Amount (test USD)").fill("50.25");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Add test funds", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Add test funds", exact: true }),
  ).toContainText("$50.25");
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Add test funds", exact: true }),
  ).toContainText("$50.25");

  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "My inventory" })
    .click();
  await expect(
    page.getByRole("heading", { name: "A collection waiting to happen." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Get a test item" }).click();
  await page
    .getByLabel("Collectible", { exact: true })
    .selectOption({ label: "M4A4 · Asiimov" });
  await page
    .getByRole("button", { name: "Add to inventory", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page
    .getByRole("button", { name: "Manage Asiimov", exact: true })
    .click();
  await page.getByRole("spinbutton", { name: "Order price" }).fill("200.00");
  await page
    .getByRole("button", { name: "List for sale", exact: true })
    .click();
  await expect(
    page.getByRole("dialog").getByText("Listing submitted.", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "My orders" })
    .click();
  await expect(page.locator(".order-row")).toHaveCount(1);
  await page
    .getByRole("button", { name: "Cancel listing", exact: true })
    .click();
  await page.getByRole("button", { name: "Confirm", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "A clean slate." }),
  ).toBeVisible();

  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "Marketplace", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Inspect Asiimov", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Buy item", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirm purchase", exact: true })
    .click();
  await expect(
    page.getByRole("dialog").getByText("Purchase complete.", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await expect(
    page.getByRole("button", { name: "Add test funds", exact: true }),
  ).toContainText("$39.75");

  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "My inventory" })
    .click();
  await expect(
    page.getByRole("button", { name: "Manage Asiimov", exact: true }),
  ).toHaveCount(2);
  await page.getByRole("button", { name: "Get a test item" }).click();
  await page
    .getByLabel("Collectible", { exact: true })
    .selectOption({ label: "AFTER HOURS · After Hours Case" });
  await page
    .getByRole("button", { name: "Add to inventory", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Manage After Hours Case", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Inside this case" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Open one case", exact: true })
    .click();
  await expect(
    page
      .locator(".reward-reveal")
      .getByRole("heading", { name: "Printstream" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await expect(
    page.getByRole("button", { name: "Manage After Hours Case", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Manage Printstream", exact: true }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("login reports incorrect credentials and restores a valid session", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Username", { exact: true }).fill("demo_trader");
  await dialog.getByLabel("Password", { exact: true }).fill("wrong-password");
  await dialog.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(dialog.getByRole("alert")).toBeVisible();
  await dialog.getByLabel("Password", { exact: true }).fill("DemoTrader123!");
  await dialog.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(dialog).toHaveCount(0);
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Add test funds", exact: true }),
  ).toContainText("$25.00");
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("button", { name: "Get started" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("button", { name: "Get started" })).toBeEnabled();
});

test("API failures display a recovery path and anonymous inventory asks for login", async ({
  page,
}) => {
  await page.route("**/api/orders", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Exchange temporarily unavailable" }),
    }),
  );
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText(
    "Exchange temporarily unavailable",
  );
  await page.unroute("**/api/orders");
  await page.getByRole("button", { name: "Try again", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Inspect Dragon Lore", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "My inventory" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Your collection starts here." }),
  ).toBeVisible();
});

test("buy orders recover from server validation and can be cancelled", async ({
  page,
}) => {
  await page.goto("/");
  await register(page);
  await page
    .getByRole("button", { name: "Inspect Asiimov", exact: true })
    .click();
  await page.getByRole("spinbutton", { name: "Order price" }).fill("1.00");
  await page.route("**/api/orders", (route) => {
    if (route.request().method() !== "POST") return route.continue();
    return route.fulfill({
      status: 422,
      contentType: "application/json",
      body: JSON.stringify({
        detail: [
          { loc: ["body", "price"], msg: "Simulated price validation error" },
        ],
      }),
    });
  });
  await page
    .getByRole("button", { name: "Place buy order", exact: true })
    .click();
  await expect(page.getByRole("dialog").getByRole("alert")).toContainText(
    "price: Simulated price validation error",
  );
  await page.unroute("**/api/orders");
  await page
    .getByRole("button", { name: "Place buy order", exact: true })
    .click();
  await expect(
    page
      .getByRole("dialog")
      .getByText("Buy order submitted.", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "My orders" })
    .click();
  await expect(page.locator(".order-row")).toHaveCount(1);
  await expect(page.locator(".order-row")).toContainText("$1.00");
  await expect(page.locator(".order-row")).toContainText("Buy order");
  await page
    .getByRole("button", { name: "Cancel buy order", exact: true })
    .click();
  await page.getByRole("button", { name: "Confirm", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "A clean slate." }),
  ).toBeVisible();
});

test("buy orders can be cancelled from item details and failed cancellation preserves them", async ({
  page,
}) => {
  await page.goto("/");
  await register(page);
  await page
    .getByRole("button", { name: "Inspect Asiimov", exact: true })
    .click();
  await page.getByRole("spinbutton", { name: "Order price" }).fill("1.00");
  await page
    .getByRole("button", { name: "Place buy order", exact: true })
    .click();

  const bids = page.getByRole("region", {
    name: "Your buy orders",
    exact: true,
  });
  await expect(bids.locator(".item-bid-row")).toHaveCount(1);
  await expect(bids).toContainText("$1.00");
  await bids
    .getByRole("button", { name: "Cancel buy order", exact: true })
    .click();
  await bids
    .getByRole("button", { name: "Keep buy order", exact: true })
    .click();
  await expect(
    bids.getByRole("button", { name: "Cancel buy order", exact: true }),
  ).toBeVisible();

  await page.route("**/api/order", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Cancellation temporarily unavailable" }),
    }),
  );
  await bids
    .getByRole("button", { name: "Cancel buy order", exact: true })
    .click();
  await bids
    .getByRole("button", { name: "Confirm cancellation", exact: true })
    .click();
  await expect(page.getByRole("dialog").getByRole("alert")).toContainText(
    "Cancellation temporarily unavailable",
  );
  await expect(bids.locator(".item-bid-row")).toHaveCount(1);

  await page.unroute("**/api/order");
  await bids
    .getByRole("button", { name: "Confirm cancellation", exact: true })
    .click();
  await expect(
    bids.getByText("No open buy orders for this item.", { exact: true }),
  ).toBeVisible();
  await expect(bids.locator(".item-bid-row")).toHaveCount(0);
  await expect(page.getByRole("dialog").getByRole("alert")).toHaveCount(0);
  await page.getByRole("button", { name: "Close dialog" }).click();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "My orders" })
    .click();
  await expect(
    page.getByRole("heading", { name: "A clean slate." }),
  ).toBeVisible();
});
