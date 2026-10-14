"""Jason Stys: case generation/negative verdicts, actual Node/.NET fixtures and CLI evidence persistence."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_case_generation — line 60
# parameter: component — line 60
# parameter: monkeypatch — line 60
# variable: counter — line 62
# definition: respond — line 64
# parameter: args — line 64
# variable: counter — line 67
# variable: rows — line 81
# variable: row — line 83
# definition: test_bad_upload_evidence — line 91
# parameter: monkeypatch — line 91
# parameter: args — line 93
# definition: test_cookie_security_verdict — line 99
# parameter: monkeypatch — line 99
# parameter: secure — line 99
# definition: respond — line 102
# parameter: args — line 102
# variable: rows — line 118
# variable: issued — line 119
# variable: row — line 119
# definition: test_actual_node — line 123
# parameter: tmp_path — line 123
# variable: port — line 125
# variable: rows — line 126
# variable: row — line 127
# definition: test_cli — line 130
# parameter: capsys — line 130
# parameter: monkeypatch — line 130
# parameter: tmp_path — line 130
# variable: report — line 133
# variable: row — line 134
# parameter: args — line 138
# definition: test_cli_all_and_link — line 153
# parameter: monkeypatch — line 153
# parameter: tmp_path — line 153
# definition: owned — line 158
# parameter: args — line 158
# parameter: component — line 165
# parameter: port — line 165
# parameter: self — line 177
# parameter: args — line 181
# parameter: kwargs — line 181
# variable: _ — line 181
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
