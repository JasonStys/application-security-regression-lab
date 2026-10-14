"""Jason Stys: private-state/link/action-pin and test-only-vulnerable-comparison confinement checks."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 26
# definition: main — line 29
# variable: names — line 31
# variable: name — line 37
# variable: path — line 38
# variable: text — line 44
# variable: target — line 47
# variable: action — line 53
# variable: word — line 57
# variable: frontend — line 68
# variable: word — line 71
# variable: package — line 73
# variable: value — line 76
# variable: lock — line 78
# variable: name — line 79
# variable: value — line 79
# END CODE MAP

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
        text = path.read_text(encoding="utf-8")
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
