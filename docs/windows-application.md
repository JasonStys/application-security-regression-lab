# Windows application guide

Created by Jason Stys. The portable workbench is an owner-local graphical application for this project's actual security regressions and saved-evidence review. It is not a public service, vulnerability scanner or production identity system.

## Launch and choose a workflow

Launch `ApplicationSecurityRegressionLab.exe`. Its bundled runtime needs no Python, Java, .NET, PHP or Node installation. The window exposes Inputs, Findings, Saved analyses, Help and licenses. Run and lifecycle controls remain visible at the minimum 980 × 700 window. Attribution and GitHub/LinkedIn contact details are available in Help.

| Operation | Inputs and result |
| --- | --- |
| Run real owned service regressions | Choose all, Java, C# sessions, PHP or Node. The original core runner starts that authored fixture on numeric loopback, verifies its nonce/runtime identity, runs its actual expected-status/content cases, and saves JSON plus inert HTML. There is no target URL, custom executable or arbitrary code option. |
| Review supplied HTTP report | Select an authorized ordinary local JSON report conforming to the original strict evidence schema. Inspect every case and mismatch. The UI labels it supplied evidence rather than a newly executed test. |
| Compare saved reports | Select baseline and candidate reports. The existing comparison engine classifies unchanged pass/failure, recovery, regression, missing execution, new case and changed assertion. Changing/deleting an assertion cannot count as recovery. Exact original bytes remain in the saved bundle. |

The prepared menu contains five real service choices plus two fictional reports and their comparison. Select a prepared case to populate the same editable controls; you may choose your own supported report files instead. Fictional fixture descriptions explicitly identify their origin.

## Review, save and export

After Run, search the literal findings text, select a row and read its complete JSON detail. For a comparison the table shows baseline/candidate expected and observed statuses with content-match evidence; a missing side reads “not executed.” Clear the search to restore the full denominator. Native core and browser checks remain separate from HTTP evidence.

Each completed operation is an immutable, hash-bound local bundle. Saved analyses reopens the original parameters and result bytes; it does not rerun an old service or reinterpret a supplied report as executed. Export creates a **new** directory and refuses overwrite. Opening exported HTML displays escaped inert evidence without remote assets or scripts.

The default profile uses the operating system's local application-data directory, in an `ApplicationSecurityRegressionLab` subdirectory. Developer `--profile` supports a separate authorized location. Profiles contain plaintext reports, input copies and SQLite history; protect them with OS permissions. They are outside Git and the installation folder. Back up the entire profile only after normal exit. No passwords, provider keys, real records or sensitive uploads belong in this educational lab.

Retention is bounded to 20 saved analyses and 128 MiB of bundle payloads; SQLite metadata adds overhead. Each bundle is at most 64 MiB, each file 32 MiB. Export wanted evidence and explicitly delete selected local analyses to make room; nothing is silently evicted. The UI reports invalid input or full storage without deleting saved results.

## Close and recover

Exit waits for the active analysis and owned-service cleanup. It does not abandon a worker and claim a successful shutdown. A second instance cannot own the same profile concurrently. Pre-existing linked, nonregular or multiply linked fixed DB, marker, lock and SQLite-sidecar files are rejected before initialization; ordinary genuine SQLite recovery files remain supported. These controls prevent accidental aliases, not all races by a malicious same-OS administrator.

Missing/corrupted bundled runtimes fail admission before a run. A failed owned service yields a bounded component/category message, never raw credentials or arbitrary process output. Invalid imported files leave saved history unchanged. If startup refuses a profile, close other instances and inspect permissions; do not delete recovery files or reset the database to bypass a refusal.

## Source build and acceptance

On an authorized Windows development machine, use CPython **3.14.10 with Tk**, a Java compiler, a licensed Visual Studio x64 CRT installation, the exact locks and a built Node UI:

```powershell
python -m pip install --require-hashes -r requirements-dev.lock -r requirements-native.lock
npm ci --ignore-scripts
npm run build
python scripts/build_native.py
python scripts/test_native_app.py
```

The builder downloads only four fixed official archives, verifies provider digests and every extracted SDK file, validates Microsoft CRT signatures, compiles authored service code, bundles notices and verifies the real frozen CArchive payloads. It changes no global runtime, registry or Docker configuration. The actual consumer launches the final EXE twice with a temporary synthetic profile and drives the same Tk widgets, core functions and mainloop. `source_dirty` distinguishes a development candidate from a clean-source package; CI requires clean source. This is a Windows x64 portable, not an NSIS installer, code-signing or all-OS native-package claim.

PHP's admitted external-runtime closure is temporarily copied into this analysis's own private working directory and checked again before launch. Allow space for that bounded temporary copy; it is removed after the exact owned service has stopped. Normal app launch still downloads nothing and installs no system runtime. The application does not accept user executables, shell commands, external test targets or provider keys. Earlier Windows validation failures and the controlled namespace experiment are documented in the dated native report; a local source/package test is distinct from hosted acceptance.
