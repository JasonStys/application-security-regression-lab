"""Actual inert developer-archive extraction and provider boundary regressions. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_actual_zip_extract_and_exact_reuse_without_overwrite — line 34
# parameter: tmp_path — line 34
# variable: archive — line 36
# variable: package — line 37
# variable: root — line 39
# definition: test_actual_zip_bad_path_refused — line 70
# parameter: name — line 70
# parameter: tmp_path — line 70
# variable: archive — line 72
# variable: package — line 73
# definition: test_actual_zip_case_alias_and_link_refused — line 88
# parameter: tmp_path — line 88
# variable: index — line 90
# variable: link — line 90
# variable: archive — line 91
# variable: package — line 92
# variable: row — line 94
# attribute: create_system — line 95
# attribute: external_attr — line 96
# definition: test_provider_urls_refuse_credentials_or_other_authority — line 115
# parameter: url — line 115
# END CODE MAP

import hashlib
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from scripts.prepare_native_sdks import checked_url, digest, unpack


def test_actual_zip_extract_and_exact_reuse_without_overwrite(tmp_path):
    """The authenticated-archive materializer preserves exact repeated bytes and refuses changed or extra SDK files."""
    archive = tmp_path / "inert.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as package:
        package.writestr("runtime/file.txt", b"inert SDK fixture")
    root = tmp_path / "sdk"
    unpack(archive, root)
    unpack(archive, root)
    assert (root / "runtime/file.txt").read_bytes() == b"inert SDK fixture"
    assert (
        digest(archive, "sha256", archive.stat().st_size)
        == hashlib.sha256(archive.read_bytes()).hexdigest()
    )
    (root / "extra.txt").write_bytes(b"retain")
    with pytest.raises(ValueError, match="unexpected"):
        unpack(archive, root)
    (root / "extra.txt").unlink()
    (root / "runtime/file.txt").write_bytes(b"changed")
    with pytest.raises(ValueError):
        unpack(archive, root)
    assert (root / "runtime/file.txt").read_bytes() == b"changed"


@pytest.mark.parametrize(
    "name",
    [
        "../outside",
        "/outside",
        "runtime/../outside",
        "runtime//outside",
        "runtime/CON.txt",
        "runtime/x:ads",
        "runtime\\outside",
        "runtime/x.",
    ],
)
def test_actual_zip_bad_path_refused(tmp_path, name):
    """No traversal, alternate stream or Windows device may be opened by a developer archive."""
    archive = tmp_path / "inert.zip"
    with ZipFile(archive, "w") as package:
        package.writestr(name.replace("\\", "/"), b"inert")
    if "\\" in name:
        # Windows ZipInfo normalizes its authoring input. Replace both actual
        # local/central filename bytes to construct the otherwise valid hazard.
        archive.write_bytes(
            archive.read_bytes().replace(
                name.replace("\\", "/").encode(), name.encode()
            )
        )
    with pytest.raises(ValueError):
        unpack(archive, tmp_path / "sdk")
    assert not (tmp_path / "outside").exists()


def test_actual_zip_case_alias_and_link_refused(tmp_path):
    """Case collisions and symlink member types fail independently of benign-looking payload bytes."""
    for index, link in enumerate((False, True)):
        archive = tmp_path / (str(index) + ".zip")
        with ZipFile(archive, "w") as package:
            if link:
                row = ZipInfo("runtime/link")
                row.create_system = 3
                row.external_attr = 0o120777 << 16
                package.writestr(row, "outside")
            else:
                package.writestr("runtime/a", "a")
                package.writestr("runtime/A", "b")
        with pytest.raises(ValueError):
            unpack(archive, tmp_path / ("sdk" + str(index)))


@pytest.mark.parametrize(
    "url",
    [
        "http://nodejs.org/file",
        "https://nodejs.org.evil.invalid/file",
        "https://user:secret@nodejs.org/file",
        "https://nodejs.org:444/file",
        "https://nodejs.org/file#fragment",
    ],
)
def test_provider_urls_refuse_credentials_or_other_authority(url):
    """Only official HTTPS archive providers are eligible; no browser/account credential is used."""
    with pytest.raises(ValueError):
        checked_url(url)
