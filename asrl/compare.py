"""Jason Stys: exact-byte regression run comparison; missing execution never becomes a pass."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: unique — line 60
# parameter: pairs — line 60
# variable: result — line 62
# variable: name — line 63
# variable: value — line 63
# definition: load — line 70
# parameter: path — line 70
# variable: p — line 74
# variable: stream — line 79
# variable: content — line 80
# definition: compare — line 86
# parameter: baseline — line 86
# parameter: candidate — line 86
# variable: before — line 88
# variable: before_bytes — line 88
# variable: after — line 89
# variable: after_bytes — line 89
# variable: case — line 90
# variable: old — line 90
# variable: case — line 91
# variable: new — line 91
# variable: rows — line 92
# variable: case_id — line 93
# variable: left — line 94
# variable: right — line 94
# variable: state — line 96
# variable: state — line 98
# variable: state — line 103
# variable: state — line 105
# variable: state — line 107
# variable: state — line 109
# variable: queue — line 113
# variable: row — line 115
# definition: publish — line 132
# parameter: output — line 132
# parameter: result — line 132
# variable: target — line 134
# variable: p — line 135
# variable: page — line 137
# definition: main — line 147
# variable: parser — line 149
# variable: args — line 155
# variable: result — line 157
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any

from .evidence import LabError, canonical, passed, validate


def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject shadowed report keys instead of silently comparing a chosen last value."""
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise LabError("duplicate_report_key")
        result[name] = value
    return result


def load(path: Path) -> tuple[bytes, dict[str, Any]]:
    """Read at most one MiB from an ordinary nonlinked report; do not execute or fetch anything."""
    if any(
        p.is_symlink() or p.is_junction()
        for p in (path.absolute(), *path.absolute().parents)
    ):
        raise LabError("linked_input")
    if not path.is_file():
        raise LabError("ordinary_report_required")
    with path.open("rb") as stream:
        content = stream.read(1_048_577)
    if len(content) > 1_048_576:
        raise LabError("report_size")
    return content, validate(json.loads(content, object_pairs_hook=unique))


def compare(baseline: Path, candidate: Path) -> dict[str, Any]:
    """Compare the union of exact case IDs; changed component/expected status invalidates direct verdict comparison."""
    before_bytes, before = load(baseline)
    after_bytes, after = load(candidate)
    old = {case["id"]: case for case in before["cases"]}
    new = {case["id"]: case for case in after["cases"]}
    rows = []
    for case_id in sorted(old.keys() | new.keys()):
        left, right = old.get(case_id), new.get(case_id)
        if left is None:
            state = "NEW_CASE"
        elif right is None:
            state = "NOT_EXECUTED"
        elif (left["component"], left["expected"]) != (
            right["component"],
            right["expected"],
        ):
            state = "ASSERTION_CHANGED"
        elif passed(left) and not passed(right):
            state = "REGRESSION"
        elif not passed(left) and passed(right):
            state = "RECOVERED"
        else:
            state = "STILL_PASS" if passed(right) else "STILL_FAIL"
        rows.append(
            {"case_id": case_id, "state": state, "baseline": left, "candidate": right}
        )
    queue = [
        row["case_id"]
        for row in rows
        if row["state"] not in ("STILL_PASS", "RECOVERED")
    ]
    return {
        "schema": 1,
        "author": "Jason Stys",
        "kind": "regression_run_comparison",
        "baseline_sha256": hashlib.sha256(before_bytes).hexdigest(),
        "candidate_sha256": hashlib.sha256(after_bytes).hexdigest(),
        "baseline_source": before["source"],
        "candidate_source": after["source"],
        "cases": rows,
        "review_queue": queue,
        "scope": "HTTP status/content invariants only. Missing cases are unexecuted, new/changed assertions need review. Latencies are observations, not comparable benchmarks. Case labels do not authenticate test implementation equivalence. Native core/browser gates remain separate.",
    }


def publish(result: dict[str, Any], output: Path) -> None:
    """Create new exact-scope JSON and escaped network-inert review page without replacing existing evidence."""
    target = output.absolute()
    if any(p.is_symlink() or p.is_junction() for p in (target, *target.parents)):
        raise LabError("linked_output")
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>Regression review — Jason Stys</title><main><h1>Regression run review</h1><p>Created by Jason Stys</p><pre>'
        + html.escape(json.dumps(result, indent=2))
        + "</pre></main></html>"
    )
    target.mkdir(mode=0o700)
    (target / "comparison.json").write_bytes(canonical(result))
    (target / "comparison.html").write_text(page, encoding="utf-8")


def main() -> int:
    """Compare explicit saved reports locally; a review queue is data, while invalid inputs return nonzero."""
    parser = argparse.ArgumentParser(
        description="Jason Stys — local HTTP regression report comparison"
    )
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = compare(args.baseline, args.candidate)
        publish(result, args.output)
        print(
            json.dumps(
                {
                    "cases": len(result["cases"]),
                    "review_items": len(result["review_queue"]),
                }
            )
        )
        return 0
    except (OSError, ValueError, UnicodeError, RecursionError):
        print("Rejected: invalid_or_existing_comparison_input_output")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
