"""Owned-pipe privacy/cap/drain and real PHP-capability handshake regressions. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_only_closed_loader_classes_escape — line 66
# parameter: expected — line 66
# parameter: text — line 66
# variable: diagnostic — line 68
# definition: test_real_owned_pipe_drains_beyond_retention_cap_without_blocking — line 76
# variable: command — line 78
# variable: process — line 84
# variable: diagnostic — line 88
# definition: test_reader_failure_and_stuck_owned_drain_remain_errors — line 102
# parameter: monkeypatch — line 102
# definition: Broken — line 105
# definition: read — line 108
# parameter: _count — line 108
# parameter: self — line 108
# variable: read1 — line 112
# variable: diagnostic — line 114
# definition: test_frozen_php_health_requires_actual_sqlite_and_drains_its_own_pipe — line 124
# parameter: capability — line 125
# parameter: monkeypatch — line 125
# parameter: tmp_path — line 125
# variable: calls — line 128
# parameter: _root — line 130
# parameter: _size — line 133
# variable: process — line 134
# parameter: _kwargs — line 142
# parameter: _args — line 145
# parameter: _kwargs — line 145
# variable: headers — line 147
# parameter: _args — line 156
# variable: port — line 161
# END CODE MAP

import io
import subprocess
import sys
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from asrl import native_runtime, transport
from asrl.evidence import LabError
from asrl.native_stderr import StartupDiagnostic


@pytest.mark.parametrize(
    "text,expected",
    [
        (b"ordinary log /private/fixture", "unclassified"),
        (b"unable to load dynamic library /private/fixture", "startup_other"),
        (
            b"unable to load dynamic library: The specified module could not be found",
            "module_missing",
        ),
        (
            b"unable to load dynamic library: The specified procedure could not be found",
            "procedure_missing",
        ),
        (b"unable to load dynamic library: not a valid Win32 application", "bad_image"),
        (b"unable to load dynamic library: Access is denied", "access_denied"),
        (b"unrelated The specified module could not be found", "unclassified"),
    ],
)
def test_only_closed_loader_classes_escape(text, expected):
    """Paths/bodies never enter the exposed value; an unrelated phrase is not treated as a PHP loader diagnostic."""
    diagnostic = StartupDiagnostic(io.BufferedReader(io.BytesIO(text)))
    diagnostic.thread.join(timeout=2)
    assert not diagnostic.thread.is_alive()
    assert diagnostic.category() == expected
    diagnostic.close()
    assert diagnostic.buffer == b""


def test_real_owned_pipe_drains_beyond_retention_cap_without_blocking():
    """An actual inert child emits well beyond pipe capacity; only the first 16 KiB is retained and no raw data is logged."""
    command = [
        sys.executable,
        "-I",
        "-c",
        "import sys;sys.stderr.buffer.write(b'unable to load dynamic library: The specified module could not be found\\n'+b'PRIVATE-INERT-'*20000)",
    ]
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    assert process.stderr is not None
    diagnostic = StartupDiagnostic(process.stderr)
    try:
        assert process.wait(timeout=5) == 0
        diagnostic.thread.join(timeout=2)
        assert not diagnostic.thread.is_alive()
        assert len(diagnostic.buffer) == 16384
        assert diagnostic.category() == "module_missing"
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        diagnostic.close()


def test_reader_failure_and_stuck_owned_drain_remain_errors(monkeypatch):
    """Diagnostic I/O cannot silently certify a healthy service or mask ownership failure as success."""

    class Broken(io.BytesIO):
        """A controlled read failure, containing text that must never be surfaced."""

        def read(self, _count):
            """Fail before returning any private bytes."""
            raise OSError("PRIVATE-INERT")

        read1 = read

    diagnostic = StartupDiagnostic(Broken())
    diagnostic.thread.join(timeout=2)
    with pytest.raises(LabError, match="owned_php_diagnostic_read"):
        diagnostic.close()
    monkeypatch.setattr(diagnostic.thread, "is_alive", lambda: True)
    with pytest.raises(LabError, match="owned_php_diagnostic_drain"):
        diagnostic.close()


@pytest.mark.parametrize("capability", ["available", "unavailable", None])
def test_frozen_php_health_requires_actual_sqlite_and_drains_its_own_pipe(
    tmp_path, monkeypatch, capability
):
    """A valid runtime/nonce/component still cannot admit a PHP server without its real SQLite driver."""
    calls = []
    monkeypatch.setattr(transport.sys, "frozen", True, raising=False)
    monkeypatch.setattr(native_runtime, "validate", lambda _root: {})
    monkeypatch.setattr(transport, "isolated_dll_search", nullcontext)
    monkeypatch.setattr(transport, "free_port", lambda: 12345)
    monkeypatch.setattr(transport.secrets, "token_hex", lambda _size: "a" * 64)
    process = SimpleNamespace(
        stderr=io.BufferedReader(
            io.BytesIO(
                b"unable to load dynamic library: The specified module could not be found"
            )
        ),
        poll=lambda: None,
        terminate=lambda: calls.append("terminate"),
        wait=lambda **_kwargs: calls.append("wait"),
    )
    monkeypatch.setattr(
        transport.subprocess, "Popen", lambda *_args, **_kwargs: process
    )
    headers = {
        "x-lab-component": "php",
        "x-lab-owned-nonce": "a" * 64,
        "x-lab-runtime": "8.5.12",
        "x-lab-sqlite": capability,
    }
    monkeypatch.setattr(
        transport,
        "request",
        lambda *_args: (200, headers, b'{"component":"php","synthetic":true}', 0),
    )
    if capability == "available":
        with transport.service(
            "php", tmp_path, tmp_path, _direct_frozen_php=True
        ) as port:
            assert port == 12345
    else:
        with (
            pytest.raises(LabError, match="owned_php_driver_"),
            transport.service("php", tmp_path, tmp_path, _direct_frozen_php=True),
        ):
            pytest.fail("missing capability must not yield")
    assert calls == ["terminate", "wait"]
    assert process.stderr.closed
