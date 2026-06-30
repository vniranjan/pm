import { expect, test, type Page } from "@playwright/test";

const login = async (page: Page) => {
  let isAuthenticated = false;

  await page.route("**/api/auth/me", async (route) => {
    if (isAuthenticated) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ authenticated: true, username: "user" }),
      });
      return;
    }

    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });

  await page.route("**/api/auth/login", async (route) => {
    const payload = route.request().postDataJSON() as
      | { username?: string; password?: string }
      | undefined;

    if (payload?.username === "user" && payload?.password === "password") {
      isAuthenticated = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ authenticated: true, username: "user" }),
      });
      return;
    }

    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Invalid credentials" }),
    });
  });

  await page.route("**/api/auth/logout", async (route) => {
    isAuthenticated = false;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ authenticated: false }),
    });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: /sign in to kanban/i })).toBeVisible();
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
};

test("loads the kanban board", async ({ page }) => {
  await login(page);
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await login(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("logs out and returns to sign in", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: /log out/i }).click();
  await expect(page.getByRole("heading", { name: /sign in to kanban/i })).toBeVisible();
});
