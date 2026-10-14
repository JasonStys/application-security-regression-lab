"""Jason Stys: property and negative checks for truthful verdicts, strict reports and inert rendering."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: report — line 43
# definition: test_valid_report — line 62
# parameter: report — line 62
# variable: output — line 67
# definition: test_top_rejections — line 92
# parameter: field — line 92
# parameter: report — line 92
# parameter: value — line 92
# definition: test_case_rejections — line 122
# parameter: field — line 122
# parameter: report — line 122
# parameter: value — line 122
# definition: test_duplicate_missing — line 132
# parameter: report — line 132
# definition: test_verdict_truth — line 143
# parameter: content — line 143
# parameter: expected — line 143
# parameter: observed — line 143
# definition: test_response_decode — line 155
# parameter: data — line 155
# END CODE MAP

import copy

import pytest
from hypothesis import given
from hypothesis import strategies as st

from asrl.evidence import (
    LabError,
    canonical,
    decode,
    fingerprint,
    passed,
    render,
    validate,
)


@pytest.fixture
def report():
    """Build independent synthetic evidence, not a pre-recorded success asserted without evaluation."""
    return {
        "schema": 1,
        "source": "uncommitted",
        "note": "<script>synthetic</script>",
        "cases": [
            {
                "id": "NODE-ONE",
                "component": "node",
                "expected": 403,
                "observed": 403,
                "content_ok": True,
                "elapsed_ms": 1.25,
            }
        ],
    }


def test_valid_report(report):
    """Verify successful evidence is deterministic, hash-bound and inert while contradictory evidence remains failed."""
    assert validate(report) is report
    assert canonical(report) == canonical(copy.deepcopy(report))
    assert fingerprint(report) == fingerprint(copy.deepcopy(report))
    output = render(report)
    assert "<script>" not in output and "&lt;script&gt;" in output
    assert "1 / 1 passed" in output
    report["cases"][0]["observed"] = 200
    assert not passed(report["cases"][0])
    assert "FAIL" in render(report)
    report["cases"][0].update(observed=403, content_ok=False)
    assert not passed(report["cases"][0])
    assert "0 / 1 passed" in render(report)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", True),
        ("schema", 2),
        ("source", None),
        ("source", "../x"),
        ("note", None),
        ("note", "x" * 1001),
        ("cases", []),
        ("cases", {}),
        ("cases", [{}] * 501),
    ],
)
def test_top_rejections(report, field, value):
    """Reject incompatible, oversized or misleading report headers and source references."""
    report[field] = value
    with pytest.raises(LabError):
        validate(report)
    with pytest.raises(LabError):
        validate([])
    with pytest.raises(LabError):
        validate({**report, "extra": 1})


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "bad id"),
        ("id", 1),
        ("component", "unknown"),
        ("component", []),
        ("expected", True),
        ("expected", 99),
        ("observed", 600),
        ("content_ok", 1),
        ("elapsed_ms", True),
        ("elapsed_ms", -1),
        ("elapsed_ms", float("nan")),
        ("elapsed_ms", float("inf")),
        ("elapsed_ms", 60001),
        ("elapsed_ms", None),
    ],
)
def test_case_rejections(report, field, value):
    """Every verdict datum must be typed, finite, bounded and uniquely identified."""
    report["cases"][0][field] = value
    with pytest.raises(LabError):
        validate(report)
    report["cases"] = [None]
    with pytest.raises(LabError):
        validate(report)


def test_duplicate_missing(report):
    """Duplicate cases and omitted fields cannot inflate evidence counts or conceal results."""
    report["cases"] *= 2
    with pytest.raises(LabError, match="case_id"):
        validate(report)
    report["cases"] = [{}]
    with pytest.raises(LabError, match="case_schema"):
        validate(report)


@given(st.integers(100, 599), st.integers(100, 599), st.booleans())
def test_verdict_truth(expected, observed, content):
    """A pass is exactly status equality AND content invariant, never a permissive status class."""
    assert passed(
        {"expected": expected, "observed": observed, "content_ok": content}
    ) is (expected == observed and content)


@pytest.mark.parametrize(
    "data",
    [b"{", b"\xff", b"[" * 2000, b"x" * 32769],
    ids=["syntax", "utf8", "depth", "size"],
)
def test_response_decode(data):
    """Malformed/oversized transport evidence raises a safe category without raw input echo."""
    with pytest.raises(LabError):
        decode(data)
    assert decode(b'{"a":1}') == {"a": 1}
