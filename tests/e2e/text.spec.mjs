/** Jason Stys: corrected DOM browser execution, active-node absence, no remote traffic, keyboard and WCAG acceptance. */
/* BEGIN CODE MAP (generated; npm run code-map)
 * parameter: { page } — line 18
 * parameter: { page, } — line 24
 * variable: dialogs — line 27
 * parameter: dialog — line 28
 * variable: value — line 32
 * parameter: { page, } — line 52
 * variable: remote — line 55
 * parameter: request — line 56
 * variable: original — line 67
 * parameter: { page } — line 78
 * parameter: { page, } — line 95
END CODE MAP */
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#status")).toContainText(
    "Rendered as literal text",
  );
});
test("Hostile labels remain literal with no active nodes or dialogs", async ({
  page,
}) => {
  let dialogs = 0;
  page.on("dialog", async (dialog) => {
    dialogs++;
    await dialog.dismiss();
  });
  for (const value of [
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "</pre><script>alert(1)</script>",
    "javascript:alert(1)",
    "quotes \" & ' · ✓ 😀",
  ]) {
    await page.getByLabel("Untrusted label", { exact: true }).fill(value);
    await page
      .getByRole("button", { name: "Render as text", exact: true })
      .click();
    await expect(page.locator("#preview")).toHaveText(value);
    expect(
      await page
        .locator("#preview img, #preview svg, #preview script, #preview a")
        .count(),
    ).toBe(0);
  }
  expect(dialogs).toBe(0);
});
test("Local fixture and byte-limit error preserve previous text", async ({
  page,
}) => {
  const remote = [];
  page.on("request", (request) => {
    if (new URL(request.url()).origin !== new URL(page.url()).origin)
      remote.push(request.url());
  });
  await page
    .getByRole("button", { name: "Fetch local fixture", exact: true })
    .click();
  await expect(page.locator("#status")).toHaveText(
    "Fetched local fixture and rendered as literal text.",
  );
  await expect(page.locator("#preview")).toContainText("<img src=x");
  const original = await page.locator("#preview").textContent();
  await page
    .getByLabel("Untrusted label", { exact: true })
    .fill("é".repeat(2049));
  await page
    .getByRole("button", { name: "Render as text", exact: true })
    .click();
  await expect(page.locator("#status")).toContainText("4096 UTF8 bytes");
  await expect(page.locator("#preview")).toHaveText(original);
  expect(remote).toEqual([]);
});
test("Keyboard, mobile overflow and WCAG scan", async ({ page }) => {
  await page.locator("#render").focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#render")).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
});
test("Help discloses independent fixtures and no certification", async ({
  page,
}) => {
  await page
    .getByText("Help, test evidence and scope", { exact: true })
    .click();
  await expect(page.getByText(/independent focused fixtures/)).toBeVisible();
  await expect(
    page.getByText(/do not certify complete OWASP ASVS/),
  ).toBeVisible();
});
