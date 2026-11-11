"""Jason Stys: actual loopback sockets plus isolated lifecycle failure/timeout/no-external-target tests."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Fixture — line 70
# definition: do_GET — line 73
# parameter: self — line 73
# variable: data — line 75
# definition: log_message — line 81
# parameter: args — line 81
# parameter: self — line 81
# definition: test_actual_transport — line 85
# variable: server — line 87
# variable: thread — line 88
# variable: body — line 93
# variable: headers — line 93
# variable: latency — line 93
# variable: status — line 93
# definition: test_no_external_target — line 119
# parameter: path — line 119
# parameter: port — line 119
# definition: test_commands_and_failure — line 125
# parameter: monkeypatch — line 125
# parameter: tmp_path — line 125
# variable: component — line 127
# definition: broken — line 132
# parameter: args — line 132
# parameter: kwargs — line 132
# variable: error — line 137
# definition: test_owned_lifecycle — line 143
# parameter: mode — line 143
# parameter: monkeypatch — line 143
# parameter: tmp_path — line 143
# variable: calls — line 145
# definition: wait — line 147
# parameter: timeout — line 147
# variable: process — line 153
# parameter: args — line 159
# parameter: kwargs — line 159
# parameter: _ — line 161
# variable: times — line 162
# definition: reply — line 165
# parameter: args — line 165
# variable: port — line 181
# definition: test_free_port — line 191
# definition: test_frozen_service_binds_exact_nonce_runtime_and_program — line 197
# parameter: monkeypatch — line 198
# parameter: runtime — line 198
# parameter: tmp_path — line 198
# variable: calls — line 203
# parameter: _root — line 205
# parameter: _ — line 207
# definition: launched — line 210
# parameter: argv — line 210
# parameter: kwargs — line 210
# parameter: _kw — line 224
# parameter: _args — line 231
# variable: port — line 243
# END CODE MAP

import http.client
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

from asrl import transport as t
from asrl.evidence import LabError


class Fixture(BaseHTTPRequestHandler):
    """Serve only artificial response bytes to exercise the client boundary, not a security-service substitute."""

    def do_GET(self):
        """Return a controlled normal/over-cap response for genuine HTTP read tests."""
        data = b"x" * 32769 if self.path == "/large" else b"{}"
        self.send_response(200)
        self.send_header("X-Lab-Component", "fixture")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        """Suppress test-only request logs exactly as the owned runner avoids raw native output."""


def test_actual_transport():
    """Use real sockets, verify capped reads and latency; close the owned listener even on rejection."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        status, headers, body, latency = t.request(server.server_port, "/normal")
        assert (
            status == 200
            and body == b"{}"
            and headers["x-lab-component"] == "fixture"
            and latency >= 0
        )
        with pytest.raises(LabError, match="response_size"):
            t.request(server.server_port, "/large")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize(
    "port,path",
    [
        (0, "/"),
        (65536, "/"),
        (True, "/"),
        (1, "https://evil.invalid"),
        (1, "//evil.invalid"),
        (1, "/" + "x" * 16384),
    ],
)
def test_no_external_target(port, path):
    """No configuration can substitute an external host/protocol or overlong path into the transport."""
    with pytest.raises(LabError, match="loopback_request"):
        t.request(port, path)


def test_commands_and_failure(monkeypatch, tmp_path):
    """Native execution commands are fixed argument arrays, never user-defined shell text."""
    for component in ("java", "session", "php", "node"):
        assert t.command(component, tmp_path, tmp_path, 12345)[-1] != "evil.invalid"
    with pytest.raises(LabError, match="component"):
        t.command("unknown", tmp_path, tmp_path, 12345)

    def broken(*args, **kwargs):
        """Represent a connection failure whose arbitrary original message must remain private."""
        raise OSError("PRIVATE-COOKIE")

    monkeypatch.setattr(http.client.HTTPConnection, "request", broken)
    with pytest.raises(LabError, match="loopback_transport") as error:
        t.request(12345, "/")
    assert "PRIVATE" not in str(error.value)


