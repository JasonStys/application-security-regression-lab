"""Jason Stys: validated expected/observed security evidence, honest verdicts and inert HTML summaries."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: COMPONENTS — line 40
# variable: MAX_RESPONSE — line 41
# definition: LabError — line 44
# definition: canonical — line 48
# parameter: value — line 48
# definition: decode — line 55
# parameter: data — line 55
# definition: validate — line 65
# parameter: value — line 65
# variable: ids — line 82
# variable: case — line 83
# variable: field — line 107
# variable: timing — line 110
# definition: passed — line 123
# parameter: case — line 123
# definition: render — line 128
# parameter: value — line 128
# variable: report — line 130
# variable: cells — line 131
# variable: case — line 132
# variable: item — line 137
# variable: case — line 148
# variable: total — line 148
# variable: name — line 161
# definition: fingerprint — line 176
# parameter: value — line 176
# END CODE MAP

from __future__ import annotations

import hashlib
import html
import json
import math
import re
from typing import Any

COMPONENTS = {"java", "session", "php", "node"}
MAX_RESPONSE = 32768


class LabError(ValueError):
    """Fixed safe categories; never echo tokens, body content, SQL, paths or private machine details."""


def canonical(value: object) -> bytes:
    """Serialize deterministic finite evidence, not executable scripts or external resources."""
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")
    ).encode()


def decode(data: bytes) -> Any:
    """Decode bounded UTF8 response JSON and normalize all parsing failures to one safe error."""
    if len(data) > MAX_RESPONSE:
        raise LabError("response_size")
    try:
        return json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError):
        raise LabError("response_json") from None


def validate(value: object) -> dict[str, Any]:
    """Check exact result structure and derive verdict; reported success cannot contradict observed results."""
    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "source", "note", "cases"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
    ):
        raise LabError("report_schema")
    if not isinstance(value["source"], str) or not re.fullmatch(
        "[a-f0-9]{40}|uncommitted", value["source"]
    ):
        raise LabError("source_id")
    if not isinstance(value["note"], str) or len(value["note"]) > 1000:
        raise LabError("report_note")
    if not isinstance(value["cases"], list) or not 1 <= len(value["cases"]) <= 500:
        raise LabError("report_count")
    ids = set()
    for case in value["cases"]:
        if not isinstance(case, dict) or set(case) != {
            "id",
            "component",
            "expected",
            "observed",
            "content_ok",
            "elapsed_ms",
        }:
            raise LabError("case_schema")
        if (
            not isinstance(case["id"], str)
            or not re.fullmatch("[A-Z][A-Z0-9-]{0,79}", case["id"])
            or case["id"] in ids
        ):
            raise LabError("case_id")
        ids.add(case["id"])
        if (
            not isinstance(case["component"], str)
            or case["component"] not in COMPONENTS
        ):
            raise LabError("case_component")
        if any(
            type(case[field]) is not int or not 100 <= case[field] <= 599
            for field in ("expected", "observed")
        ):
            raise LabError("case_status")
        timing = case["elapsed_ms"]
        if (
            isinstance(timing, bool)
            or not isinstance(timing, (int, float))
            or not 0 <= timing <= 60000
            or not math.isfinite(timing)
        ):
            raise LabError("case_timing")
        if type(case["content_ok"]) is not bool:
            raise LabError("case_content")
    return value


def passed(case: dict[str, Any]) -> bool:
    """Success requires both the exact expected HTTP status and evaluated response/content invariant."""
    return bool(case["expected"] == case["observed"] and case["content_ok"])


def render(value: object) -> str:
    """Render a strict report as standalone inert escaped HTML, with no JavaScript/external assets."""
    report = validate(value)
    cells = []
    for case in report["cases"]:
        cells.append(
            "<tr>"
            + "".join(
                "<td>" + html.escape(str(item)) + "</td>"
                for item in (
                    case["id"],
                    case["component"],
                    case["expected"],
                    case["observed"],
                    "PASS" if passed(case) else "FAIL",
                    case["elapsed_ms"],
                )
            )
            + "</tr>"
        )
    total = sum(passed(case) for case in report["cases"])
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>AppSec evidence · Jason Stys</title><h1>AppSec regression evidence</h1><p>Created by Jason Stys. '
        + str(total)
        + " / "
        + str(len(cells))
        + " passed.</p><p>"
        + html.escape(report["note"])
        + "</p><p>Source: "
        + html.escape(report["source"])
        + "</p><table><caption>Exact expected versus observed status plus content invariant</caption><tr>"
        + "".join(
            '<th scope="col">' + name + "</th>"
            for name in (
                "Case",
                "Component",
                "Expected",
                "Observed",
                "Verdict",
                "Latency ms",
            )
        )
        + "</tr>"
        + "".join(cells)
        + "</table></html>"
    )


def fingerprint(value: object) -> str:
    """Bind the validated result bytes; a SHA256 is not a signature or certification."""
    return hashlib.sha256(canonical(validate(value))).hexdigest()
