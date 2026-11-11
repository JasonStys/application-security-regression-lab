"""Jason Stys: case generation/negative verdicts, actual Node/.NET fixtures and CLI evidence persistence."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_case_generation — line 65
# parameter: component — line 65
# parameter: monkeypatch — line 65
# variable: counter — line 67
# definition: respond — line 69
# parameter: args — line 69
# variable: counter — line 72
# variable: rows — line 86
# variable: row — line 88
# definition: test_bad_upload_evidence — line 96
# parameter: monkeypatch — line 96
# parameter: args — line 98
# definition: test_cookie_security_verdict — line 104
# parameter: monkeypatch — line 104
# parameter: secure — line 104
# definition: respond — line 107
# parameter: args — line 107
# variable: rows — line 123
# variable: issued — line 124
# variable: row — line 124
# definition: test_actual_node — line 128
# parameter: tmp_path — line 128
# variable: port — line 130
# variable: rows — line 131
# variable: row — line 132
# definition: test_cli — line 135
# parameter: capsys — line 135
# parameter: monkeypatch — line 135
# parameter: tmp_path — line 135
# variable: report — line 138
# variable: row — line 139
# parameter: args — line 143
# definition: test_cli_all_and_link — line 158
# parameter: monkeypatch — line 158
# parameter: tmp_path — line 158
# definition: owned — line 163
# parameter: args — line 163
# parameter: component — line 170
# parameter: port — line 170
# parameter: self — line 182
# parameter: args — line 186
# parameter: kwargs — line 186
# variable: _ — line 186
# definition: test_php_failure_transport_uses_only_closed_nonprivate_categories — line 197
# parameter: category — line 198
# parameter: expected — line 198
# parameter: monkeypatch — line 198
# parameter: _args — line 204
# END CODE MAP

import json
import subprocess
from pathlib import Path

import pytest

from asrl import cases, transport
from asrl.__main__ import ROOT, main
from asrl.evidence import LabError, passed, validate


@pytest.mark.parametrize("component", ["java", "session", "php", "node"])
def test_case_generation(monkeypatch, component):
    """Mock transport only to test deterministic case construction; contradictory outcomes must remain failures."""
    counter = 0

    def respond(*args):
        """Return deliberately incomplete content rather than a canned all-pass simulation."""
        nonlocal counter
        counter += 1
        return (
            200,
            {
                "x-lab-component": component,
                "cache-control": "no-store",
                "x-content-type-options": "nosniff",
                "set-cookie": "lab_session=unique" + str(counter),
            },
            b'{"id":"0123456789abcdef","synthetic":true}',
            1,
        )

    monkeypatch.setattr(cases, "request", respond)
    rows = cases.exercise(component, 12345)
    assert len(rows) >= 10
    assert not all(passed(row) for row in rows)
    assert validate(
        dict(schema=1, source="uncommitted", note="construction only", cases=rows)
    )
    with pytest.raises(LabError, match="component"):
        cases.exercise("unknown", 12345)


def test_bad_upload_evidence(monkeypatch):
    """Malformed native upload evidence must fail, not be reused as an arbitrary downstream request path."""
    monkeypatch.setattr(cases, "request", lambda *args: (200, {}, b"{}", 1))
    with pytest.raises(LabError, match="upload_evidence"):
        cases.exercise("php", 12345)


@pytest.mark.parametrize("secure", [False, True])
def test_cookie_security_verdict(monkeypatch, secure):
    """Missing Secure must fail the HTTP evidence predicate; transport mocks do not certify native issuance."""

    def respond(*args):
        """Return synthetic issuance headers with one controlled security-attribute difference."""
        return (
            200,
            {
                "x-lab-component": "session",
                "cache-control": "no-store",
                "x-content-type-options": "nosniff",
                "set-cookie": "lab_session=synthetic; HttpOnly; SameSite=Strict; Path=/; Max-Age=120"
                + ("; Secure" if secure else ""),
            },
            b'{"synthetic":true}',
            1,
        )

    monkeypatch.setattr(cases, "request", respond)
    rows = cases.exercise("session", 12345)
    issued = next(row for row in rows if row["id"] == "SESSION-ISSUE")
    assert passed(issued) is secure


def test_actual_node(tmp_path):
    """Run the actual corrected native Node adapter, not a mock, through its whole HTTP case catalog."""
    with transport.service("node", ROOT, tmp_path) as port:
        rows = cases.exercise("node", port)
    assert all(passed(row) for row in rows)


def test_cli(tmp_path, monkeypatch, capsys):
    """The shipped entrypoint persists actual loopback evidence and refuses overwrites of existing result directories."""
    assert main(["--component", "node", "--output", str(tmp_path / "actual")]) == 0
    report = json.loads((tmp_path / "actual/http.json").read_text())
    assert len(report["cases"]) >= 10 and all(passed(row) for row in report["cases"])
    assert main(["--component", "node", "--output", str(tmp_path / "actual")]) == 2
    monkeypatch.setattr(
        "asrl.__main__.exercise",
        lambda *args: [
            dict(
                id="NODE-SYNTHETIC-FAIL",
                component="node",
                expected=403,
                observed=200,
                content_ok=True,
                elapsed_ms=1,
            )
        ],
    )
    assert main(["--component", "node", "--output", str(tmp_path / "failed")]) == 1
    assert "PRIVATE" not in capsys.readouterr().out


def test_cli_all_and_link(tmp_path, monkeypatch):
    """Exercise explicit all-component orchestration without claiming mocked cases validate native languages."""
    from contextlib import contextmanager

    @contextmanager
    def owned(*args):
        """Provide an isolated deterministic port only for orchestration-control tests."""
        yield 12345

    monkeypatch.setattr("asrl.__main__.service", owned)
    monkeypatch.setattr(
        "asrl.__main__.exercise",
        lambda component, port: [
            dict(
                id=component.upper() + "-TEST",
                component=component,
                expected=200,
                observed=200,
                content_ok=True,
                elapsed_ms=1,
            )
        ],
    )
    assert main(["--output", str(tmp_path / "all")]) == 0
    monkeypatch.setattr(Path, "is_symlink", lambda self: self.name == "linked")
    assert main(["--output", str(tmp_path / "linked")]) == 2
    monkeypatch.setattr(
        "asrl.__main__.subprocess.check_output",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.CalledProcessError(128, "git")
        ),
    )
    assert main(["--output", str(tmp_path / "no-commit")]) == 0


@pytest.mark.parametrize(
    "category,expected",
    [("database_8", "database_8"), ("private SQL C:/secret", "unclassified")],
)
def test_php_failure_transport_uses_only_closed_nonprivate_categories(
    monkeypatch, category, expected
):
    """Protocol plumbing never echoes a received private body/header; actual SQLite categories have separate PHP tests."""
    monkeypatch.setattr(
        cases,
        "request",
        lambda *_args: (
            500,
            {"x-lab-error-category": category},
            b'{"error":"local_operation_failed"}',
            0,
        ),
    )
    with pytest.raises(LabError, match="upload_evidence_500_" + expected + "$"):
        cases.exercise("php", 12345)
