#!/usr/bin/env bash
# Jason Stys: real native compilation/core comparisons and owned-loopback conformance; never skip a runtime.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: source — line 22
# END CODE MAP
set -euo pipefail
mkdir -p out/java
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
export DOTNET_CLI_HOME="${PWD}/out/dotnet-home"
export NUGET_PACKAGES="${PWD}/out/nuget"
javac -encoding UTF-8 -Xlint:all -Werror -d out/java services/java/*.java tests/java/*.java
java -cp out/java PolicyTests > out/java-core.json
dotnet restore services/session/SessionLab.csproj --locked-mode
dotnet restore tests/session/SessionTests.csproj --locked-mode
dotnet build services/session/SessionLab.csproj -c Release --no-restore
dotnet build tests/session/SessionTests.csproj -c Release --no-restore
dotnet format services/session/SessionLab.csproj whitespace --verify-no-changes --no-restore
dotnet format tests/session/SessionTests.csproj whitespace --verify-no-changes --no-restore
dotnet tests/session/bin/Release/net10.0/SessionTests.dll > out/session-core.json
for source in services/php/*.php tests/php/*.php; do
  php -l "$source"
done
php tests/php/store_test.php > out/php-core.json
python -m asrl --output out/native-http
