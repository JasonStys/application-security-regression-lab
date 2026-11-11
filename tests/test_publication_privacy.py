"""Jason Stys: credentials in actual Word XML remain visible to repository privacy checks."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_package_descriptor_budget_precedes_zip_directory_read — line 59
# parameter: tmp_path — line 59
# variable: path — line 61
# variable: stream — line 62
# definition: test_current_exact_edition_retains_xml_visibility — line 68
# parameter: monkeypatch — line 68
# parameter: tmp_path — line 68
# variable: path — line 71
# variable: archive — line 73
# variable: text — line 76
# variable: unknown — line 78
# definition: test_actual_deflate_api_is_bounded_even_when_headers_understate_size — line 84
# parameter: monkeypatch — line 85
# parameter: tmp_path — line 85
# variable: path — line 88
# variable: archive — line 89
# variable: raw — line 91
# variable: central — line 92
# variable: original — line 96
# variable: observed — line 97
# definition: BoundedInflater — line 99
# definition: __init__ — line 102
# parameter: real — line 102
# parameter: self — line 102
# attribute: real — line 104
# definition: decompress — line 106
# parameter: data — line 106
# parameter: max_length — line 106
# parameter: self — line 106
# definition: __getattr__ — line 112
# parameter: name — line 112
# parameter: self — line 112
# parameter: method — line 117
# definition: test_word_xml_remains_visible_to_secret_scan — line 124
# parameter: tmp_path — line 124
# variable: path — line 126
# variable: archive — line 127
# variable: text — line 130
# definition: test_unsupported_word_packages_fail_closed — line 139
# parameter: kind — line 139
# parameter: tmp_path — line 139
# variable: path — line 141
# variable: archive — line 142
# END CODE MAP

import re
import struct
import zipfile
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

import pytest

from scripts import validate_repo as policy
from scripts.validate_repo import publication_text


def test_package_descriptor_budget_precedes_zip_directory_read(tmp_path):
    """A sparse oversized source is refused before ZIP parsing or expansion."""
    path = tmp_path / "guide.docx"
    with path.open("wb") as stream:
        stream.truncate(policy.MAX_PACKAGE_BYTES + 1)
    with pytest.raises(ValueError, match="bounded regular"):
        publication_text(path)


def test_current_exact_edition_retains_xml_visibility(tmp_path, monkeypatch):
    """The production selector inspects current XML and still rejects an arbitrary binary name."""
    monkeypatch.setattr(policy, "ROOT", tmp_path)
    path = tmp_path / "docs/reports/windows-application-guide-1.1.0.docx"
    path.parent.mkdir(parents=True)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", "<p>current-installed-marker</p>")
        archive.writestr("word/_rels/document.xml.rels", "<Relationships/>")
    text = policy.public_text(path)
    assert "current-installed-marker" in text and "Relationships" in text
    unknown = path.with_name("unknown-guide.docx")
    unknown.write_bytes(path.read_bytes())
    with pytest.raises(UnicodeDecodeError):
        policy.public_text(unknown)


def test_actual_deflate_api_is_bounded_even_when_headers_understate_size(
    tmp_path, monkeypatch
):
    """Genuine small dishonest ZIP bytes cannot cause an unbounded initial decompressor request."""
    path = tmp_path / "guide.docx"
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", b"x" * 65_536)
    raw = bytearray(path.read_bytes())
    central = raw.index(b"PK\x01\x02")
    struct.pack_into("<I", raw, 22, 1)
    struct.pack_into("<I", raw, central + 24, 1)
    path.write_bytes(raw)
    original = zipfile._get_decompressor
    observed = []

    class BoundedInflater:
        """Record the actual stdlib-to-zlib request while delegating real decompression."""

        def __init__(self, real):
            """Retain the genuine decompressor for delegated bounded inflation."""
            self.real = real

        def decompress(self, data, max_length=0):
            """Reject an unbounded call before delegating real small-fixture bytes."""
            observed.append(max_length)
            assert 0 < max_length <= policy.MAX_XML_BYTES + 1
            return self.real.decompress(data, max_length)

        def __getattr__(self, name):
            """Preserve normal zlib end-of-stream and tail behavior."""
            return getattr(self.real, name)

    monkeypatch.setattr(
        zipfile, "_get_decompressor", lambda method: BoundedInflater(original(method))
    )
    with pytest.raises((ValueError, BadZipFile)):
        policy.publication_text(path)
    assert observed


def test_word_xml_remains_visible_to_secret_scan(tmp_path):
    """Binary packaging cannot hide a synthetic token from the existing text credential pattern."""
    path = tmp_path / "guide.docx"
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", "<p>ghp_" + "z" * 24 + "</p>")
        archive.writestr("word/_rels/document.xml.rels", "<Relationships />")
    text = publication_text(path)
    assert re.search(r"ghp_[A-Za-z0-9]{20,}", text)
    assert "Relationships" in text


@pytest.mark.parametrize(
    "kind",
    ["missing-document", "macro", "embedded-package", "invalid-utf8", "oversized"],
)
def test_unsupported_word_packages_fail_closed(tmp_path, kind):
    """Unknown/malformed/macro and amplified packages do not become a skipped empty source."""
    path = tmp_path / "guide.docx"
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "word/document.xml" if kind != "missing-document" else "other.xml",
            b"\xff" if kind == "invalid-utf8" else b"<p>Owned fixture</p>",
        )
        if kind == "macro":
            archive.writestr("word/vbaProject.bin", b"not an executable macro")
        if kind == "embedded-package":
            archive.writestr("word/embeddings/inert.bin", b"synthetic inert package")
        if kind == "oversized":
            archive.writestr("word/oversized.xml", b"x" * (16 * 1024 * 1024 + 1))
    with pytest.raises((ValueError, UnicodeDecodeError)):
        publication_text(path)
