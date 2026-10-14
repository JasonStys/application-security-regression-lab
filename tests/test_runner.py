"""Jason Stys: case generation/negative verdicts, actual Node/.NET fixtures and CLI evidence persistence."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_case_generation — line 52
# parameter: component — line 52
# parameter: monkeypatch — line 52
# variable: counter — line 54
# definition: respond — line 56
# parameter: args — line 56
# variable: counter — line 59
# variable: rows — line 73
# variable: row — line 75
# definition: test_bad_upload_evidence — line 83
# parameter: monkeypatch — line 83
# parameter: args — line 85
# definition: test_actual_node — line 90
# parameter: tmp_path — line 90
# variable: port — line 92
# variable: rows — line 93
# variable: row — line 94
# definition: test_cli — line 97
# parameter: capsys — line 97
# parameter: monkeypatch — line 97
# parameter: tmp_path — line 97
# variable: report — line 100
# variable: row — line 101
# parameter: args — line 105
# definition: test_cli_all_and_link — line 120
# parameter: monkeypatch — line 120
# parameter: tmp_path — line 120
# definition: owned — line 125
# parameter: args — line 125
# parameter: component — line 132
# parameter: port — line 132
# parameter: self — line 144
# parameter: args — line 148
# parameter: kwargs — line 148
# variable: _ — line 148
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
