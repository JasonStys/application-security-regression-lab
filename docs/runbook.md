# Local operations and reproducing results

Author: Jason Stys. Synthetic-only trusted host. [README](../README.md) gives setup. Keep native runtimes patched; exact CI versions and platform limits are in validation.

## Native commands (PowerShell or Bash)

    mkdir out/java
    javac -encoding UTF-8 -Xlint:all -Werror -d out/java services/java/*.java tests/java/*.java
    java -cp out/java PolicyTests
    dotnet restore services/session/SessionLab.csproj --locked-mode
    dotnet restore tests/session/SessionTests.csproj --locked-mode
    dotnet build services/session/SessionLab.csproj -c Release --no-restore
    dotnet build tests/session/SessionTests.csproj -c Release --no-restore
    dotnet tests/session/bin/Release/net10.0/SessionTests.dll
    php tests/php/store_test.php
    python -m asrl --output out/new-http

Create out/java only if absent. Activate the venv or replace python with its absolute executable. Install PDO SQLite from your trusted platform/vendor distribution if absent; do not silently skip its checks. Build npm assets first. Session SDK is pinned by global.json. Native script also validates format/PHP syntax.

For one explicit component: --component java/session/php/node. Results say exactly which adapters executed. No external target or custom executable option. Report directory must be new with existing parent; do not pass sensitive files to fixtures.

## Browser exercise

npm run serve opens a loopback-only Node demo; browse printed numeric URL, not localhost. Render hostile-looking text literally, fetch synthetic fixture, observe invalid-byte error preserving preview and read Help. This is not a tenant account portal. Ctrl+C stops. Do not expose via port forwarding/reverse proxy or repurpose fixture IDs as passwords.

## Cleanup/recovery

The conformance runner verifies identity before sending mutations and stops only its own PIDs in a finally block. Timeout/failure is nonzero, not a skipped success. Preserve failed report evidence privately if useful. Re-run with a new output directory; no automatic overwrite/pruning. Out contains only transient synthetic local state, but Git ignore is not encryption.

If readiness fails: verify runtime/install/build/available port before changing code. Do not repair Docker, weaken TLS/OS defenses or target some other listening service. Windows command-sandbox named pipes can block dotnet format/Firefox; trusted runs outside that command sandbox may be used without altering OS/browser protections, and hosted verification remains authoritative for missing native tools.

No production deployment/rollback exists. For source regression, preserve current branch/data, revert the specific reviewed change in a new commit, and rerun all gates. Never use destructive reset or erase evidence to conceal failures.
