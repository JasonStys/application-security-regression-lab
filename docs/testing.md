# Test strategy and limitations

Author: Jason Stys. Test critical boundaries in native cores, actual HTTP adapters and real DOM; record failures accurately.

- Java native tests: cross-tenant/operation/null/unknown/duplicate/encoding/size rejection, quote safety, unchanged state, version races and test-only incorrect comparisons. Actual javac warnings-as-errors, Linux/Windows.
- C# native tests: random uniqueness, authoritative scope, exact expiry boundary/backward time, revocation/peer isolation, expired capacity reclamation and incorrect test predicates. Nullable/warnings-as-errors/format and actual .NET builds, Linux/Windows.
- PHP actual PDO/SQLite tests: same-tenant prepared literal search, SQL comparison witness, UTF8/text/path/extension/device rejection, byte/count quotas and rollback, same-tenant downloads. Real PHP lint and native tests on Ubuntu; not a mocked PHP evaluator.
- Python: strict verdict/report negatives, Hypothesis truth property, real sockets/response cap, owned process failures/cleanup/timeout, CLI no-overwrite/links, and mocked case-construction tests explicitly separate from native service acceptance.
- Real all-service integration: component handshake before mutations, exact statuses AND headers/content/absence, fixture scope, protected uploads/downloads, token issue/revoke/isolation, Host/Origin/no-CSRF and malformed inputs. Missing runtimes fail, never skip.
- Native Node/compiled TypeScript: Unicode/byte/shape cases, text sink, precise native HTTP headers, static allowlist and private failure. Real browsers: active-tag/dialog absence, literal labels, local-only requests, preservation on bad input, keyboard/overflow, axe WCAG A/AA and help.
- Complete locked tool-graph audits, full-history redacted Gitleaks, actionlint/ShellCheck, exact maps/file guide/links/privacy, security-extended CodeQL for four supported languages.

Python conformance/evidence gate is 95% combined statement/branch coverage, all asrl modules, no omissions. This percentage does not measure Java/C#/PHP/DOM coverage. Native case counts and real adapter/browser scenarios are independently recorded. Selected incorrect comparisons are not complete mutation coverage or proof every ASVS requirement is met.

Run npm build before tests, activate venv then bash scripts/validate.sh. Full native: bash scripts/native.sh. Browser: npx playwright install chromium firefox webkit, npm run test:e2e (Linux CI --with-deps). [Measured report](reports/validation.md) records actual source IDs/counts/platforms/fixes. Private working reports ignored; no artifact/cache uploads.
