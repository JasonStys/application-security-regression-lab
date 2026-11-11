"""Jason Stys: private-state/link/action-pin and test-only-vulnerable-comparison confinement checks."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 51
# variable: PUBLICATION_PATHS — line 52
# variable: MAX_XML_BYTES — line 56
# variable: MAX_PACKAGE_BYTES — line 57
# definition: publication_text — line 60
# parameter: path — line 60
# variable: flags — line 62
# variable: source — line 63
# variable: metadata — line 64
# definition: _word_xml — line 70
# parameter: source — line 70
# variable: archive — line 72
# variable: entries — line 73
# variable: item — line 76
# variable: item — line 77
# variable: item — line 83
# variable: result — line 87
# variable: item — line 88
# variable: stream — line 92
# variable: payload — line 93
# definition: public_text — line 100
# parameter: path — line 100
# definition: main — line 107
# variable: names — line 109
# variable: name — line 115
# variable: path — line 116
# variable: text — line 122
# variable: target — line 125
# variable: action — line 131
# variable: word — line 135
# variable: frontend — line 146
# variable: word — line 149
# variable: package — line 151
# variable: value — line 154
# variable: lock — line 156
# variable: name — line 157
# variable: value — line 157
# END CODE MAP

import json
import os
import re
import stat
import subprocess
from pathlib import Path
from typing import BinaryIO
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_PATHS = {
    "docs/reports/project-guide.docx",
    "docs/reports/windows-application-guide-1.1.0.docx",
}
MAX_XML_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_BYTES = 20 * 1024 * 1024


def publication_text(path: Path) -> str:
    """Read bounded non-macro Word XML for the existing secret scan; reject malformed packages."""
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as source:
        metadata = os.fstat(source.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_PACKAGE_BYTES:
            raise ValueError("Word package must be a bounded regular file")
        return _word_xml(source)


def _word_xml(source: BinaryIO) -> str:
    """Inspect bounded opened ZIP bytes without reopening a different path identity."""
    with ZipFile(source) as archive:
        entries = archive.infolist()
        if (
            len(entries) > 512
            or len({item.filename for item in entries}) != len(entries)
            or sum(item.file_size for item in entries) > 16 * 1024 * 1024
            or "word/document.xml" not in archive.namelist()
            or any(
                item.flag_bits & 1
                or "vbaproject" in item.filename.lower()
                or "/embeddings/" in item.filename.lower()
                for item in entries
            )
        ):
            raise ValueError("Invalid or oversized Word documentation package")
        result = []
        for item in entries:
            if item.filename.endswith((".xml", ".rels")):
                if item.file_size > MAX_XML_BYTES:
                    raise ValueError("Word XML exceeds its declared byte budget")
                with archive.open(item) as stream:
                    payload = stream.read(MAX_XML_BYTES + 1)
                if len(payload) > MAX_XML_BYTES or len(payload) != item.file_size:
                    raise ValueError("Word XML exceeds its actual byte budget")
                result.append(payload.decode("utf-8", errors="strict"))
        return "\n".join(result)


def public_text(path: Path) -> str:
    """Expose XML only for exact reviewed editions; unknown binary names retain strict UTF-8 failure."""
    if path.relative_to(ROOT).as_posix() in PUBLICATION_PATHS:
        return publication_text(path)
    return path.read_text(encoding="utf-8", errors="strict")


def main() -> None:
    """Verify repository boundaries and exact pins, not a complete application-security certification."""
    names = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    for name in names:
        path = ROOT / name
        assert path.is_file()
        assert not name.startswith(
            ("out/", "dist/", "node_modules/", ".venv/", ".tools/")
        )
        assert not re.search(r"/(?:bin|obj)/|\.(?:sqlite|db|env)(?:$|[.-])", name)
        text = public_text(path)
        assert not re.search(r"(?:ghp_|github_pat_)[A-Za-z0-9]{20,}", text)
        if name.endswith(".md"):
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if not target.startswith(("https:", "http:", "#", "mailto:")):
                    assert (path.parent / target.split("#")[0]).resolve().is_file(), (
                        "Broken link " + name + ": " + target
                    )
        if name.startswith(".github/workflows/"):
            for action in re.findall(r"uses:\s*([^\s#]+)", text):
                assert re.fullmatch(r"[\w/.-]+@[a-f0-9]{40}", action)
                assert not any(
                    word in action
                    for word in (
                        "upload-artifact",
                        "download-artifact",
                        "actions/cache",
                    )
                )
            assert "persist-credentials: false" in text
        if name.startswith(("services/", "web/")):
            assert not re.search(r"\b(?:require|import)\b.*tests[\\/]", text), (
                "Test-only code must never be served"
            )
    frontend = (ROOT / "web/app.ts").read_text() + (ROOT / "web/text.ts").read_text()
    assert not any(
        word in frontend
        for word in ("innerHTML", "outerHTML", "insertAdjacentHTML", "eval(")
    )
    package = json.loads((ROOT / "package.json").read_text())
    assert all(
        re.fullmatch(r"\d+\.\d+\.\d+", value)
        for value in package["devDependencies"].values()
    )
    lock = json.loads((ROOT / "package-lock.json").read_text())
    assert all("integrity" in value for name, value in lock["packages"].items() if name)
    assert "--hash=sha256:" in (ROOT / "requirements-dev.lock").read_text()
    assert (
        json.loads((ROOT / "global.json").read_text())["sdk"]["rollForward"]
        == "disable"
    )
    print(
        "Private-state/link/pin/test-confinement gates: "
        + str(len(names))
        + " files passed"
    )


if __name__ == "__main__":
    main()
