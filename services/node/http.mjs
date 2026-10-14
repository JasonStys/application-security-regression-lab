/** Jason Stys: numeric-loopback corrected text demo, fixed assets/fixture, no arbitrary URLs or vulnerable modes. */
/* BEGIN CODE MAP (generated; npm run code-map)
 * definition: server — line 26
 * parameter: root — line 26
 * variable: instance — line 27
 * parameter: request — line 27
 * parameter: response — line 27
 * variable: origin — line 28
 * variable: headers — line 29
 * variable: hosts — line 38
 * parameter: _ — line 39
 * parameter: index — line 39
 * variable: origins — line 42
 * parameter: _ — line 43
 * parameter: index — line 43
 * variable: assets — line 63
 * variable: value — line 71
 * variable: [name, mime] — line 84
 * variable: bytes — line 85
END CODE MAP */
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

/** Create a finite-timeout, fixed-route synthetic server; upstream request strings never become HTML. */
export function server(root) {
  const instance = createServer(async (request, response) => {
    const origin = "http://127.0.0.1:" + instance.address().port;
    const headers = {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "X-Lab-Component": "node",
      "Referrer-Policy": "no-referrer",
      "Content-Security-Policy":
        "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
      "X-Frame-Options": "DENY",
    };
    const hosts = request.rawHeaders.filter(
      (_, index) =>
        index % 2 === 0 && request.rawHeaders[index].toLowerCase() === "host",
    );
    const origins = request.rawHeaders.filter(
      (_, index) =>
        index % 2 === 0 && request.rawHeaders[index].toLowerCase() === "origin",
    );
    if (
      hosts.length !== 1 ||
      request.headers.host !== "127.0.0.1:" + instance.address().port ||
      origins.length > 1 ||
      (request.headers.origin !== undefined &&
        request.headers.origin !== origin) ||
      request.headers["sec-fetch-site"] === "cross-site"
    ) {
      response.writeHead(403, headers);
      response.end();
      return;
    }
    if (request.method !== "GET") {
      response.writeHead(405, headers);
      response.end();
      return;
    }
    const assets = {
      "/": ["index.html", "text/html; charset=utf-8"],
      "/app.js": ["app.js", "text/javascript"],
      "/text.js": ["text.js", "text/javascript"],
      "/style.css": ["style.css", "text/css"],
    };
    try {
      if (request.url === "/health" || request.url === "/sample") {
        const value = {
          component: "node",
          synthetic: true,
          ...(request.url === "/sample"
            ? { label: "<img src=x onerror=alert(1)> · synthetic label" }
            : {}),
        };
        response.writeHead(200, {
          ...headers,
          "Content-Type": "application/json",
        });
        response.end(JSON.stringify(value));
      } else if (Object.hasOwn(assets, request.url ?? "")) {
        const [name, mime] = assets[request.url];
        const bytes = await readFile(join(root, name));
        response.writeHead(200, { ...headers, "Content-Type": mime });
        response.end(bytes);
      } else {
        response.writeHead(404, headers);
        response.end();
      }
    } catch {
      response.writeHead(500, headers);
      response.end();
    }
  });
  instance.requestTimeout = 5000;
  instance.headersTimeout = 5000;
  instance.keepAliveTimeout = 1000;
  instance.maxConnections = 16;
  return instance;
}
