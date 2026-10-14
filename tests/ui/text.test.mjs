/** Jason Stys: native TypeScript text contracts and genuine Node transport, plus a nonserved unsafe comparison. */
/* BEGIN CODE MAP (generated; npm run code-map)
 * definition: wire — line 38
 * parameter: origin — line 38
 * parameter: headers — line 38
 * parameter: resolve — line 39
 * parameter: reject — line 39
 * variable: connection — line 40
 * parameter: response — line 43
 * variable: value — line 53
 * variable: target — line 63
 * parameter: _ — line 65
 * variable: value — line 73
 * variable: target — line 89
 * variable: value — line 98
 * variable: input — line 110
 * variable: unsafeMarkup — line 111
 * variable: target — line 112
 * variable: instance — line 118
 * parameter: resolve — line 121
 * variable: origin — line 122
 * variable: path — line 124
 * variable: response — line 132
 * variable: headers — line 141
 * parameter: resolve — line 153
 * variable: missing — line 155
 * parameter: resolve — line 156
 * parameter: resolve — line 163
END CODE MAP */
import test from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { label, renderText, sample } from "../../dist/text.js";
import { server } from "../../services/node/http.mjs";
import { request as nativeRequest } from "node:http";

/** Send precise headers using the native client; Fetch may rewrite forbidden Host/fetch-metadata headers. */
async function wire(origin, headers) {
  return await new Promise((resolve, reject) => {
    const connection = nativeRequest(
      origin + "/health",
      { headers },
      (response) => {
        response.resume();
        response.on("end", () => resolve(response.statusCode));
      },
    );
    connection.on("error", reject);
    connection.end();
  });
}

for (const value of [
  "<img src=x onerror=alert(1)>",
  "<script>alert(1)</script>",
  "javascript:alert(1)",
  "✓ 😀",
  "",
  "&<>\"'",
]) {
  test("Literal text " + value.slice(0, 12), () => {
    assert.equal(label(value), value);
    const target = {
      textContent: "previous",
      set innerHTML(_) {
        throw new Error("unsafe sink");
      },
    };
    renderText(target, value);
    assert.equal(target.textContent, value);
  });
}
for (const value of [
  null,
  [],
  {},
  true,
  1,
  "\ud800",
  "\udfff",
  "x".repeat(4097),
  "é".repeat(2049),
]) {
  test("Reject invalid text " + String(value).slice(0, 8), () =>
    assert.throws(() => label(value)),
  );
}
test("Validation precedes mutation", () => {
  const target = { textContent: "preserved" };
  assert.throws(() => renderText(target, {}));
  assert.equal(target.textContent, "preserved");
});
test("Runtime sample schema", () => {
  assert.equal(
    sample({ component: "node", synthetic: true, label: "<img>" }),
    "<img>",
  );
  for (const value of [
    null,
    [],
    {},
    { component: "java", synthetic: true, label: "x" },
    { component: "node", synthetic: false, label: "x" },
    { component: "node", synthetic: true, label: 3 },
    { component: "node", synthetic: true, label: "x", extra: 1 },
  ])
    assert.throws(() => sample(value));
});
test("Nonserved unsafe comparison distinguishes executable markup from literal sink", () => {
  const input = "<img src=x onerror=alert(1)>";
  const unsafeMarkup = "<p>" + input + "</p>";
  const target = { textContent: "" };
  renderText(target, input);
  assert.ok(unsafeMarkup.includes("<p><img"));
  assert.equal(target.textContent, input);
});
test("Actual Node transport guards, fixed assets and private failures", async () => {
  const instance = server(
    fileURLToPath(new URL("../../dist", import.meta.url)),
  );
  await new Promise((resolve) => instance.listen(0, "127.0.0.1", resolve));
  const origin = "http://127.0.0.1:" + instance.address().port;
  try {
    for (const path of [
      "/",
      "/app.js",
      "/text.js",
      "/style.css",
      "/health",
      "/sample",
    ]) {
      const response = await fetch(origin + path);
      assert.equal(response.status, 200);
      assert.equal(response.headers.get("cache-control"), "no-store");
      assert.ok(
        response.headers
          .get("content-security-policy")
          .includes("default-src 'none'"),
      );
    }
    for (const headers of [
      { Host: "evil.invalid" },
      { Origin: "http://evil.invalid" },
      { "Sec-Fetch-Site": "cross-site" },
    ])
      assert.equal(await wire(origin, headers), 403);
    assert.equal(
      (await fetch(origin + "/sample", { method: "POST", body: "{}" })).status,
      405,
    );
    assert.equal((await fetch(origin + "/.env")).status, 404);
  } finally {
    await new Promise((resolve) => instance.close(resolve));
  }
  const missing = server("/does-not-exist");
  await new Promise((resolve) => missing.listen(0, "127.0.0.1", resolve));
  try {
    assert.equal(
      (await fetch("http://127.0.0.1:" + missing.address().port + "/")).status,
      500,
    );
  } finally {
    await new Promise((resolve) => missing.close(resolve));
  }
});
