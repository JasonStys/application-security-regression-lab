/** Jason Stys: real corrected DOM exercise on three browser engines and a mobile layout, no artifact/cache uploads. */
/* BEGIN CODE MAP (generated; npm run code-map)
END CODE MAP */
import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "tests/e2e",
  workers: 1,
  retries: 0,
  reporter: [["list"], ["json", { outputFile: "out/browser-results.json" }]],
  use: {
    baseURL: "http://127.0.0.1:53022",
    trace: "off",
    screenshot: "off",
    video: "off",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: "node services/node/server.mjs 53022",
    url: "http://127.0.0.1:53022/health",
    reuseExistingServer: false,
    timeout: 20000,
  },
});
