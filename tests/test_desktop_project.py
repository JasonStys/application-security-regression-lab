"""Independent exact-report/cohort/user-control oracles; mocks do not establish actual native execution. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_fictional_review_and_full_comparison_cohort — line 56
# parameter: tmp_path — line 56
# variable: parameters — line 58
# variable: files — line 59
# variable: kind — line 59
# variable: summary — line 59
# variable: value — line 60
# variable: row — line 61
# variable: name — line 85
# variable: files — line 86
# variable: kind — line 86
# variable: summary — line 86
# variable: value — line 87
# variable: views — line 93
# definition: test_actual_execution_adapter_preserves_mismatches_and_uses_original_interfaces — line 104
# parameter: monkeypatch — line 105
# parameter: tmp_path — line 105
# variable: selected — line 108
# definition: owned — line 111
# parameter: component — line 111
# parameter: root — line 111
# parameter: stage — line 111
# definition: exercised — line 116
# parameter: component — line 116
# parameter: port — line 116
# variable: _ — line 132
# variable: files — line 132
# variable: summary — line 132
# variable: views — line 137
# definition: test_invalid_inputs_and_inert_report_text — line 152
# parameter: tmp_path — line 152
# variable: selected — line 164
# variable: files — line 168
# definition: test_service_failure_categories_are_component_scoped_and_value_free — line 182
# parameter: category — line 183
# parameter: expected — line 183
# parameter: monkeypatch — line 183
# parameter: tmp_path — line 183
# definition: stopped — line 187
# parameter: _args — line 187
# variable: result — line 192
# END CODE MAP

import hashlib
import json
from contextlib import contextmanager

import pytest

from asrl import desktop_project as project
from asrl.desktop_io import Rejected


def test_fictional_review_and_full_comparison_cohort(tmp_path):
    """The unchanged comparator must retain all seven dispositions, exact originals and honest imported scope."""
    parameters = project.scenario(project.SCENARIOS[-1])
    kind, summary, files = project.analyze(None, parameters, tmp_path)
    value = json.loads(files["review.json"])
    assert {row["case_id"]: row["state"] for row in value["cases"]} == {
        "ADDED": "NEW_CASE",
        "CHANGED": "ASSERTION_CHANGED",
        "MISSING": "NOT_EXECUTED",
        "PERSISTENT": "STILL_FAIL",
        "RECOVERED": "RECOVERED",
        "REGRESSED": "REGRESSION",
        "STABLE": "STILL_PASS",
    }
    assert value["review_queue"] == [
        "ADDED",
        "CHANGED",
        "MISSING",
        "PERSISTENT",
        "REGRESSED",
    ]
    assert len(project.views(files)["All compared case IDs"]) == 7
    assert (
        value["baseline_sha256"] == hashlib.sha256(files["baseline.json"]).hexdigest()
    )
    assert (
        value["candidate_sha256"] == hashlib.sha256(files["candidate.json"]).hexdigest()
    )
    assert "5/7" in summary and kind == project.MODES[2]
    for name in project.SCENARIOS[-3:-1]:
        kind, summary, files = project.analyze(None, project.scenario(name), tmp_path)
        value = json.loads(files["review.json"])
        assert "Fictional" in value["report"]["note"] and "not executed" in summary
        assert (
            value["input_sha256"]
            == hashlib.sha256(files["supplied-http.json"]).hexdigest()
        )
        views = project.views(files)
        assert len(views["Supplied case outcomes (not executed)"]) == 6
        assert len(views["Supplied mismatches"]) == (
            2 if name == project.SCENARIOS[-3] else 3
        )
        assert (
            project.cells(views["Supplied case outcomes (not executed)"][0])[3]
            == "PASS"
        )


def test_actual_execution_adapter_preserves_mismatches_and_uses_original_interfaces(
    tmp_path, monkeypatch
):
    """A mocked transport proves wiring only; a failed content invariant remains a failed outcome at matching status."""
    selected = []

    @contextmanager
    def owned(component, root, stage):
        """Observe selected fixed component names; this isolated adapter is not native execution proof."""
        selected.append(component)
        yield 12345

    def exercised(component, port):
        """Supply a known content mismatch to test preservation rather than fabricate all-success outcomes."""
        assert port == 12345
        return [
            {
                "id": component.upper() + "-CHECK",
                "component": component,
                "expected": 403,
                "observed": 403,
                "content_ok": component != "php",
                "elapsed_ms": 1.0,
            }
        ]

    monkeypatch.setattr(project, "service", owned)
    monkeypatch.setattr(project, "exercise", exercised)
    _, summary, files = project.analyze(
        None, project.scenario(project.SCENARIOS[0]), tmp_path
    )
    assert selected == ["java", "node", "php", "session"]
    assert "3/4" in summary and "1 mismatches" in summary
    views = project.views(files)
    assert len(views["Actual HTTP cases"]) == 4
    assert views["Actual oracle mismatches"][0]["component"] == "php"
    assert project.cells(views["Actual oracle mismatches"][0])[-1] == "MISMATCH"
    assert project.cells(
        {
            "case_id": "MISSING",
            "baseline": {"expected": 403, "observed": 403, "content_ok": True},
            "candidate": None,
            "state": "NOT_EXECUTED",
        }
    ) == ("MISSING", "403 → 403; content=True", "not executed", "NOT_EXECUTED")
    assert project.cells({"scope": "metadata"})[-1] == "Not a verdict"


def test_invalid_inputs_and_inert_report_text(tmp_path):
    """Malformed/ambiguous data or external-looking component names cannot execute a test or replace earlier evidence."""
    with pytest.raises(Rejected):
        project.scenario("arbitrary-command")
    with pytest.raises(Rejected):
        project.analyze(None, {"mode": "execute-shell"}, tmp_path)
    with pytest.raises(Rejected):
        project.analyze(
            None,
            {"mode": project.MODES[0], "component": "https://evil.invalid"},
            tmp_path,
        )
    selected = tmp_path / "ambiguous.json"
    selected.write_text('{"schema":1,"schema":2}')
    with pytest.raises(Rejected):
        project.report(selected)
    files = project.bundle({"label": "<script>alert(1)</script>"})
    assert (
        b"<script>" not in files["review.html"]
        and b"&lt;script&gt;" in files["review.html"]
    )


@pytest.mark.parametrize(
    "category,expected",
    [
        ("owned_service_exited", "java_owned_service_exited"),
        ("private fixture: do not echo", "java_request_failed"),
    ],
)
def test_service_failure_categories_are_component_scoped_and_value_free(
    tmp_path, monkeypatch, category, expected
):
    """A failed authored service cannot produce a partial passing report or expose arbitrary exception text."""

    def stopped(*_args):
        """Represent startup failure at the real context-manager call boundary without launching a program."""
        raise project.evidence.LabError(category)

    monkeypatch.setattr(project, "service", stopped)
    with pytest.raises(Rejected) as result:
        project.analyze(None, project.scenario(project.SCENARIOS[0]), tmp_path)
    assert str(result.value) == expected
    assert list(tmp_path.iterdir()) == []
