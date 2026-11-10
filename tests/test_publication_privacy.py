"""Jason Stys: credentials in actual Word XML remain visible to repository privacy checks."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_word_xml_remains_visible_to_secret_scan — line 23
# parameter: tmp_path — line 23
# variable: path — line 25
# variable: archive — line 26
# variable: text — line 29
# definition: test_unsupported_word_packages_fail_closed — line 38
# parameter: kind — line 38
# parameter: tmp_path — line 38
# variable: path — line 40
# variable: archive — line 41
# END CODE MAP

import re
from zipfile import ZipFile

import pytest

from scripts.validate_repo import publication_text


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
