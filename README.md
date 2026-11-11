# Application Security Regression Lab

[![Validate](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/ci.yml) [![CodeQL](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/application-security-regression-lab/actions/workflows/codeql.yml)

Created by **Jason Stys** · [GitHub](https://github.com/JasonStys) · [Contact on LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

Four independent, functional, corrected native services demonstrate security boundaries and keep them under regression tests. This is an owner-local **synthetic educational lab**, not a public login system, vulnerability scanner, federated app, ASVS certification or production-ready deployment.

| Workbench                            | Working feature                                                                          | Proof                                                                   |
| ------------------------------------ | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Java                                 | Authoritative tenant/operation authorization, immutable notes, atomic expected revisions | native negative/race checks + actual HTTP read/write isolation          |
| C# / ASP.NET Core                    | 256-bit random sessions, hash-only storage, monotonic expiry/revocation/capacity         | native time-boundary tests + real cookies, peer scope and revocation    |
| PHP / SQLite                         | Parameterized literal search, same-tenant access, bounded .txt data uploads              | actual PDO queries/quota rollback + HTTP upload/download                |
| JavaScript / TypeScript / HTML / CSS | Literal DOM rendering, strict response validation, CSP, no remote UI assets              | native Node/typed tests + real browser XSS/keyboard/accessibility cases |
| Python / Bash                        | Owned-process orchestration, exact expected/observed evidence, inert HTML reports        | strict negative/property/lifecycle tests, real loopback conformance     |

Deliberately incorrect comparisons live only in tests, not HTTP modes. Regressions prove selected known defects are discriminated; this is not universal mutation coverage. Synthetic fixture IDs are **public exercise selectors, never real credentials**. C# bootstrap selects synthetic identities without passwords; it is not authentication of real people.

## Windows application: execute, inspect and compare

The portable **Application Security Regression Workbench 1.1.0** opens a native window and includes Python/Tk, Java, .NET, PHP and Node. An end user launches one EXE; no separate language installation, command setup or Docker is required. Source builds and release publication are separate steps; this change does not claim a published or installed release.

Choose **Run real owned service regressions**, select all services or one component, acknowledge authorized synthetic use and run. The app starts only its own loopback fixtures and evaluates actual HTTP statuses **and** content invariants. Search the results, inspect the full selected evidence, export a new directory, and reopen an exact saved analysis. **Review supplied HTTP report** imports this project's bounded JSON schema without claiming to execute it. **Compare saved reports** preserves the original comparison engine's union of case IDs, changed assertions, missing execution and regressions.

Eight prepared scenarios are selections within the full application: five real service runs, two explicitly fictional supplied reports and their seven-state comparison. They do not replace user-selected supported inputs. Saved evidence lives in an owner-local SQLite profile outside the EXE/repository; no real login or production scan target exists. Exit waits for active owned analysis and cleanup. [Application guide](docs/windows-application.md), [runtime sources/notices](docs/native-dependencies.md) and [dated acceptance evidence](docs/reports/native-workbench-2026-11-11.md) explain privacy, limits and reproduction.

## Quick start: browser exercise

Node 24+, Python 3.12+:

    npm ci --ignore-scripts
    npm run build
    npm run serve

Open the printed numeric 127.0.0.1 URL. Try a hostile-looking label: the text is displayed literally; no tags/code execute and typed input stays in the tab. Ctrl+C stops. All attribution/help is in the UI. This page does not falsely claim that Java/C#/PHP services are interconnected.

## Run the complete lab

Prerequisites for source CLI development: Temurin JDK 25.0.5, .NET SDK 10.0.404, PHP 8.3+ with PDO SQLite, Node 24+ and Python 3.12+. GitHub's integration runner uses Node 24.22.1 and Ubuntu's maintained PHP/SQLite packages. The Windows portable bundles JRE 25.0.5+8, .NET runtime 10.0.15, PHP 8.5.12 and Node 24.22.1. No runtime third-party Maven/NuGet/Composer/npm libraries are required.

    python -m venv .venv
    .venv\Scripts\python -m pip install --require-hashes -r requirements-dev.lock
    npm ci --ignore-scripts
    npm run build
    bash scripts/native.sh

On Linux/macOS use .venv/bin/python and activate the venv before Bash. On PowerShell run the native script's commands individually (the [runbook](docs/runbook.md) explains). The script compiles actual Java/C# cores, checks PHP syntax/real PDO behavior, runs selected vulnerable comparisons and exercises **all four actual HTTP adapters**. Missing runtimes fail; no hidden skips.

Working evidence is ignored under out/native-http/http.json and http.html. A fresh result directory is mandatory, not silently overwritten. For explicit individual adapters after building: python -m asrl --component session --output out/new-session. All is the default; no external target/URL option exists. Only owned numeric-loopback processes are started and stopped in a finally block.

## Compare saved regression runs

```powershell
python -m asrl.compare out/previous/http.json out/current/http.json --output out/review
```

Open the escaped standalone `comparison.html`. Review every regressed or still-failing case, missing execution, new case and changed assertion. The union of IDs prevents deleting a failing case from looking like a fix; changing expected status or component also cannot count as a recovery. Exact input-byte hashes and source commits remain in the report. A recovery requires the same component/expected status and successful status **and** content invariant. This compares saved HTTP evidence only; native core/browser checks stay separate. Matching labels do not prove test implementation equivalence and observed latencies are not controlled benchmarks. Reports must be bounded ordinary local files and output must be new.

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
| [asrl/compare.py](asrl/compare.py) | Jason Stys: exact-byte regression run comparison; missing execution never becomes a pass. |
| [asrl/desktop.py](asrl/desktop.py) | Native offline workbench: real project inputs, analysis, searchable evidence, history and export. Jason Stys. |
| [asrl/desktop\_io.py](asrl/desktop_io.py) | Bounded regular descriptor reads and strict finite JSON for owner-local desktop state. Jason Stys. |
| [asrl/desktop\_project.py](asrl/desktop_project.py) | Real native HTTP regression execution and exact saved-report review for the desktop. Jason Stys. |
| [asrl/desktop\_state.py](asrl/desktop_state.py) | Owner-local desktop profile, bounded durable bundles and non-overwriting export. Jason Stys. |
| [asrl/evidence.py](asrl/evidence.py) | Jason Stys: validated expected/observed security evidence, honest verdicts and inert HTML summaries. |
| [asrl/inputs.py](asrl/inputs.py) | Bounded stable ordinary-file reads and streaming tool hashes for offline identity inputs. Jason Stys. |
| [asrl/native\_runtime.py](asrl/native_runtime.py) | Closed, exact-byte app-local runtime admission and minimal service environment. Jason Stys. |
| [asrl/native\_spawn.py](asrl/native_spawn.py) | Temporarily isolate fixed native children from inherited PyInstaller Windows DLL search state. Jason Stys. |
| [asrl/native\_stderr.py](asrl/native_stderr.py) | Bounded volatile startup classification for owned PHP; raw errors and paths never escape. Jason Stys. |
| [asrl/transport.py](asrl/transport.py) | Jason Stys: explicit owned numeric-loopback request/process lifecycle, no external-target scan interface. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: independent native boundaries, not a fake production federation. |
| [docs/contracts.md](docs/contracts.md) | Native fixture and evidence contracts. |
| [docs/handbook.md](docs/handbook.md) | Application Security Regression Lab handbook. |
| [docs/native-dependencies.md](docs/native-dependencies.md) | Native runtime sources and notices. |
| [docs/reports/ci.json](docs/reports/ci.json) | Immutable accepted-source Actions check snapshot, not a future guarantee. |
| [docs/reports/documentation-refresh-2026-11-09.md](docs/reports/documentation-refresh-2026-11-09.md) | Documentation refresh — 2026-11-09. |
| [docs/reports/native-workbench-2026-11-11.md](docs/reports/native-workbench-2026-11-11.md) | Native security regression workbench — 2026-11-11. |
| [docs/reports/office-input-boundary-2026-11-10.md](docs/reports/office-input-boundary-2026-11-10.md) | Documentation input boundary review — 2026-11-10. |
| [docs/reports/portfolio-sync-2026-10-22.md](docs/reports/portfolio-sync-2026-10-22.md) | <!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->. |
| [docs/reports/project-guide.docx](docs/reports/project-guide.docx) | Reviewed Word project guide with source revision and dated validation scope. |
| [docs/reports/publications.json](docs/reports/publications.json) | Exact reviewed Office file identities, immutable source baseline and workflow observations. |
| [docs/reports/regression-review-2026-11-09.md](docs/reports/regression-review-2026-11-09.md) | Regression run review validation — November 9, 2026. |
| [docs/reports/validation.md](docs/reports/validation.md) | Validation and acceptance record. |
| [docs/research.md](docs/research.md) | Primary sources and selected control references. |
| [docs/runbook.md](docs/runbook.md) | Local operations and reproducing results. |
| [docs/security.md](docs/security.md) | Threat model and review boundaries. |
| [docs/testing.md](docs/testing.md) | Test strategy and limitations. |
| [docs/windows-application.md](docs/windows-application.md) | Windows application guide. |
| [examples/desktop/baseline.json](examples/desktop/baseline.json) | Explicitly fictional supplied comparison baseline; not an observed native test execution. |
| [examples/desktop/candidate.json](examples/desktop/candidate.json) | Explicitly fictional supplied comparison changes with missing/new/changed/mismatching assertions. |
| [global.json](global.json) | Exact patched .NET SDK 10.0.404, no automatic version roll-forward. |
| [native-sdks.lock.json](native-sdks.lock.json) | Official fixed runtime/SDK archive sizes, URLs and provider hashes used only by the developer build. |
| [package-lock.json](package-lock.json) | Complete integrity-locked npm tool graph. |
| [package.json](package.json) | Exact browser tool graph and build/verification commands. |
| [playwright.config.mjs](playwright.config.mjs) | Jason Stys: real corrected DOM exercise on three browser engines and a mobile layout, no artifact/cache uploads. |
| [pyproject.toml](pyproject.toml) | Strict Python evidence/conformance lint/type/95% combined coverage gates. |
| [requirements-dev.in](requirements-dev.in) | Exact Python development tool inputs. |
| [requirements-dev.lock](requirements-dev.lock) | Complete portable hash-locked Python development graph. |
| [requirements-native.lock](requirements-native.lock) | Exact SHA256-locked freezing tools; no runtime provider credentials or external SDK lookup at app launch. |
| [scripts/build.mjs](scripts/build.mjs) | Jason Stys: copy reviewed static assets after strict TypeScript compilation; private reports/state excluded. |
| [scripts/build\_native.py](scripts/build_native.py) | Freeze the real four-service workbench with exact app-local runtimes; no install or publication. Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Jason Stys: generate exact definition/variable line maps and verify Python function/class contracts. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Jason Stys: exact tracked-file README purpose inventory; unknown files fail instead of receiving guessed descriptions. |
| [scripts/native.sh](scripts/native.sh) | Jason Stys: real native compilation/core comparisons and owned-loopback conformance; never skip a runtime. |
| [scripts/native\_acceptance.py](scripts/native_acceptance.py) | Actual frozen AppSec widgets, four real service engines and durable restart acceptance. Jason Stys. |
| [scripts/native\_common.py](scripts/native_common.py) | Actual patched Python/Tcl/Tk/PyInstaller runtime notices and authored portable icon. Jason Stys. |
| [scripts/native\_entry.py](scripts/native_entry.py) | Launch the actual bundled offline project workbench; no setup shell commands. Jason Stys. |
| [scripts/prepare\_native\_crt.ps1](scripts/prepare_native_crt.ps1) | Read-only discovery and actual Microsoft signature/hash validation of licensed app-local CRT build inputs. |
| [scripts/prepare\_native\_sdks.py](scripts/prepare_native_sdks.py) | Verify exact official Windows SDK archives and inert local extraction; never install globally. Jason Stys. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/test\_native\_app.py](scripts/test_native_app.py) | Run the real frozen workbench twice with an owned synthetic profile and exact bundle persistence. Jason Stys. |
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
| [tests/test\_compare.py](tests/test_compare.py) | Jason Stys: independent regression cohort/status oracles and exact source/output boundaries. |
| [tests/test\_desktop\_gui.py](tests/test_desktop_gui.py) | Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys. |
| [tests/test\_desktop\_project.py](tests/test_desktop_project.py) | Independent exact-report/cohort/user-control oracles; mocks do not establish actual native execution. Jason Stys. |
| [tests/test\_desktop\_state.py](tests/test_desktop_state.py) | Independent offline desktop ownership, byte-bound, SQLite and non-overwrite regressions. Jason Stys. |
| [tests/test\_evidence.py](tests/test_evidence.py) | Jason Stys: property and negative checks for truthful verdicts, strict reports and inert rendering. |
| [tests/test\_native\_diagnostics.py](tests/test_native_diagnostics.py) | Actual failure-summary privacy/bounds tests; no process, service or application result is mocked into a pass. Jason Stys. |
| [tests/test\_native\_inputs.py](tests/test_native_inputs.py) | Actual same-descriptor input bounds and ownership-change cases for selected offline reports. Jason Stys. |
| [tests/test\_native\_preflight.py](tests/test_native_preflight.py) | Native builder preflight false-pass controls; actual PHP execution remains the separate native gate. Jason Stys. |
| [tests/test\_native\_runtime.py](tests/test_native_runtime.py) | Independent bundled-runtime boundaries without executing any fixture or modifying global tools. Jason Stys. |
| [tests/test\_native\_sdks.py](tests/test_native_sdks.py) | Actual inert developer-archive extraction and provider boundary regressions. Jason Stys. |
| [tests/test\_native\_spawn.py](tests/test_native_spawn.py) | DLL-directory lifecycle refusal/cleanup and actual inert Windows child inheritance controls. Jason Stys. |
| [tests/test\_native\_stderr.py](tests/test_native_stderr.py) | Owned-pipe privacy/cap/drain and real PHP-capability handshake regressions. Jason Stys. |
| [tests/test\_profile\_admission.py](tests/test_profile_admission.py) | Actual pre-existing alias refusal and ordinary SQLite recovery continuity. Jason Stys. |
| [tests/test\_publication\_privacy.py](tests/test_publication_privacy.py) | Jason Stys: credentials in actual Word XML remain visible to repository privacy checks. |
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

## Documentation editions

Start with the [organized handbook](docs/handbook.md) for current usage, design, security and test guidance. Reviewed downloadable editions: [project-guide.docx](docs/reports/project-guide.docx).

[Publication identities and source scope](docs/reports/publications.json) · [Documentation validation record](docs/reports/documentation-refresh-2026-11-09.md). Historical results retain their own tested revision and date.
