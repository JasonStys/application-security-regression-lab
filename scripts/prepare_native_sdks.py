"""Verify exact official Windows SDK archives and inert local extraction; never install globally. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 92
# variable: HOSTS — line 93
# definition: Redirect — line 102
# definition: redirect_request — line 105
# parameter: code — line 105
# parameter: fp — line 105
# parameter: headers — line 105
# parameter: message — line 105
# parameter: newurl — line 105
# parameter: request — line 105
# parameter: self — line 105
# definition: checked_url — line 111
# parameter: value — line 111
# variable: parsed — line 113
# definition: digest — line 126
# parameter: algorithm — line 126
# parameter: maximum — line 126
# parameter: path — line 126
# variable: descriptor — line 130
# variable: stream — line 137
# variable: info — line 138
# variable: checksum — line 145
# variable: total — line 145
# variable: chunk — line 146
# variable: total — line 147
# variable: after — line 151
# definition: download — line 161
# parameter: cache — line 161
# parameter: row — line 161
# variable: selected — line 163
# variable: request — line 165
# variable: deadline — line 169
# variable: total — line 169
# variable: response — line 173
# variable: stream — line 174
# variable: chunk — line 177
# variable: total — line 178
# definition: unpack — line 192
# parameter: archive — line 192
# parameter: target — line 192
# variable: package — line 194
# variable: entries — line 195
# variable: row — line 198
# variable: files — line 201
# variable: seen — line 201
# variable: row — line 202
# variable: name — line 207
# variable: part — line 208
# variable: reserved — line 209
# variable: item — line 216
# variable: kind — line 218
# variable: item — line 223
# variable: selected — line 236
# variable: item — line 239
# variable: expected — line 249
# variable: total — line 249
# variable: existing — line 250
# variable: source — line 251
# variable: chunk — line 253
# variable: total — line 254
# variable: output — line 259
# variable: chunk — line 260
# variable: total — line 261
# variable: actual — line 273
# variable: item — line 273
# definition: main — line 280
# variable: value — line 284
# variable: cache — line 294
# variable: destination — line 294
# variable: path — line 297
# variable: item — line 298
# variable: row — line 303
# variable: archive — line 317
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {
    "builds.dotnet.microsoft.com",
    "github.com",
    "release-assets.githubusercontent.com",
    "nodejs.org",
    "downloads.php.net",
}


class Redirect(urllib.request.HTTPRedirectHandler):
    """Follow only public HTTPS provider archive redirects; no credential or user-controlled host is accepted."""

    def redirect_request(self, request, fp, code, message, headers, newurl):
        """Validate each redirect authority before urllib can contact that public provider."""
        checked_url(newurl)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def checked_url(value: str) -> str:
    """Validate the fixed official provider boundary without logging signed redirect queries."""
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or parsed.fragment
    ):
        raise ValueError("SDK provider URL refused")
    return value


def digest(path: Path, algorithm: str, maximum: int) -> str:
    """Stream an ordinary one-link development archive through one descriptor with a hard byte bound."""
    if path.is_symlink() or path.is_junction():
        raise ValueError("Linked SDK archive refused")
    descriptor = os.open(
        path,
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_BINARY", 0),
    )
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_size > maximum
        ):
            raise ValueError("SDK archive type or size refused")
        checksum, total = hashlib.new(algorithm), 0
        while chunk := stream.read(1024 * 1024):
            total += len(chunk)
            if total > maximum:
                raise ValueError("SDK archive exceeds bound")
            checksum.update(chunk)
        after = os.fstat(stream.fileno())
        if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("SDK archive changed during hashing")
        return checksum.hexdigest()


def download(row: dict, cache: Path) -> Path:
    """Exclusively create a bounded archive or verify the existing one; unknown bytes are preserved and refused."""
    selected = cache / (row["name"] + ".zip")
    if not selected.exists():
        request = urllib.request.Request(
            checked_url(row["url"]),
            headers={"User-Agent": "JasonStys-AppSec-native-build"},
        )
        deadline, total = time.monotonic() + 300, 0
        with (
            urllib.request.build_opener(Redirect()).open(
                request, timeout=30
            ) as response,
            selected.open("xb") as stream,
        ):
            checked_url(response.url)
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > row["bytes"] or time.monotonic() > deadline:
                    raise ValueError("SDK download exceeded bound")
                stream.write(chunk)
    if (
        selected.stat().st_size != row["bytes"]
        or digest(selected, row["algorithm"], row["bytes"]) != row["digest"]
    ):
        raise ValueError(
            "Existing or downloaded SDK archive identity mismatch; preserve it for review"
        )
    return selected


def unpack(archive: Path, target: Path) -> None:
    """Admit closed ordinary ZIP entries and compare every existing SDK file to the authenticated archive before reuse."""
    with ZipFile(archive) as package:
        entries = package.infolist()
        if (
            not 1 <= len(entries) <= 50000
            or sum(row.file_size for row in entries) > 2 * 1024**3
        ):
            raise ValueError("SDK expansion bound")
        seen, files = set(), set()
        for row in entries:
            if row.orig_filename != row.filename:
                raise ValueError(
                    "SDK ZIP original filename was normalized or truncated"
                )
            name = row.filename.rstrip("/")
            part = PurePosixPath(name)
            reserved = any(
                re.fullmatch(
                    r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?",
                    item,
                    re.IGNORECASE,
                )
                or item.endswith((".", " "))
                for item in name.split("/")
            )
            kind = stat.S_IFMT(row.external_attr >> 16)
            if (
                not name
                or len(name) > 512
                or part.is_absolute()
                or any(item in ("", ".", "..") for item in name.split("/"))
                or "\\" in name
                or ":" in name
                or "\x00" in name
                or name.casefold() in seen
                or reserved
                or row.flag_bits & 1
                or row.compress_type not in (ZIP_STORED, ZIP_DEFLATED)
                or kind not in (0, stat.S_IFREG, stat.S_IFDIR)
                or row.file_size > 256 * 1024**2
            ):
                raise ValueError("SDK ZIP path/type identity refused")
            seen.add(name.casefold())
            selected = target.joinpath(*part.parts)
            if any(
                item.is_symlink() or item.is_junction()
                for item in (selected, *selected.parents)
            ):
                raise ValueError("SDK extraction link refused")
            if row.is_dir():
                selected.mkdir(parents=True, exist_ok=True)
                continue
            files.add(selected)
            selected.parent.mkdir(parents=True, exist_ok=True)
            # Read to EOF so ZipFile verifies the real CRC. Hash the verified
            # archive content and every existing selected SDK file independently.
            expected, total = hashlib.sha256(), 0
            existing = selected.exists()
            with package.open(row) as source:
                if existing:
                    while chunk := source.read(1024 * 1024):
                        total += len(chunk)
                        if total > row.file_size:
                            raise ValueError("SDK member growth")
                        expected.update(chunk)
                else:
                    with selected.open("xb") as output:
                        while chunk := source.read(1024 * 1024):
                            total += len(chunk)
                            if total > row.file_size:
                                raise ValueError("SDK member growth")
                            expected.update(chunk)
                            output.write(chunk)
            if (
                total != row.file_size
                or digest(selected, "sha256", row.file_size) != expected.hexdigest()
            ):
                raise ValueError(
                    "Extracted SDK bytes differ from authenticated archive"
                )
        actual = {item for item in target.rglob("*") if item.is_file()}
        if actual != files:
            raise ValueError(
                "SDK directory contains unexpected files; nothing was deleted"
            )


def main() -> None:
    """Prepare only exact source-locked public development SDKs below the ignored project tooling directory."""
    if sys.platform != "win32":
        raise RuntimeError("Windows native developer recipe required")
    value = json.loads((ROOT / "native-sdks.lock.json").read_text(encoding="utf-8"))
    if (
        set(value) != {"schema", "platform", "archives"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
        or value["platform"] != "windows-x86_64"
        or not isinstance(value["archives"], list)
        or len(value["archives"]) != 4
    ):
        raise ValueError("Closed SDK lock required")
    cache, destination = ROOT / ".tools/native-downloads", ROOT / ".tools/native-sdks"
    if any(
        item.is_symlink() or item.is_junction()
        for path in (cache, destination)
        for item in (path, *path.parents)
    ):
        raise ValueError("Linked SDK output directory refused")
    cache.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=True, exist_ok=True)
    for row in value["archives"]:
        if (
            set(row) != {"name", "url", "bytes", "algorithm", "digest"}
            or re.fullmatch(r"[a-z0-9.-]+", row["name"]) is None
            or type(row["bytes"]) is not int
            or not 1 <= row["bytes"] <= 512 * 1024**2
            or row["algorithm"] not in ("sha256", "sha512")
            or re.fullmatch(
                "[a-f0-9]{" + str(64 if row["algorithm"] == "sha256" else 128) + "}",
                row["digest"],
            )
            is None
        ):
            raise ValueError("SDK lock entry refused")
        archive = download(row, cache)
        unpack(archive, destination / row["name"])
        print(
            "Verified official SDK archive and exact extracted bytes: " + row["name"],
            flush=True,
        )


if __name__ == "__main__":
    main()
