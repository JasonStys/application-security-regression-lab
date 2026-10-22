# Application Security Regression Lab

[![Validate](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/ci.yml) [![CodeQL](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/codeql.yml)

Created by **Jason Stys** · [GitHub](https://github.com/JasonStys) · [Contact on LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

Four independent, functional, corrected native services demonstrate security boundaries and keep them under regression tests. This is an owner-local **synthetic educational lab**, not a public login system, vulnerability scanner, federated app, ASVS certification or production-ready deployment.

| Workbench | Working feature | Proof |
| --- | --- | --- |
| Java | Authoritative tenant/operation authorization, immutable notes, atomic expected revisions | native negative/race checks + actual HTTP read/write isolation |
| C# / ASP.NET Core | 256-bit random sessions, hash-only storage, monotonic expiry/revocation/capacity | native time-boundary tests + real cookies, peer scope and revocation |
| PHP / SQLite | Parameterized literal search, same-tenant access, bounded .txt data uploads | actual PDO queries/quota rollback + HTTP upload/download |
| JavaScript / TypeScript / HTML / CSS | Literal DOM rendering, strict response validation, CSP, no remote UI assets | native Node/typed tests + real browser XSS/keyboard/accessibility cases |
| Python / Bash | Owned-process orchestration, exact expected/observed evidence, inert HTML reports | strict negative/property/lifecycle tests, real loopback conformance |

Deliberately incorrect comparisons live only in tests, not HTTP modes. Regressions prove selected known defects are discriminated; this is not universal mutation coverage. Synthetic fixture IDs are **public exercise selectors, never real credentials**. C# bootstrap selects synthetic identities without passwords; it is not authentication of real people.

## Quick start: browser exercise

Node 24+, Python 3.12+:

    npm ci --ignore-scripts
    npm run build
    npm run serve

Open the printed numeric 127.0.0.1 URL. Try a hostile-looking label: the text is displayed literally; no tags/code execute and typed input stays in the tab. Ctrl+C stops. All attribution/help is in the UI. This page does not falsely claim that Java/C#/PHP services are interconnected.

## Run the complete lab

Prerequisites: Temurin JDK 25.0.4, .NET SDK 10.0.401, PHP 8.3+ with PDO SQLite, Node 24+ and Python 3.12+. GitHub's integration runner uses Node 24.21.0 and Ubuntu's maintained PHP/SQLite packages. No runtime third-party Maven/NuGet/Composer/npm libraries are required.

    python -m venv .venv
    .venv\Scripts\python -m pip install --require-hashes -r requirements-dev.lock
    npm ci --ignore-scripts
    npm run build
    bash scripts/native.sh

On Linux/macOS use .venv/bin/python and activate the venv before Bash. On PowerShell run the native script's commands individually (the [runbook](docs/runbook.md) explains). The script compiles actual Java/C# cores, checks PHP syntax/real PDO behavior, runs selected vulnerable comparisons and exercises **all four actual HTTP adapters**. Missing runtimes fail; no hidden skips.

Working evidence is ignored under out/native-http/http.json and http.html. A fresh result directory is mandatory, not silently overwritten. For explicit individual adapters after building: python -m asrl --component session --output out/new-session. All is the default; no external target/URL option exists. Only owned numeric-loopback processes are started and stopped in a finally block.

## Read and validate

[Architecture/ADR](docs/architecture.md), [contracts](docs/contracts.md), [threat model](docs/security.md), [runbook](docs/runbook.md), [testing](docs/testing.md), [research/control references](docs/research.md), [actual validation](docs/reports/validation.md), [contributing](CONTRIBUTING.md).

Authored code has descriptions and checked generated exact-line symbol maps. Python/TypeScript maps use ASTs; Java/C#/PHP/SQL/shell/YAML use documented lexical declaration maps. Native compilers/type/lint gates independently verify syntax. JSON/lock/config purposes are in the complete tracked-file inventory below.

Complexity: Java note lookups/updates expected O(1), bounded form parsing O(bytes); C# resolution expected O(1), bounded expiry reclamation O(sessions); PHP indexed upload lookup, bounded literal-search scan and quota aggregation; DOM validation/render O(text bytes); orchestration O(cases). Complexity analysis and observed request latencies are not universal worst-case or production performance promises.

## Safety scope

Owned trusted host, fictional tenants/records only. Loopback/session/Host/Origin/CSP guards do not protect against malicious OS users/admins or replace production identity/TLS. PHP's development server and the small JDK server are not public gateways. Stored uploads are SQLite text, not files executed or publicly served; downloads are plaintext attachments, not malware-certified.

No Docker repair, public hosting, real account collection, cloud resources, ads, analytics or secret upload. Do not enter sensitive data in these fixtures. Out/builds/reports/tokens stay ignored. [Security disclosure](SECURITY.md). All workflows avoid artifact uploads/Actions caches; logs/CodeQL results are separate storage.

## Complete file guide

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.gitattributes](.gitattributes) | Consistent LF checkouts across supported operating systems. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: actual native/HTTP/browser security regressions; no artifact uploads or Actions caches. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: security-extended analysis of all supported authored languages, including compiled native code. |
| [.gitignore](.gitignore) | Exclude runtime tokens, databases, builds, compilers and working reports. |
| [CHANGELOG.md](CHANGELOG.md) | Changelog. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributing. |
| [LICENSE](LICENSE) | MIT license for authored code; upstream tools retain their licenses. |
| [README.md](README.md) | Application Security Regression Lab. |
| [SECURITY.md](SECURITY.md) | Security disclosure. |
| [asrl/\_\_init\_\_.py](asrl/__init__.py) | Jason Stys: owned-loopback conformance and strict inert evidence reporting; no import-time I/O. |
| [asrl/\_\_main\_\_.py](asrl/__main__.py) | Jason Stys: explicit component/all conformance runner and new-directory inert reports; owned synthetic fixtures only. |
| [asrl/cases.py](asrl/cases.py) | Jason Stys: actual expected/observed application-boundary cases across four independent native adapters. |
| [asrl/evidence.py](asrl/evidence.py) | Jason Stys: validated expected/observed security evidence, honest verdicts and inert HTML summaries. |
| [asrl/transport.py](asrl/transport.py) | Jason Stys: explicit owned numeric-loopback request/process lifecycle, no external-target scan interface. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: independent native boundaries, not a fake production federation. |
| [docs/contracts.md](docs/contracts.md) | Native fixture and evidence contracts. |
| [docs/reports/ci.json](docs/reports/ci.json) | Immutable accepted-source Actions check snapshot, not a future guarantee. |
| [docs/reports/portfolio-sync-2026-10-22.md](docs/reports/portfolio-sync-2026-10-22.md) | <!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->. |
| [docs/reports/validation.md](docs/reports/validation.md) | Validation and acceptance record. |
| [docs/research.md](docs/research.md) | Primary sources and selected control references. |
| [docs/runbook.md](docs/runbook.md) | Local operations and reproducing results. |
| [docs/security.md](docs/security.md) | Threat model and review boundaries. |
| [docs/testing.md](docs/testing.md) | Test strategy and limitations. |
| [global.json](global.json) | Exact .NET SDK 10.0.401, no automatic version roll-forward. |
| [package-lock.json](package-lock.json) | Complete integrity-locked npm tool graph. |
| [package.json](package.json) | Exact browser tool graph and build/verification commands. |
| [playwright.config.mjs](playwright.config.mjs) | Jason Stys: real corrected DOM exercise on three browser engines and a mobile layout, no artifact/cache uploads. |
| [pyproject.toml](pyproject.toml) | Strict Python evidence/conformance lint/type/95% combined coverage gates. |
| [requirements-dev.in](requirements-dev.in) | Exact Python development tool inputs. |
| [requirements-dev.lock](requirements-dev.lock) | Complete portable hash-locked Python development graph. |
| [scripts/build.mjs](scripts/build.mjs) | Jason Stys: copy reviewed static assets after strict TypeScript compilation; private reports/state excluded. |
| [scripts/code\_map.py](scripts/code_map.py) | Jason Stys: generate exact definition/variable line maps and verify Python function/class contracts. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Jason Stys: exact tracked-file README purpose inventory; unknown files fail instead of receiving guessed descriptions. |
| [scripts/native.sh](scripts/native.sh) | Jason Stys: real native compilation/core comparisons and owned-loopback conformance; never skip a runtime. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/ts-map.mjs](scripts/ts-map.mjs) | Jason Stys: exact AST declaration/parameter maps for TypeScript/JavaScript and static HTML/CSS control maps. |
| [scripts/validate.sh](scripts/validate.sh) | Jason Stys: strict conformance/evidence core and complete maintained source/documentation gates. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Jason Stys: private-state/link/action-pin and test-only-vulnerable-comparison confinement checks. |
| [services/java/JavaService.java](services/java/JavaService.java) | Jason Stys: corrected tenant-policy HTTP fixture on numeric loopback; no vulnerable HTTP mode. |
| [services/java/Policy.java](services/java/Policy.java) | Jason Stys: authoritative tenant/operation policy, atomic revisions and bounded literal form parsing. |
| [services/node/http.mjs](services/node/http.mjs) | Jason Stys: numeric-loopback corrected text demo, fixed assets/fixture, no arbitrary URLs or vulnerable modes. |
| [services/node/server.mjs](services/node/server.mjs) | Jason Stys: launch the corrected synthetic browser fixture on numeric loopback only. |
| [services/php/Store.php](services/php/Store.php) | Jason Stys: native prepared SQLite queries, authoritative tenant scope and bounded nonexecuting text uploads. |
| [services/php/router.php](services/php/router.php) | Jason Stys: corrected synthetic-only PHP loopback routes, private SQLite path comes only from trusted environment. |
| [services/session/Broker.cs](services/session/Broker.cs) | Jason Stys: bounded random-token lifecycle with hashed storage, explicit expiry, revocation and fixture scope. |
| [services/session/Program.cs](services/session/Program.cs) | Jason Stys: synthetic-only loopback HTTP session fixture. Not a real identity provider or public login. |
| [services/session/SessionLab.csproj](services/session/SessionLab.csproj) | Jason Stys: ASP.NET Core session-lifecycle lab using platform-only APIs, strict compiler and nullable checks. |
| [services/session/packages.lock.json](services/session/packages.lock.json) | Locked framework-only server restore, no external NuGet packages. |
| [sql/schema.sql](sql/schema.sql) | Jason Stys: synthetic tenant-scoped SQLite records and bounded text uploads, never executable files. |
| [tests/e2e/text.spec.mjs](tests/e2e/text.spec.mjs) | Jason Stys: corrected DOM browser execution, active-node absence, no remote traffic, keyboard and WCAG acceptance. |
| [tests/java/PolicyTests.java](tests/java/PolicyTests.java) | Jason Stys: native tenant, operation, form/JSON and edit-race tests, plus nonserved insecure comparisons. |
| [tests/php/store\_test.php](tests/php/store_test.php) | Jason Stys: real in-memory PDO tests and deliberately incorrect test-only SQL/name predicates, never served. |
| [tests/session/Program.cs](tests/session/Program.cs) | Jason Stys: actual native session boundaries and nonserved deliberately incorrect comparison predicates. |
| [tests/session/SessionTests.csproj](tests/session/SessionTests.csproj) | Jason Stys: native self-contained session tests, no test framework or runtime packages. |
| [tests/session/packages.lock.json](tests/session/packages.lock.json) | Locked framework-only native test restore. |
| [tests/test\_evidence.py](tests/test_evidence.py) | Jason Stys: property and negative checks for truthful verdicts, strict reports and inert rendering. |
| [tests/test\_runner.py](tests/test_runner.py) | Jason Stys: case generation/negative verdicts, actual Node/.NET fixtures and CLI evidence persistence. |
| [tests/test\_transport.py](tests/test_transport.py) | Jason Stys: actual loopback sockets plus isolated lifecycle failure/timeout/no-external-target tests. |
| [tests/ui/text.test.mjs](tests/ui/text.test.mjs) | Jason Stys: native TypeScript text contracts and genuine Node transport, plus a nonserved unsafe comparison. |
| [tools.lock.json](tools.lock.json) | Official scanner version/URL/SHA256 pins. |
| [tsconfig.json](tsconfig.json) | Strict browser compilation with unchecked-index/nullable safeguards. |
| [web/app.ts](web/app.ts) | Jason Stys: accessible browser encoding exercise. Java/C#/PHP are independent native fixture services. |
| [web/index.html](web/index.html) | Responsive semantic local-only browser encoding exercise and scope/help. |
| [web/style.css](web/style.css) | Jason Stys: restrained, accessible operational-learning layout with responsive cards and visible keyboard focus. |
| [web/text.ts](web/text.ts) | Jason Stys: validate bounded Unicode and render it as text, never markup, attributes, URLs or code. |

<!-- END FILE GUIDE -->
