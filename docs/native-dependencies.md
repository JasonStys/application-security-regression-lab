# Native runtime sources and notices

Created by Jason Stys. Authored code remains MIT. Bundled third-party runtimes and libraries retain their original licenses; the application includes an actual-runtime notices viewer. This inventory records technical provenance and redistribution inputs, not legal clearance or a claim that every upstream source can be rebuilt here.

| Component | Bundled version / source | Admission |
| --- | --- | --- |
| CPython | 3.14.10, actual build interpreter and `python314.dll` | Actual DLL SHA256 is in package metadata and verified by acceptance. Original Python license retained. |
| Tcl / Tk | 9.0.4 in the patched Windows SDK | Actual Tcl/Tk runtime identity and notices read through their runtime library paths, including Windows zipfs. No fabricated 8.6 fallback. |
| Freezer | PyInstaller 6.22.3 / hooks 2026.9 | Exact hashes in `requirements-native.lock`; original notices retained. |
| OpenJDK / Temurin | JRE 25.0.5+8 | Official archive SHA256, complete original legal tree, runtime version, per-file frozen payload hashes. GPLv2 with Classpath Exception terms remain applicable. |
| .NET | runtime 10.0.15, build SDK 10.0.404 | Official SDK SHA512; only the app-local runtime, authored DLL and runtime metadata are bundled. No SDK at application launch. |
| PHP | 8.5.12-1 Windows NTS | Official archive SHA256; PHP, PDO SQLite and SQLite modules/notices are included. `-n` prevents loading a user configuration file. |
| Node | 24.22.1 Windows x64 | Official archive SHA256; fixed executable and original license. No user npm or module lookup at launch. |
| Microsoft CRT | Licensed installed x64 VC runtime | Fixed `vswhere` discovery; actual Microsoft Authenticode-valid DLLs, company identity and file hashes. No global CRT installation or signature bypass. |

`native-sdks.lock.json` is the exact archive URL/size/digest build contract. The runtime manifest records each bundled authored/runtime resource's byte count and SHA256. Normal app launch downloads nothing. SHA256 identifies bytes; it is not an application-publisher Authenticode signature or independent assurance of safety.

## Retained OpenJDK source and build references

The matching official source archive is [OpenJDK25U-jdk-sources_25.0.5_8.tar.gz](https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jdk-sources_25.0.5_8.tar.gz), 120,593,019 bytes, SHA256 `f331d870d998f9c144c361c220960f8ad2de169dc1b1c4dc4145291c501c2341`. The owner has retained its original inert bytes as a distribution input; do not substitute a JRE `src.zip` subset for the corresponding source.

The official [Windows JRE build metadata](https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jre_x64_windows_hotspot_25.0.5_8.zip.json) is 31,640 bytes, SHA256 `57be961b5816ae74bf229a1f2f018adf307676b883054a9b24d83212a755ae29`. It binds the [Temurin build scripts](https://github.com/adoptium/temurin-build/commit/1cf43d7a3e77886bfea7d550a902e151a87d724d) and [OpenJDK source revision](https://github.com/adoptium/jdk25u/commit/7ec19fb1eda7e42498b7ee4ebde29f77aa961a1c), plus configure/build arguments and tool identities. These inputs have not undergone an independent whole-JDK source rebuild in this project. Preserve appropriate source materials and upstream terms alongside any eventual binary distribution; release publication is a separate owner-reviewed operation.

Primary references: [Adoptium licensing FAQ](https://adoptium.net/docs/faq/), [Eclipse Temurin project](https://projects.eclipse.org/projects/adoptium.temurin), [Python 3.14.10](https://www.python.org/downloads/release/python-31410/), [Microsoft .NET download](https://dotnet.microsoft.com/en-us/download/dotnet/10.0), [Node release](https://nodejs.org/download/release/v24.22.1/), [PHP Windows downloads](https://windows.php.net/download/).

The fixed PHP child environment includes only its authenticated app-local directory and System32. This satisfies the [PDO_SQLITE Windows dependency requirement](https://www.php.net/manual/en/ref.pdo-sqlite.php) without inheriting a user's PATH or copying DLLs into Windows. The builder tests actual PDO capability, refuses an actually missing extension and retests the restored admitted bytes. Final frozen acceptance separately exercises real SQLite-backed HTTP upload behavior.

The frozen app's PHP child uses a fresh per-analysis runtime directory outside PyInstaller's extraction namespace. Full original bundle validation precedes any fixed nine-file copy; every copied program/library/router/schema byte is rebound to its admitted hash. The child receives the same fixed minimal configuration and is waited/drained before nonce-owned copy cleanup. This is isolation of the external runtime's file namespace, not system installation, arbitrary plugin support or proof of a particular Windows loader cause. The final native consumer retains the original 150 real HTTP status/content oracles.
