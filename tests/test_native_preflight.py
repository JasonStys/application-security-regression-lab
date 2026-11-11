"""Native builder preflight false-pass controls; actual PHP execution remains the separate native gate. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_preflight_requires_complete_status_and_content_oracles — line 28
# parameter: fault — line 29
# parameter: monkeypatch — line 29
# parameter: tmp_path — line 29
# definition: owned — line 34
# parameter: component — line 34
# parameter: root — line 34
# parameter: state — line 34
# variable: _ — line 40
# variable: rows — line 40
# parameter: component — line 50
# parameter: port — line 50
# END CODE MAP

from contextlib import contextmanager

import pytest

from asrl import cases, transport
from scripts.build_native import verify_php_http


@pytest.mark.parametrize(
    "fault", [None, "wrong-status", "wrong-content", "missing-case", "extra-case"]
)
def test_preflight_requires_complete_status_and_content_oracles(
    tmp_path, monkeypatch, fault
):
    """A successful child/health endpoint alone cannot admit missing or failing original HTTP cases."""

    @contextmanager
    def owned(component, root, state):
        """Control only the fixture boundary; record lifetime and verify a fresh builder-owned state directory."""
        assert component == "php" and root == tmp_path
        assert state.parent == tmp_path and state.is_dir()
        yield 12345

    rows = [{"observed": 200, "expected": 200, "content_ok": True} for _ in range(24)]
    if fault == "wrong-status":
        rows[-1]["observed"] = 500
    elif fault == "wrong-content":
        rows[-1]["content_ok"] = False
    elif fault == "missing-case":
        rows.pop()
    elif fault == "extra-case":
        rows.append(dict(rows[-1]))
    monkeypatch.setattr(transport, "service", owned)
    monkeypatch.setattr(cases, "exercise", lambda component, port: rows)
    if fault is None:
        verify_php_http(tmp_path, tmp_path)
    else:
        with pytest.raises(ValueError, match="status/content"):
            verify_php_http(tmp_path, tmp_path)
    assert not list(tmp_path.iterdir())
