"""Exact admitted PHP closure in a nonce-owned per-analysis namespace, never arbitrary executables. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: PHP_FILES — line 55
# definition: PHPLaunch — line 69
# variable: arguments — line 72
# variable: environment — line 73
# variable: root — line 74
# variable: receipt — line 75
# definition: isolated_php — line 79
# parameter: original — line 79
# parameter: port — line 79
# parameter: state — line 79
# variable: manifest — line 84
# variable: original_manifest — line 85
# variable: inventory — line 88
# variable: row — line 88
# variable: parent — line 91
# variable: path — line 93
# variable: parent — line 96
# variable: selected — line 99
# variable: identity — line 100
# variable: nonce — line 101
# variable: marker — line 102
# variable: expected_marker — line 103
# variable: stream — line 106
# variable: name — line 110
# variable: row — line 111
# variable: raw — line 112
# variable: target — line 118
# variable: stream — line 120
# variable: copied — line 123
# variable: receipt — line 126
# variable: name — line 136
# variable: current — line 157
# END CODE MAP

from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .desktop_io import Rejected, canonical, json_value
from .inputs import read_source
from .native_runtime import environment, validate

PHP_FILES = (
    "runtime/php/php.exe",
    "runtime/php/php8.dll",
    "runtime/php/libsqlite3.dll",
    "runtime/php/ext/php_pdo_sqlite.dll",
    "runtime/php/vcruntime140.dll",
    "runtime/php/vcruntime140_1.dll",
    "services/php/router.php",
    "services/php/Store.php",
    "sql/schema.sql",
)


@dataclass(frozen=True)
class PHPLaunch:
    """Launch values derived only from a fully authenticated source bundle and this fresh owned namespace."""

    arguments: list[str]
    environment: dict[str, str]
    root: Path
    receipt: dict[str, Any]


@contextmanager
def isolated_php(original: Path, state: Path, port: int) -> Iterator[PHPLaunch]:
    """Authenticate the WHOLE bundle, copy/rebind fixed PHP files, retain ownership until the caller's child has exited."""
    if type(port) is not int or not 1 <= port <= 65535:
        raise Rejected("invalid owned PHP port")
    # Never admit a partial source inventory or accept caller-provided trust metadata.
    manifest = validate(original)
    original_manifest = read_source(original / "runtime-manifest.json", 2 * 1024 * 1024)
    if json_value(original_manifest) != manifest:
        raise Rejected("source runtime manifest changed after admission")
    inventory = {row["path"]: row for row in manifest["entries"]}
    if set(PHP_FILES) - inventory.keys():
        raise Rejected("fixed PHP runtime closure is incomplete")
    parent = state.absolute()
    if any(
        path.is_symlink() or path.is_junction() for path in (parent, *parent.parents)
    ):
        raise Rejected("linked owned PHP state directory")
    parent = parent.resolve()
    if not parent.is_dir() or parent.is_relative_to(original.resolve()):
        raise Rejected("owned PHP state must be outside bundled resources")
    selected = Path(tempfile.mkdtemp(prefix="owned-php-runtime-", dir=parent))
    identity = selected.stat()
    nonce = secrets.token_hex(32)
    marker = selected / "owned-runtime.json"
    expected_marker = canonical(
        {"schema": 1, "product": "asrl-owned-php-runtime", "nonce": nonce}
    )
    with marker.open("xb") as stream:
        os.chmod(marker, 0o600)
        stream.write(expected_marker)
    try:
        for name in PHP_FILES:
            row = inventory[name]
            raw = read_source(original / name, 32 * 1024 * 1024)
            if (
                len(raw) != row["bytes"]
                or hashlib.sha256(raw).hexdigest() != row["sha256"]
            ):
                raise Rejected("admitted PHP source changed before copying")
            target = selected / name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with target.open("xb") as stream:
                os.chmod(target, 0o600)
                stream.write(raw)
            copied = read_source(target, 32 * 1024 * 1024)
            if copied != raw:
                raise Rejected("owned PHP copy identity failed")
        receipt = {
            "schema": 1,
            "namespace": "fresh-owned-outside-frozen-extraction",
            "source_manifest_sha256": hashlib.sha256(original_manifest).hexdigest(),
            "files": [
                {
                    "path": name,
                    "bytes": inventory[name]["bytes"],
                    "sha256": inventory[name]["sha256"],
                }
                for name in PHP_FILES
            ],
            "scope": "Exact original whole-bundle admission, then same-byte fixed PHP closure copy. No caller executable, user PATH or trust metadata; this is not proof of a Windows loader root cause.",
        }
        yield PHPLaunch(
            [
                str(selected / "runtime/php/php.exe"),
                "-n",
                "-d",
                "display_errors=0",
                "-d",
                "extension=" + str(selected / "runtime/php/ext/php_pdo_sqlite.dll"),
                "-S",
                "127.0.0.1:" + str(port),
                str(selected / "services/php/router.php"),
            ],
            environment(state, selected, "php"),
            selected,
            receipt,
        )
    finally:
        current = selected.lstat()
        if (
            not stat.S_ISDIR(current.st_mode)
            or selected.is_symlink()
            or selected.is_junction()
            or (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino)
            or selected.resolve().parent != parent
            or not selected.name.startswith("owned-php-runtime-")
            or read_source(marker, 4096) != expected_marker
        ):
            raise Rejected("owned PHP cleanup identity changed")
        # Parent/caller must stop and wait for its exact child before leaving this context.
        # No separately discovered directory, PID, profile or service is cleaned up.
        shutil.rmtree(selected)
