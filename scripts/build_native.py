"""Freeze the real four-service workbench with exact app-local runtimes; no install or publication. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 101
# definition: copy_tree — line 105
# parameter: source — line 105
# parameter: target — line 105
# variable: path — line 109
# variable: selected — line 113
# definition: verify_php_capability — line 118
# parameter: root — line 118
# parameter: state — line 118
# variable: result — line 122
# definition: verify_php_http — line 149
# parameter: output — line 149
# parameter: root — line 149
# variable: directory — line 156
# variable: port — line 160
# variable: rows — line 161
# variable: row — line 164
# definition: main — line 173
# variable: source — line 188
# variable: dirty — line 191
# variable: output — line 196
# variable: release — line 196
# variable: sdks — line 200
# variable: jre — line 201
# variable: dotnet — line 202
# variable: node — line 203
# variable: php — line 204
# variable: compiler — line 205
# variable: build_env — line 210
# variable: crt — line 251
# variable: directory — line 254
# variable: stage — line 255
# variable: runtime — line 260
# variable: family — line 262
# variable: name — line 271
# variable: target — line 272
# variable: row — line 275
# variable: selected — line 276
# variable: component — line 279
# variable: session — line 281
# variable: name — line 283
# variable: config_path — line 291
# variable: config — line 292
# variable: options — line 293
# variable: row — line 294
# variable: row — line 299
# variable: classes — line 303
# variable: path — line 319
# variable: path — line 325
# variable: notice_sources — line 329
# variable: path — line 334
# variable: notice_sources — line 337
# variable: base_notices — line 344
# variable: blocks — line 345
# variable: path — line 346
# variable: title — line 346
# variable: raw — line 347
# variable: combined — line 351
# variable: entries — line 357
# variable: path — line 363
# variable: manifest — line 366
# variable: extension — line 376
# variable: held — line 377
# variable: resources — line 396
# variable: name — line 404
# variable: metadata — line 406
# variable: name — line 414
# variable: path — line 414
# variable: command — line 420
# variable: name — line 442
# variable: path — line 442
# variable: command — line 444
# variable: name — line 448
# variable: command — line 449
# variable: command — line 450
# variable: packed — line 469
# variable: name — line 472
# variable: packed_names — line 472
# variable: row — line 475
# variable: name — line 476
# variable: data — line 479
# variable: executable — line 487
# variable: stream — line 488
# variable: digest — line 489
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def copy_tree(source: Path, target: Path) -> None:
    """Copy only verified regular one-link SDK/authored files into this new owned package stage."""
    from asrl.inputs import file_hash

    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        file_hash(path, 256 * 1024 * 1024)
        selected = target / path.relative_to(source)
        selected.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, selected)


def verify_php_capability(root: Path, state: Path) -> None:
    """Require actual SQLite PDO capability under the same fixed absolute extension/minimal child environment."""
    from asrl.native_runtime import environment

    result = subprocess.run(
        [
            str(root / "runtime/php/php.exe"),
            "-n",
            "-d",
            "display_errors=0",
            "-d",
            "extension=" + str(root / "runtime/php/ext/php_pdo_sqlite.dll"),
            "-r",
            "exit(PHP_VERSION==='8.5.12' && in_array('sqlite',PDO::getAvailableDrivers(),true)?0:12);",
        ],
        cwd=root,
        env=environment(state, root, "php"),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("Exact staged PHP version/PDO SQLite capability failed")
    print(
        "Actual exact staged PHP/PDO SQLite capability passed with fixed minimal environment",
        flush=True,
    )


def verify_php_http(root: Path, output: Path) -> None:
    """Require all original 24 real PHP HTTP oracles before freezing; distinguish server-SAPI from CLI-only capability."""
    from unittest.mock import patch

    from asrl.cases import exercise
    from asrl.transport import service

    with tempfile.TemporaryDirectory(prefix="owned-php-http-", dir=output) as directory:
        # Only this standalone builder's owned context changes; no application
        # runtime setting or arbitrary caller program is accepted by the app.
        with patch.object(sys, "frozen", True, create=True):
            with service("php", root, Path(directory)) as port:
                rows = exercise("php", port)
        if len(rows) != 24 or any(
            row["observed"] != row["expected"] or row["content_ok"] is not True
            for row in rows
        ):
            raise ValueError("Actual staged PHP HTTP status/content oracles failed")
    print(
        "Actual staged PHP HTTP/health/SQLite passed all 24 original status/content oracles",
        flush=True,
    )


def main() -> None:
    """Build with pinned verified SDKs, strict resource identity and actual runtime notices; user launch needs no SDK."""
    from asrl import desktop_project as project
    from asrl.inputs import file_hash
    from asrl.native_runtime import validate as validate_runtime
    from scripts.native_common import icon, notices
    from scripts.prepare_native_sdks import main as prepare_sdks

    if sys.platform != "win32" or sys.version_info[:3] != (3, 14, 10):
        raise RuntimeError("Patched Windows CPython3.14.10 is required")
    if (
        tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
        != project.VERSION
    ):
        raise ValueError("Native version coherence failed")
    source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip()
    )
    release, output = ROOT / "release", ROOT / "out"
    release.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    prepare_sdks()
    sdks = ROOT / ".tools/native-sdks"
    jre = sdks / "temurin-jre-25.0.5-8/jdk-25.0.5+8-jre"
    dotnet = sdks / "dotnet-sdk-10.0.404"
    node = sdks / "node-24.22.1/node-v24.22.1-win-x64"
    php = sdks / "php-8.5.12-1-nts"
    compiler = os.environ.get("ASRL_JAVAC") or shutil.which("javac")
    if not compiler:
        raise ValueError(
            "Development Java compiler is required to build; users receive compiled classes"
        )
    build_env = {
        **os.environ,
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
        "DOTNET_NOLOGO": "1",
        "DOTNET_CLI_HOME": str(output / "dotnet-home"),
        "NUGET_PACKAGES": str(output / "nuget"),
    }
    subprocess.run(
        [
            str(dotnet / "dotnet.exe"),
            "restore",
            "services/session/SessionLab.csproj",
            "--locked-mode",
        ],
        cwd=ROOT,
        env=build_env,
        check=True,
    )
    subprocess.run(
        [
            str(dotnet / "dotnet.exe"),
            "build",
            "services/session/SessionLab.csproj",
            "-c",
            "Release",
            "--no-restore",
        ],
        cwd=ROOT,
        env=build_env,
        check=True,
    )
    subprocess.run(
        [
            "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
            "-NoProfile",
            "-File",
            "scripts/prepare_native_crt.ps1",
        ],
        cwd=ROOT,
        check=True,
    )
    crt = json.loads((output / "native-crt.json").read_text(encoding="utf-8-sig"))
    notices(release / "notices.txt")
    icon(output / "app.ico")
    with tempfile.TemporaryDirectory(prefix="owned-package-", dir=output) as directory:
        stage = Path(directory)
        if stage.resolve().parent != output.resolve():
            raise ValueError(
                "Owned package staging directory escaped its intended output root"
            )
        runtime = stage / "runtime"
        copy_tree(jre, runtime / "java")
        for family in ("Microsoft.NETCore.App", "Microsoft.AspNetCore.App"):
            copy_tree(
                dotnet / "shared" / family / "10.0.15",
                runtime / "dotnet/shared" / family / "10.0.15",
            )
        copy_tree(dotnet / "host/fxr/10.0.15", runtime / "dotnet/host/fxr/10.0.15")
        shutil.copyfile(dotnet / "dotnet.exe", runtime / "dotnet/dotnet.exe")
        (runtime / "node").mkdir()
        shutil.copyfile(node / "node.exe", runtime / "node/node.exe")
        for name in ("php.exe", "php8.dll", "libsqlite3.dll", "ext/php_pdo_sqlite.dll"):
            target = runtime / "php" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(php / name, target)
        for row in crt["files"]:
            selected = Path(crt["directory"]) / row["name"]
            if file_hash(selected, 4 * 1024 * 1024) != row["sha256"]:
                raise ValueError("Actual signed CRT changed after verification")
            for component in ("php", "dotnet"):
                shutil.copyfile(selected, runtime / component / row["name"])
        session = runtime / "session"
        session.mkdir()
        for name in (
            "SessionLab.dll",
            "SessionLab.deps.json",
            "SessionLab.runtimeconfig.json",
        ):
            shutil.copyfile(
                ROOT / "services/session/bin/Release/net10.0" / name, session / name
            )
        config_path = session / "SessionLab.runtimeconfig.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        options = config["runtimeOptions"]
        if {row["name"] for row in options["frameworks"]} != {
            "Microsoft.NETCore.App",
            "Microsoft.AspNetCore.App",
        }:
            raise ValueError("Review changed required .NET framework inventory")
        for row in options["frameworks"]:
            row["version"] = "10.0.15"
        options["rollForward"] = "Disable"
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        classes = runtime / "java-classes"
        classes.mkdir()
        subprocess.run(
            [
                compiler,
                "--release",
                "21",
                "-g:none",
                "-encoding",
                "UTF-8",
                "-Xlint:all",
                "-Werror",
                "-d",
                str(classes),
                *[
                    str(path)
                    for path in sorted((ROOT / "services/java").glob("*.java"))
                ],
            ],
            cwd=ROOT,
            check=True,
        )
        for path in (ROOT / "services/php", ROOT / "services/node", ROOT / "dist"):
            copy_tree(path, stage / path.relative_to(ROOT))
        (stage / "sql").mkdir()
        shutil.copyfile(ROOT / "sql/schema.sql", stage / "sql/schema.sql")
        notice_sources = [
            (
                "OpenJDK Temurin25.0.5 runtime / " + path.relative_to(jre).as_posix(),
                path,
            )
            for path in sorted((jre / "legal").rglob("*"))
            if path.is_file()
        ]
        notice_sources += [
            ("Node.js24.22.1 and bundled dependencies", node / "LICENSE"),
            ("PHP8.5.12-1 license", php / "license.txt"),
            ("PHP binary dependency notices", php / "readme-redist-bins.txt"),
            ("Microsoft .NET SDK/runtime license", dotnet / "LICENSE.txt"),
            ("Microsoft .NET dependency notices", dotnet / "ThirdPartyNotices.txt"),
        ]
        base_notices = (release / "notices.txt").read_bytes()
        blocks = [base_notices]
        for title, path in notice_sources:
            raw = path.read_bytes()
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("Actual runtime notice exceeds per-file bound")
            blocks.append(title.encode() + b"\n" + raw)
        combined = b"\n\n".join(blocks)
        if len(combined) > 8 * 1024 * 1024:
            raise ValueError(
                "Actual combined runtime notices exceed supported viewer bound"
            )
        (release / "notices.txt").write_bytes(combined)
        entries = [
            {
                "path": path.relative_to(stage).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": file_hash(path, 256 * 1024 * 1024),
            }
            for path in sorted(stage.rglob("*"))
            if path.is_file()
        ]
        manifest = release / "runtime-manifest.json"
        manifest.write_text(
            json.dumps({"schema": 1, "entries": entries}, indent=2) + "\n",
            encoding="utf-8",
        )
        shutil.copyfile(manifest, stage / "runtime-manifest.json")
        validate_runtime(stage)
        verify_php_capability(stage, output)
        # An actual missing-module control must fail under the same command,
        # then the exact admitted DLL must be restored before any freezing.
        extension = stage / "runtime/php/ext/php_pdo_sqlite.dll"
        held = extension.with_suffix(".disabled-owned-check")
        extension.rename(held)
        try:
            try:
                verify_php_capability(stage, output)
            except ValueError:
                print(
                    "Actual missing PDO extension refused by staged capability check",
                    flush=True,
                )
            else:
                raise RuntimeError(
                    "Missing PDO extension incorrectly passed capability admission"
                )
        finally:
            held.rename(extension)
        validate_runtime(stage)
        verify_php_capability(stage, output)
        verify_php_http(stage, output)
        resources = {
            name: release / name
            if name in ("runtime-manifest.json", "notices.txt")
            else output / name
            if name == "app.ico"
            else Path(sys.base_prefix) / name
            if name == "python314.dll"
            else ROOT / name
            for name in project.RESOURCES
        }
        metadata = {
            "schema": 1,
            "product": project.PRODUCT,
            "version": project.VERSION,
            "source": source,
            "source_dirty": dirty,
            "resources": {
                name: file_hash(path, 32 * 1024 * 1024)
                for name, path in resources.items()
            },
        }
        (release / "native-release.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--windowed",
            "--noupx",
            "--name",
            "ApplicationSecurityRegressionLab",
            "--icon",
            str(output / "app.ico"),
            "--distpath",
            "release/portable",
            "--workpath",
            "out/native-build",
            "--specpath",
            "out",
            "--paths",
            str(ROOT),
        ]
        for name, path in resources.items():
            if name != "python314.dll":
                command += [
                    "--add-data",
                    str(path) + os.pathsep + Path(name).parent.as_posix(),
                ]
        for name in ("runtime", "services", "dist", "sql"):
            command += ["--add-data", str(stage / name) + os.pathsep + name]
        command += [
            "--add-data",
            str(release / "native-release.json") + os.pathsep + ".",
            "scripts/native_entry.py",
        ]
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            env={
                **os.environ,
                "PYINSTALLER_CONFIG_DIR": str(output / "native-freezer-cache"),
            },
        )
        # Inspect actual collected bytes, including Windows TOC separator
        # normalization. A declared SDK hash is not evidence of what the freezer
        # finally embedded, and missing authored data must not be a runtime surprise.
        from PyInstaller.archive.readers import CArchiveReader

        packed = CArchiveReader(
            str(release / "portable/ApplicationSecurityRegressionLab.exe")
        )
        packed_names = {name.replace("\\", "/"): name for name in packed.toc}
        if len(packed_names) != len(packed.toc):
            raise ValueError("Ambiguous frozen runtime paths")
        for row in entries:
            name = packed_names.get(row["path"])
            if name is None:
                raise ValueError("Actual frozen runtime/data entry is missing")
            data = packed.extract(name)
            if (
                len(data) != row["bytes"]
                or hashlib.sha256(data).hexdigest() != row["sha256"]
            ):
                raise ValueError(
                    "Actual frozen runtime/data bytes differ from verified inputs"
                )
    executable = release / "portable/ApplicationSecurityRegressionLab.exe"
    with executable.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    executable.with_suffix(".exe.sha256").write_text(
        digest + "  " + executable.name + "\n", encoding="ascii"
    )
    print(
        "Complete four-runtime portable built; source_dirty="
        + str(dirty)
        + "; not installed or published"
    )


if __name__ == "__main__":
    main()