@pytest.mark.parametrize("mode", ["ok", "exit", "wrong", "foreign", "timeout", "kill"])
def test_owned_lifecycle(monkeypatch, tmp_path, mode):
    """All startup/assertion/timeout paths terminate the exact owned child, and forced kill is bounded."""
    calls = []

    def wait(timeout):
        """Record waits and simulate a stuck process only on the first graceful-shutdown wait."""
        calls.append("wait")
        if mode == "kill" and calls.count("wait") == 1:
            raise t.subprocess.TimeoutExpired("owned", timeout)

    process = SimpleNamespace(
        poll=lambda: 1 if mode == "exit" else None,
        terminate=lambda: calls.append("terminate"),
        wait=wait,
        kill=lambda: calls.append("kill"),
    )
    monkeypatch.setattr(t.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(t, "free_port", lambda: 12345)
    monkeypatch.setattr(t.secrets, "token_hex", lambda _: "a" * 64)
    times = iter([0, 16])
    monkeypatch.setattr(t.time, "monotonic", lambda: next(times))

    def reply(*args):
        """Simulate handshake outcomes only; actual native services are validated separately by integration CI."""
        if mode in ("timeout", "kill"):
            raise LabError("loopback_transport")
        return (
            200,
            {
                "x-lab-component": "wrong" if mode == "wrong" else "node",
                "x-lab-owned-nonce": "b" * 64 if mode == "foreign" else "a" * 64,
            },
            b'{"component":"node","synthetic":true}',
            0,
        )

    monkeypatch.setattr(t, "request", reply)
    if mode == "ok":
        with t.service("node", tmp_path, tmp_path) as port:
            assert port == 12345
    else:
        with pytest.raises(LabError), t.service("node", tmp_path, tmp_path):
            pytest.fail("unverified service must not yield")
    assert "terminate" in calls and "wait" in calls
    if mode == "kill":
        assert "kill" in calls


def test_free_port():
    """Allocate only numeric-loopback ephemeral ports, not an externally selected target."""
    assert 1 <= t.free_port() <= 65535


@pytest.mark.parametrize("runtime", ["v24.22.1", "v24.18.1", None])
def test_frozen_service_binds_exact_nonce_runtime_and_program(
    tmp_path, monkeypatch, runtime
):
    """Frozen wiring must use bundled argv, minimal environment and actual runtime header, never user PATH/provider state."""
    from asrl import native_runtime

    calls = []
    monkeypatch.setattr(t.sys, "frozen", True, raising=False)
    monkeypatch.setattr(native_runtime, "validate", lambda _root: {})
    monkeypatch.setattr(t, "free_port", lambda: 12345)
    monkeypatch.setattr(t.secrets, "token_hex", lambda _: "a" * 64)
    monkeypatch.setenv("NODE_OPTIONS", "--eval=private-fixture")

    def launched(argv, **kwargs):
        """Require fixed bundled argv and cleared injection environment before returning an inert owned-process fixture."""
        assert argv == [
            str(tmp_path / "runtime/node/node.exe"),
            str(tmp_path / "services/node/server.mjs"),
            "12345",
        ]
        assert (
            "NODE_OPTIONS" not in kwargs["env"]
            and kwargs["env"]["ASRL_OWNED_NONCE"] == "a" * 64
        )
        return SimpleNamespace(
            poll=lambda: None,
            terminate=lambda: calls.append("terminate"),
            wait=lambda **_kw: calls.append("wait"),
        )

    monkeypatch.setattr(t.subprocess, "Popen", launched)
    monkeypatch.setattr(
        t,
        "request",
        lambda *_args: (
            200,
            {
                "x-lab-component": "node",
                "x-lab-owned-nonce": "a" * 64,
                "x-lab-runtime": runtime,
            },
            b'{"component":"node","synthetic":true}',
            0,
        ),
    )
    if runtime == "v24.22.1":
        with t.service("node", tmp_path, tmp_path) as port:
            assert port == 12345
    else:
        with (
            pytest.raises(LabError, match="runtime_identity"),
            t.service("node", tmp_path, tmp_path),
        ):
            pytest.fail("wrong/unknown runtime cannot be admitted")
    assert calls == ["terminate", "wait"]
