# Native fixture and evidence contracts

Author: Jason Stys. All services hardcode numeric-loopback binding and expose component/synthetic identity on GET /health. Exact Host and incompatible Origin/fetch-site reject. No CORS; responses no-store/nosniff/CSP. Native HTTP stacks can reject malformed framing before application headers; tests do not claim equivalent public-gateway protocol hardening.

## Java

GET /record?id=alpha-note with Authorization: Bearer fixture-alpha-owner (or alpha-viewer/beta-owner). These are closed **synthetic selectors**, not secret credentials. Same-tenant read; unknown/cross tenant both 404. POST /record: URL-encoded exact id/version/body, same-origin, X-Lab-Exercise: synthetic and exact content type. Owner only, expected revision, atomic synchronized update. Errors do not mutate. 4,096 body bytes; up to eight form fields before exact schema checks; strict UTF8 decode once/duplicate rejection; body 1–1,000 characters without controls; revision at most 1,000. Pool four handlers/16 queued/backlog16; no certified absolute per-request deadline.

## C#

POST /session with exact JSON principal alpha-owner/alpha-viewer/beta-owner, Origin and X-Lab-Exercise: synthetic. Unknown/extra/duplicate properties reject. Password-free synthetic bootstrap, not real login. Fresh random 32-byte token in Secure/HttpOnly/SameSite Strict cookie; server stores SHA256 fingerprint and authoritative tenant/role. GET /whoami resolves only live sessions; POST /logout revokes only presented cookie. Inclusive monotonic expiry 120s; expired/backward-clock observations fail closed; capacity100. Browser cookie expiry does not replace server expiry. 2,048 body bytes, depth8, 16 connections, Kestrel header/keepalive5s. This fixture uses loopback HTTP, not TLS: the owned native test client explicitly echoes cookie values to exercise lifecycle and checks the Secure attribute. It does not claim browser cookie acceptance on insecure transport. A browser session integration requires trusted HTTPS; never remove Secure to accommodate HTTP. Tokens remain transient, never reports/logs/Git.

## PHP

Same closed fixture selectors as Java. GET /search?q=... uses authoritative tenant and PDO placeholders, escapes LIKE wildcards as literal data. Maximum100 query bytes, ten rows. POST /upload: exact filename/content URL-encoded fields, authorized owner, same-origin/exercise header. ASCII portable name ending .txt, no paths/double extensions/device names; UTF8 content 1–4,096 bytes, controls except tab/newline/CR rejected. Stored as SQLite text with opaque random ID—not executable disk files. Atomic quota8 items/16,384 bytes per tenant. GET /download?id=... returns same-tenant content as text/plain attachment with validated filename; missing/cross both404. No archives/rich media/malware scans. Trusted environment alone selects DB path. Request16,384 bytes, form8-field cap/strict decoding/duplicates; SQLite busy timeout3s; development HTTP server single-process, not public-hardened.

## Node/browser

Fixed GET /, app.js, text.js, style.css, /sample, /health only. Queries/path variants reject; no mutations. Node request/header timeout5s, keepalive1s, 16 connections. Fixture JSON component/synthetic/label is runtime-checked. Browser validates at most4,096 UTF8 bytes, rejects isolated surrogates, renders textContent only, does not build links/attributes/HTML from labels. Invalid input leaves earlier preview intact. Stale fetch responses do not overwrite newer input. CSP/self assets/no remote UI requests.

## Evidence and process lifecycle

Runner only takes component/all and new local result-directory options. No arbitrary executable, shell command or external target. Port allocation has a short release-to-bind race mitigated by owned-process readiness/component handshake; malicious host processes are outside the trust model. HTTP client5s/32 KiB response cap; readiness15s; terminate then5s grace/kill, no process-name enumeration.

Exact report schema1: source 40hex or uncommitted, note at most1,000 characters, 1–500 uniquely identified cases. Each has closed component, expected/observed integer HTTP codes100–599, boolean content_ok, finite latency0–60,000ms. Pass only status equality AND content invariant. Strict validated escaped HTML, no JavaScript/external assets. SHA256 is integrity, not signature/certification. New output directory/linked-parent rejection; no overwrite or automatic pruning.
