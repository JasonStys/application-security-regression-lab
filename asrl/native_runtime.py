"""Closed, exact-byte app-local runtime admission and minimal service environment. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ENTRYPOINTS — line 47
# variable: PREFIXES — line 53
# variable: REQUIRED_DATA — line 54
# variable: MAX_RESOURCE — line 73
# variable: MAX_TOTAL — line 74
# variable: RUNTIME_VERSIONS — line 75
# definition: validate — line 83
# parameter: root — line 83
# variable: value — line 85
# variable: entries — line 93
# variable: names — line 96
# variable: total — line 97
# variable: row — line 98
# variable: digest — line 101
# variable: name — line 101
# variable: size — line 101
# variable: path — line 110
# variable: part — line 113
# variable: total — line 126
# variable: selected — line 129
# variable: name — line 136
# variable: name — line 138
# definition: command — line 143
# parameter: component — line 143
# parameter: port — line 143
# parameter: root — line 143
# parameter: state — line 143
# variable: executable — line 148
# definition: environment — line 178
# parameter: state — line 178
# variable: result — line 180
# variable: key — line 182
# END CODE MAP

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

from .desktop_io import Rejected, json_value
from .inputs import file_hash, read_source

ENTRYPOINTS = {
    "java": "runtime/java/bin/java.exe",
    "session": "runtime/dotnet/dotnet.exe",
    "php": "runtime/php/php.exe",
    "node": "runtime/node/node.exe",
}
PREFIXES = ("runtime/", "services/php/", "services/node/", "dist/")
REQUIRED_DATA = {
    "runtime/java-classes/JavaService.class",
    "runtime/java-classes/Policy.class",
    "runtime/java-classes/Policy$Failure.class",
    "runtime/java-classes/Policy$Note.class",
    "runtime/java-classes/Policy$Principal.class",
    "runtime/session/SessionLab.dll",
    "runtime/session/SessionLab.deps.json",
    "runtime/session/SessionLab.runtimeconfig.json",
    "services/php/router.php",
    "services/php/Store.php",
    "sql/schema.sql",
    "services/node/server.mjs",
    "services/node/http.mjs",
    "dist/index.html",
    "dist/app.js",
    "dist/text.js",
    "dist/style.css",
}
MAX_RESOURCE = 256 * 1024 * 1024
MAX_TOTAL = 768 * 1024 * 1024
RUNTIME_VERSIONS = {
    "java": "25.0.5",
    "session": "10.0.15",
    "php": "8.5.12",
    "node": "v24.22.1",
}


def validate(root: Path) -> dict[str, Any]:
    """Hash only closed relative manifest entries; no plugin, arbitrary executable or external path is accepted."""
    value = json_value(read_source(root / "runtime-manifest.json", 2 * 1024 * 1024))
    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "entries"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
    ):
        raise Rejected("runtime_manifest_schema")
    entries = value["entries"]
    if not isinstance(entries, list) or not 4 <= len(entries) <= 4096:
        raise Rejected("runtime_manifest_count")
    names: set[str] = set()
    total = 0
    for row in entries:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise Rejected("runtime_manifest_entry")
        name, size, digest = row["path"], row["bytes"], row["sha256"]
        if (
            not isinstance(name, str)
            or not 1 <= len(name) <= 512
            or "\\" in name
            or ":" in name
            or "\x00" in name
        ):
            raise Rejected("runtime_manifest_path")
        path = PurePosixPath(name)
        if (
            path.is_absolute()
            or any(part in (".", "..") for part in name.split("/"))
            or path.as_posix() != name
            or not (name.startswith(PREFIXES) or name == "sql/schema.sql")
            or name.casefold() in names
        ):
            raise Rejected("runtime_manifest_path")
        if (
            type(size) is not int
            or not 0 <= size <= MAX_RESOURCE
            or not isinstance(digest, str)
            or re.fullmatch("[a-f0-9]{64}", digest) is None
        ):
            raise Rejected("runtime_manifest_identity")
        total += size
        if total > MAX_TOTAL:
            raise Rejected("runtime_manifest_total")
        selected = root.joinpath(*path.parts)
        if (
            selected.stat().st_size != size
            or file_hash(selected, MAX_RESOURCE) != digest
        ):
            raise Rejected("runtime_resource_identity")
        names.add(name.casefold())
    if {name.casefold() for name in ENTRYPOINTS.values()} - names:
        raise Rejected("runtime_entrypoint_missing")
    if {name.casefold() for name in REQUIRED_DATA} - names:
        raise Rejected("runtime_required_data_missing")
    return value


def command(component: str, root: Path, state: Path, port: int) -> list[str]:
    """Only fixed bundled programs/argv are selectable; no system PATH lookup or shell text is involved."""
    if component not in ENTRYPOINTS or type(port) is not int or not 1 <= port <= 65535:
        raise Rejected("native_component_or_port")
    validate(root)
    executable = str(root / ENTRYPOINTS[component])
    if component == "java":
        return [
            executable,
            "-XX:-UsePerfData",
            "-Djava.io.tmpdir=" + str(state),
            "-cp",
            str(root / "runtime/java-classes"),
            "JavaService",
            str(port),
        ]
    if component == "session":
        return [executable, str(root / "runtime/session/SessionLab.dll"), str(port)]
    if component == "php":
        return [
            executable,
            "-n",
            "-d",
            "display_errors=0",
            "-d",
            "extension_dir=" + str(root / "runtime/php/ext"),
            "-d",
            "extension=php_pdo_sqlite.dll",
            "-S",
            "127.0.0.1:" + str(port),
            str(root / "services/php/router.php"),
        ]
    return [executable, str(root / "services/node/server.mjs"), str(port)]


def environment(state: Path) -> dict[str, str]:
    """Clear provider keys, runtime injection/config variables and user PATH before an authored disposable service starts."""
    result = {
        key: os.environ[key]
        for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP")
        if key in os.environ
    }
    result.update(
        {
            "PATH": str(Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "System32"),
            "ASRL_PHP_DB": str(state / "php.sqlite"),
            "DOTNET_EnableDiagnostics": "0",
            "DOTNET_ROLL_FORWARD": "Disable",
            "DOTNET_CLI_HOME": str(state),
            "DOTNET_MULTILEVEL_LOOKUP": "0",
            "HOME": str(state),
            "USERPROFILE": str(state),
        }
    )
    return result
