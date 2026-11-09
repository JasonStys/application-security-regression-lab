"""Jason Stys: independent regression cohort/status oracles and exact source/output boundaries."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: case — line 46
# parameter: content — line 46
# parameter: name — line 46
# parameter: status — line 46
# definition: write — line 58
# parameter: cases — line 58
# parameter: path — line 58
# definition: test_all_transitions_and_bytes — line 69
# parameter: tmp_path — line 69
# variable: before — line 71
# variable: after — line 79
# variable: a — line 88
# variable: b — line 88
# variable: original — line 89
# variable: result — line 90
# variable: r — line 91
# variable: candidate — line 104
# variable: r — line 108
# definition: test_closed_bounded_inputs — line 113
# parameter: tmp_path — line 113
# variable: p — line 115
# variable: content — line 116
# definition: test_safe_export_and_main — line 128
# parameter: tmp_path — line 128
# variable: p — line 130
# variable: out — line 131
# variable: result — line 132
# variable: before — line 136
# END CODE MAP

import copy
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from asrl.compare import compare, load, main, publish, unique
from asrl.evidence import LabError


def case(name, status=403, content=True):
    """Return independent synthetic status/content evidence for comparison fixtures."""
    return {
        "id": name,
        "component": "node",
        "expected": 403,
        "observed": status,
        "content_ok": content,
        "elapsed_ms": 1.0,
    }


def write(path, cases):
    """Write a strict fixture, not a claim of live service execution."""
    path.write_text(
        json.dumps(
            {"schema": 1, "source": "uncommitted", "note": "fictional", "cases": cases}
        ),
        encoding="utf-8",
    )
    return path


def test_all_transitions_and_bytes(tmp_path: Path):
    """Removed/changed/new cases cannot inflate improvement; content failures count even at matching status."""
    before = [
        case("PASS"),
        case("FAIL", 200),
        case("RECOVER", 200),
        case("REGRESS"),
        case("MISSING"),
        case("CHANGE"),
    ]
    after = [
        case("PASS"),
        case("FAIL", 200),
        case("RECOVER"),
        case("REGRESS", 403, False),
        case("CHANGE"),
        case("NEW"),
    ]
    after[-2]["expected"] = 200
    a, b = write(tmp_path / "a.json", before), write(tmp_path / "b.json", after)
    original = a.read_bytes(), b.read_bytes()
    result = compare(a, b)
    assert {r["case_id"]: r["state"] for r in result["cases"]} == {
        "PASS": "STILL_PASS",
        "FAIL": "STILL_FAIL",
        "RECOVER": "RECOVERED",
        "REGRESS": "REGRESSION",
        "MISSING": "NOT_EXECUTED",
        "CHANGE": "ASSERTION_CHANGED",
        "NEW": "NEW_CASE",
    }
    assert result["review_queue"] == ["CHANGE", "FAIL", "MISSING", "NEW", "REGRESS"]
    assert result["baseline_sha256"] == hashlib.sha256(original[0]).hexdigest()
    assert (a.read_bytes(), b.read_bytes()) == original
    assert result == compare(a, b)
    candidate = copy.deepcopy(after)
    candidate[-2]["component"] = "java"
    write(b, candidate)
    assert (
        next(r for r in compare(a, b)["cases"] if r["case_id"] == "CHANGE")["state"]
        == "ASSERTION_CHANGED"
    )


def test_closed_bounded_inputs(tmp_path: Path):
    """Oversize, duplicate shadow keys, missing ordinary files and invalid reports cannot be silently compared."""
    p = tmp_path / "input.json"
    for content in (b"x" * 1_048_577, b'{"schema":1,"schema":1}', b"{}", b"\xff"):
        p.write_bytes(content)
        with pytest.raises((ValueError, UnicodeError)):
            load(p)
    with pytest.raises(LabError):
        load(tmp_path)
    with pytest.raises(LabError):
        unique([("a", 1), ("a", 2)])
    with patch.object(Path, "is_symlink", return_value=True), pytest.raises(LabError):
        load(p)


def test_safe_export_and_main(tmp_path: Path):
    """CLI comparison preserves old files; HTML escapes content and rejects linked destinations."""
    p = write(tmp_path / "a.json", [case("ONE")])
    out = tmp_path / "review"
    result = compare(p, p)
    result["scope"] = "<script>private</script>"
    publish(result, out)
    assert "&lt;script&gt;" in (out / "comparison.html").read_text(encoding="utf-8")
    before = (out / "comparison.json").read_bytes()
    with pytest.raises(FileExistsError):
        publish(result, out)
    assert (out / "comparison.json").read_bytes() == before
    with patch.object(Path, "is_junction", return_value=True), pytest.raises(LabError):
        publish(result, tmp_path / "linked")
    with patch.object(
        sys, "argv", ["compare", str(p), str(p), "--output", str(tmp_path / "cli")]
    ):
        assert main() == 0
    with patch.object(sys, "argv", ["compare", str(p), str(p), "--output", str(out)]):
        assert main() == 2
