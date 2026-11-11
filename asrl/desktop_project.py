"""Real native HTTP regression execution and exact saved-report review for the desktop. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 94
# variable: PRODUCT — line 95
# variable: PROFILE — line 95
# variable: TITLE — line 99
# variable: VERSION — line 99
# variable: COLUMNS — line 100
# variable: RESOURCES — line 106
# variable: RESOURCE_LIMITS — line 115
# variable: MODES — line 116
# variable: REVIEW_MODE — line 121
# variable: CHOICES — line 122
# variable: FIELDS — line 123
# variable: ACTIVE_FIELDS — line 137
# variable: SCENARIOS — line 142
# variable: HELP — line 152
# definition: scenario — line 157
# parameter: name — line 157
# variable: index — line 161
# variable: result — line 162
# definition: report — line 178
# parameter: path — line 178
# variable: raw — line 180
# definition: bundle — line 184
# parameter: value — line 184
# variable: raw — line 186
# variable: page — line 187
# definition: analyze — line 195
# parameter: parameters — line 196
# parameter: stage — line 196
# parameter: state — line 196
# variable: mode — line 199
# variable: component — line 203
# variable: identity — line 206
# variable: rows — line 207
# variable: selected — line 208
# variable: port — line 212
# variable: category — line 215
# variable: category — line 217
# variable: value — line 219
# variable: matching — line 229
# variable: row — line 229
# variable: files — line 230
# variable: context — line 234
# variable: raw — line 243
# variable: value — line 243
# variable: matching — line 244
# variable: row — line 244
# variable: result — line 245
# variable: _ — line 257
# variable: before_raw — line 257
# variable: _ — line 258
# variable: after_raw — line 258
# variable: after — line 261
# variable: before — line 261
# variable: result — line 264
# definition: views — line 272
# parameter: files — line 272
# variable: value — line 275
# variable: row — line 279
# variable: item — line 282
# variable: key — line 282
# variable: value — line 285
# variable: saved — line 287
# variable: row — line 291
# variable: item — line 294
# variable: key — line 294
# variable: row — line 300
# variable: item — line 303
# variable: key — line 303
# definition: cells — line 308
# parameter: row — line 308
# definition: outcome — line 319
# parameter: value — line 319
# END CODE MAP

from __future__ import annotations

import hashlib
import html
import re
import sys
from pathlib import Path
from typing import Any

from . import compare, evidence
from .cases import exercise
from .desktop_io import Rejected, canonical, json_value
from .desktop_state import Workspace, package_identity
from .inputs import read_source
from .transport import service

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = (
    "application-security-regression-lab",
    "ApplicationSecurityRegressionLab",
)
TITLE, VERSION = "Application Security Regression Workbench", "1.1.0"
COLUMNS = (
    "Case / component",
    "Expected / baseline",
    "Observed / candidate",
    "Verdict / review",
)
RESOURCES = (
    "sql/schema.sql",
    "examples/desktop/baseline.json",
    "examples/desktop/candidate.json",
    "runtime-manifest.json",
    "notices.txt",
    "app.ico",
    "python314.dll",
)
RESOURCE_LIMITS: dict[str, int] = {}
MODES = (
    "Run real owned service regressions",
    "Review supplied HTTP evidence",
    "Compare saved regression reports",
)
REVIEW_MODE = None
CHOICES = {"component": ("all", "java", "session", "php", "node")}
FIELDS = (
    (
        "component",
        "Select authored native service suite (no external target)",
        "choice",
    ),
    (
        "report",
        "Authorized saved HTTP report JSON (data, not executable tests)",
        "file",
    ),
    ("baseline", "Earlier saved HTTP report JSON", "file"),
    ("candidate", "Candidate saved HTTP report JSON", "file"),
)
ACTIVE_FIELDS = {
    MODES[0]: ("component",),
    MODES[1]: ("report",),
    MODES[2]: ("baseline", "candidate"),
}
SCENARIOS = (
    "All four actual native HTTP suites",
    "Java tenant and stale-write boundaries",
    "C# session creation, expiry and logout",
    "PHP SQL and literal attachment boundaries",
    "Node fixture HTTP and output headers",
    "Review fictional baseline evidence",
    "Review fictional candidate mismatches",
    "Compare fictional release regression cohort",
)
HELP = """Run the original actual native Java, C#, PHP and Node HTTP conformance against this application's own disposable numeric-loopback services. Choose one suite or all four. The portable application bundles the runtimes; no compiler, external target, provider account or arbitrary test script is accepted. Synthetic fixture identities exist only inside those disposable services and are not real account authentication.
Review your supported saved report JSON or compare two reports. Reports are data: imported labels and source strings do not prove that tests executed, that two implementations match, or that an application is secure. The prepared comparison reports are clearly fictional inputs inside this same application. The comparison preserves missing/new/changed assertions and exact input hashes; a removed case never becomes a recovered pass. Status and content invariants both matter. Latencies are observations, not comparable performance benchmarks.
Filter and inspect literal per-case results, reopen durable owner-local plaintext history, and export exact saved files. No output, session cookie, provider key or uploaded document is sent elsewhere. This application is a local reference workbench, not a vulnerability scanner, production identity service or certification. Original native core tests and real browser DOM/accessibility tests remain separate mandatory source gates. Close waits for the retained analysis and owned service cleanup; it never abandons an in-flight history write."""


def scenario(name: str) -> dict[str, str]:
    """Populate ordinary editable controls; selecting a scenario never executes or claims a passing test."""
    if name not in SCENARIOS:
        raise Rejected("unknown_prepared_scenario")
    index = SCENARIOS.index(name)
    result = {
        "mode": MODES[0],
        "component": CHOICES["component"][index] if index < 5 else "all",
        "report": str(ROOT / "examples/desktop/baseline.json"),
        "baseline": str(ROOT / "examples/desktop/baseline.json"),
        "candidate": str(ROOT / "examples/desktop/candidate.json"),
    }
    if index in (5, 6):
        result["mode"] = MODES[1]
        if index == 6:
            result["report"] = result["candidate"]
    elif index == 7:
        result["mode"] = MODES[2]
    return result


def report(path: Path) -> tuple[bytes, dict[str, Any]]:
    """Read one exact bounded stable ordinary report; duplicate keys/nonfinite JSON cannot select another meaning."""
    raw = read_source(path, 1_048_576)
    return raw, evidence.validate(json_value(raw))


def bundle(value: dict[str, Any]) -> dict[str, bytes]:
    """Retain finite JSON and inert escaped HTML; report text is never evaluated as a script or plugin."""
    raw = canonical(value)
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>AppSec review — Jason Stys</title><h1>AppSec review</h1><p>Created by Jason Stys. Imported evidence is not authenticated execution.</p><pre>'
        + html.escape(raw.decode())
        + "</pre></html>"
    )
    return {"review.json": raw, "review.html": page.encode()}


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Invoke original core conformance/comparison with fixed runtimes or read authorized data; never execute user input."""
    mode = parameters.get("mode", "")
    if mode not in MODES:
        raise Rejected("unsupported_offline_operation")
    if mode == MODES[0]:
        component = parameters.get("component", "")
        if component not in CHOICES["component"]:
            raise Rejected("unknown_authored_component")
        identity = package_identity(ROOT, PRODUCT, VERSION, RESOURCES, RESOURCE_LIMITS)
        rows = []
        for selected in (
            sorted(evidence.COMPONENTS) if component == "all" else [component]
        ):
            try:
                with service(selected, ROOT, stage) as port:
                    rows.extend(exercise(selected, port))
            except evidence.LabError as error:
                category = str(error)
                if re.fullmatch("[a-z0-9_]{1,80}", category) is None:
                    category = "request_failed"
                raise Rejected(selected + "_" + category) from None
        value = evidence.validate(
            {
                "schema": 1,
                "source": identity["source"]
                if identity["source"] != "development"
                else "uncommitted",
                "note": "Actual owned-loopback authored service HTTP conformance. Synthetic fixture identities only; native core and real browser DOM/accessibility checks remain separate. No external target accepted.",
                "cases": rows,
            }
        )
        matching = sum(evidence.passed(row) for row in rows)
        files = {
            "http.json": evidence.canonical(value),
            "http.html": evidence.render(value).encode(),
        }
        context = stage / "php-runtime-context.json"
        if getattr(sys, "frozen", False) and context.exists():
            files["php-runtime-context.json"] = read_source(context, 65536)
        return (
            mode,
            f"{matching}/{len(rows)} actual HTTP status/content oracles match; {len(rows) - matching} mismatches retained",
            files,
        )
    if mode == MODES[1]:
        raw, value = report(Path(parameters["report"]))
        matching = sum(evidence.passed(row) for row in value["cases"])
        result: dict[str, Any] = {
            "schema": 1,
            "kind": "supplied_http_evidence_review",
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "report": value,
            "scope": "Supplied data only; labels/source strings do not authenticate execution. Exact original report bytes are retained separately.",
        }
        return (
            mode,
            f"{matching}/{len(value['cases'])} supplied status/content outcomes match; imported, not executed",
            {**bundle(result), "supplied-http.json": raw},
        )
    before_raw, _ = report(Path(parameters["baseline"]))
    after_raw, _ = report(Path(parameters["candidate"]))
    # Compare stable private copies so retained digests bind the same bytes that
    # the original comparator evaluates, including late source-file changes.
    before, after = stage / "baseline.json", stage / "candidate.json"
    before.write_bytes(before_raw)
    after.write_bytes(after_raw)
    result = compare.compare(before, after)
    return (
        mode,
        f"{len(result['review_queue'])}/{len(result['cases'])} case IDs need review; no missing execution counted as recovery",
        {**bundle(result), "baseline.json": before_raw, "candidate.json": after_raw},
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Keep all executed/imported outcomes, mismatches and comparison denominator distinctions visible."""
    if "http.json" in files:
        value = evidence.validate(json_value(files["http.json"]))
        return {
            "Actual HTTP cases": value["cases"],
            "Actual oracle mismatches": [
                row for row in value["cases"] if not evidence.passed(row)
            ],
            "Execution scope": [
                {key: item for key, item in value.items() if key != "cases"}
            ],
        }
    value = json_value(files["review.json"])
    if value["kind"] == "supplied_http_evidence_review":
        saved = evidence.validate(value["report"])
        return {
            "Supplied case outcomes (not executed)": saved["cases"],
            "Supplied mismatches": [
                row for row in saved["cases"] if not evidence.passed(row)
            ],
            "Supplied identity and scope": [
                {key: item for key, item in value.items() if key != "report"}
            ],
        }
    return {
        "All compared case IDs": value["cases"],
        "Case IDs needing review": [
            row for row in value["cases"] if row["case_id"] in value["review_queue"]
        ],
        "Exact comparison scope": [
            {key: item for key, item in value.items() if key != "cases"}
        ],
    }


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Expose exact expected/observed/content or original comparator state; unknown scope is not a pass."""
    if "expected" in row:
        return (
            str(row["id"]) + " / " + str(row["component"]),
            str(row["expected"]),
            str(row["observed"]) + " / content=" + str(row["content_ok"]),
            "PASS" if evidence.passed(row) else "MISMATCH",
        )
    if "case_id" in row:

        def outcome(value: dict[str, Any] | None) -> str:
            """Summarize exact per-side assertions; absent execution stays distinct from a pass."""
            if value is None:
                return "not executed"
            return (
                str(value["expected"])
                + " → "
                + str(value["observed"])
                + "; content="
                + str(value["content_ok"])
            )

        return (
            str(row["case_id"]),
            outcome(row["baseline"]),
            outcome(row["candidate"]),
            str(row["state"]),
        )
    return (
        "Review scope",
        "Exact input/source metadata",
        "Inspect selected record",
        "Not a verdict",
    )
