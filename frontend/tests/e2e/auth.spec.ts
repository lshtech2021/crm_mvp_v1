import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

/**
 * Full-stack login/logout flows need the API (e.g. NEXT_PUBLIC_API_URL) and valid tenant users.
 * Set E2E_EMAIL and E2E_PASSWORD for local runs against a seeded backend.
 */
const hasBackendCreds =
  Boolean(process.env.E2E_EMAIL?.trim()) && Boolean(process.env.E2E_PASSWORD?.trim());

test.describe("Authentication", () => {
  test("can navigate to login page", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
  });

  test("login with valid credentials redirects to dashboard", async ({ page }) => {
    test.skip(
      !hasBackendCreds,
      "Requires E2E_EMAIL, E2E_PASSWORD, and running API — see tests/e2e/auth.spec.ts header.",
    );
    await page.goto("/login");
    await page.getByLabelText(/^email/i).fill(process.env.E2E_EMAIL!);
    await page.getByLabelText(/^password/i).fill(process.env.E2E_PASSWORD!);
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });
  });

  test("login with invalid credentials shows error", async ({ page }) => {
    test.skip(
      !hasBackendCreds,
      "Requires running API to return an auth error — use full stack or un-skip with a mock server.",
    );
    await page.goto("/login");
    await page.getByLabelText(/^email/i).fill("not-a-real-user@example.com");
    await page.getByLabelText(/^password/i).fill("wrong-password");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByRole("alert")).toBeVisible({ timeout: 10_000 });
  });

  test("unauthenticated visit to root redirects to login", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/\/login/);
  });

  test("accessing protected route without auth redirects to login", async ({ page }) => {
    test.skip(
      true,
      "Dashboard is not auth-guarded in the MVP — add middleware or a client guard to enable this assertion.",
    );
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("logout returns to login page", async ({ page }) => {
    test.skip(
      !hasBackendCreds,
      "Requires E2E_EMAIL, E2E_PASSWORD, and running API — full-stack only.",
    );
    await page.goto("/login");
    await page.getByLabelText(/^email/i).fill(process.env.E2E_EMAIL!);
    await page.getByLabelText(/^password/i).fill(process.env.E2E_PASSWORD!);
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });
    await page.getByRole("button", { name: /logout/i }).click();
    await expect(page).toHaveURL(/\/login/, { timeout: 15_000 });
  });

  test("login page passes axe accessibility checks", async ({ page }) => {
    await page.goto("/login");
    await injectAxe(page);
    await checkA11y(page);
  });
});
