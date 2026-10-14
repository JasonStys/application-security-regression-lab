# Validation and acceptance record

Created by Jason Stys. Recorded 2026-10-14. Accepted executable source: 9538721dd1dddac74949e170ab15c022358f69cf. All 13 jobs completed successfully: [Validate](https://github.com/JasonStys/application-security-regression-lab/actions/runs/38532952741), [CodeQL](https://github.com/JasonStys/application-security-regression-lab/actions/runs/38532952764). The [immutable machine-readable snapshot](ci.json) contains exact job times, URLs and source SHA. Documentation-only follow-up commits rerun both workflows; this record is not a future-source guarantee.

## Measured acceptance

| Layer | Observed result | Scope and environment |
| --- | --- | --- |
| Python evidence/conformance | 54 tests passed on each of four lanes | Python 3.12 Ubuntu; Python 3.14 Ubuntu, Windows and macOS Intel |
| Python combined statement/branch coverage | 99.37% Linux/macOS; 98.73% Windows | All five asrl modules, no coverage omissions; required gate 95%. Not native-language or browser coverage |
| Java core | 37 assertions passed, including two selected incorrect-comparison witnesses | Actual Temurin 25.0.4 compilation, all javac lint warnings fatal; Ubuntu and Windows |
| C# core | 22 assertions passed, including two selected incorrect comparisons | Actual .NET SDK 10.0.401 builds, nullable/warnings/format gates; Ubuntu and Windows |
| PHP / SQLite core | 47 assertions passed, including two selected incorrect comparisons | Actual native PDO SQLite and PHP syntax checks on Ubuntu; not a mocked evaluator |
| All-service HTTP | 75/75 passed | Four real owned loopback adapters: Java authorization/edit races, C# issuance/revocation/scope, PHP search/upload/download, Node static/input guards |
| Native Node / compiled TypeScript | 19/19 passed | Actual HTTP boundary requests, runtime text/Unicode/schema checks, test-only unsafe comparison |
| Browser acceptance | 16/16 passed | Chromium, Firefox, WebKit, Pixel 7 layout; no retries or skipped tests. Active-tag/dialog absence, local-only requests, keyboard/overflow, axe WCAG A/AA, help |
| Static/repository checks | Passed | Ruff lint/format, strict mypy/TypeScript, Prettier, exact symbol maps, complete file inventory, privacy/links/pins/test-code confinement |
| Supply chain / CI checks | Passed; no known dependency vulnerabilities or detected secret leaks | Complete hash-locked Python and integrity-locked npm graphs audited; redacted full-history Gitleaks, actionlint, ShellCheck. No advisory exclusions |
| CodeQL security-extended | All four jobs passed; zero open alerts at acceptance | Python, JavaScript/TypeScript, Java and C#. PHP is not a supported CodeQL language; no false PHP SAST claim |

Runtime CI selections: Node 24.21.0, Temurin 25.0.4, .NET SDK 10.0.401; Ubuntu runner's maintained PHP/SQLite packages. Runtime code uses platform libraries only, with no Maven/NuGet/Composer/npm runtime dependency graph. Scanner versions and official download hashes are in tools.lock.json; browser/tool versions are locked in package-lock.json and requirements-dev.lock. Runtime/system patch versions can change independently of source.

## Local corroboration

Windows PC: Python 3.14.6, Node 24.18.1, .NET SDK 10.0.401. The final executable source passed all 54 Python tests at 98.73% combined coverage, all 19 native Node/typed tests, strict lint/type/map/inventory/format checks, the C# build with zero warnings/errors and 20/20 actual C# HTTP cases, including required Secure cookie attributes. Native C# core: 22/22. Browser suite: 16/16 across the four projects.

The in-app browser also verified script-looking labels stay literal, the local synthetic sample loads, and Help explains independent services and limitations. The preview contains Jason Stys attribution and contact links. Local Java/PHP runtimes were unavailable: their actual compilers/PDO/HTTP acceptance is supplied by the hosted jobs, not inferred from Python mocks. Docker was left unchanged. Trusted Windows formatter/Firefox checks ran outside the command sandbox where named-pipe/process restrictions prevented launching; no OS, browser sandbox or TLS protection was disabled.

## Regressions found and fixed

- JDK 25 rejected unattached file-header Javadoc comments under warnings-as-errors. Purpose headers now use ordinary comments before imports; class/function Javadoc remains attached. The compiler gate was retained. Initial failed runs are preserved: [Validate](https://github.com/JasonStys/application-security-regression-lab/actions/runs/38531739655), [CodeQL](https://github.com/JasonStys/application-security-regression-lab/actions/runs/38531739560).
- CodeQL identified a missing Secure cookie flag. Both issuance/deletion now set Secure; actual HTTP acceptance requires Secure, HttpOnly, SameSite Strict, Path and Max-Age. A focused negative verdict test ensures missing Secure fails. Alert resolved through source correction, not dismissal, suppression or exclusion.
- Browser development uncovered an ambiguous nested input label and a delayed fetch/input interaction. The label is explicit and separate, the fetch-complete status is distinct, and an input revision guard prevents obsolete responses overwriting newer input. The measured browser cases exercise literal output, fixture completion, preservation on invalid input and accessibility; they are not a claim of exhaustive asynchronous-race coverage.
- Header-negative Node tests originally used Fetch, which rewrites forbidden headers. They now use actual node:http requests to test the intended Host/fetch-metadata boundary rather than relaxing the server.

## Storage and retained evidence

Read-only account check at 2026-10-14T08:09:03Z: 72 repositories, 8,419,929 live artifact bytes, zero private-repository artifact bytes; Actions caches separately 9,029,833,071 bytes. The freshly inspected billing Actions meter showed 0.5 GB used / 0.5 GB included (100%); accrued included usage is not the same quantity as live artifact occupancy or cache bytes. The quota API did not provide a percentage. No cleanup, budget or retention changes were made.

This repo was verified at zero Actions artifacts and zero active caches. Neither workflow uploads artifacts, uses Actions cache nor uploads CodeQL databases. Logs/security results remain distinct storage. Native working JSON/HTML evidence, synthetic SQLite state, tokens, compiler output and browser reports remain ignored under out; no tokens, raw uploads or private user data are committed. Approved cleanup can be repeated separately if requested.

## Limits and interpretation

This is a synthetic educational regression lab on a trusted owner-local host. It is not real authentication, shared identity, a public website deployment, ASVS certification, universal mutation coverage or proof of absence of vulnerabilities. Deliberately unsafe comparisons remain test-only. Python coverage measures orchestration/evidence, not full native source coverage. Case counts include negative assertions and selected comparison witnesses; platform repeats are not new independent security controls.

The C# fixture emits Secure cookie headers on loopback HTTP; the native client explicitly echoes values to exercise the broker. This does not demonstrate browser session acceptance over insecure transport. Trusted HTTPS and a real identity design are prerequisites to any browser/real-data integration. Do not remove Secure to accommodate HTTP.

Request elapsed times are diagnostic observations, not comparable benchmark scores or a certified performance SLO. Resource/input caps and documented complexity support bounded behavior; finite header/body limits do not guarantee immunity to every denial-of-service technique. Reproduce with the README/runbook, then rerun all native, HTTP, browser and security gates after changes.
