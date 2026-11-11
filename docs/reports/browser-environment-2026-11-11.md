# Complete browser environment correction

By Jason Stys. Actual current-guide job 130616724515 stopped during Ubuntu browser dependency installation after package DNS failed. The browser assertions had not started; cancellation/setup results are not application failures or passing browser evidence.

Only the browser job now uses the [official matching Playwright image](https://playwright.dev/docs/docker) `mcr.microsoft.com/playwright:v1.63.0-noble@sha256:eff16c30e6f3f4af0a03fa4b706120d5e9b0891c344a27d64559aff5900a4a27`, with user 1001 and its original job deadline. The installed package must match the unchanged lock graph. The complete vendor image supplies its intended Chromium, Firefox, WebKit and system dependencies; there is no ignored package-manager error or host-validation bypass.

The actual driver is resolved through `@playwright/test`, its own `playwright` dependency and then `playwright-core`. Its installed version must match both that declaration and the precise lock entry; an independent root-level copy is not mistaken for the driver. No dependency version or graph changes.

Before the unchanged full engine/mobile suite, each real browser must reject a genuinely absent executable, launch normally from the image, render/fill accented text, measure usable fonts, retain keyboard focus and fit 390/1400 viewport widths without horizontal overflow. The static probe blocks and counts outside requests; zero is required. All owned browser processes close in finally blocks. Original application assertions, independent expected outputs, retries/deadlines and all other source/native/security jobs remain mandatory.

Actual-workflow negative fixtures reject an unpinned/mismatched image, root identity, omitted engine/assertions or ignored host error. Local source/format/mutation checks do not execute a Linux container or prove those browser results. Fresh hosted actual browser acceptance remains required. No Docker command, image installation or system change was made on this PC; approved Office bytes, packaged runtime, normal profiles and published releases remain unchanged. The guide still refers to its declared historical installed source.
