"""Jason Stys: actual loopback sockets plus isolated lifecycle failure/timeout/no-external-target tests."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Fixture — line 56
# definition: do_GET — line 59
# parameter: self — line 59
# variable: data — line 61
# definition: log_message — line 67
# parameter: args — line 67
# parameter: self — line 67
# definition: test_actual_transport — line 71
# variable: server — line 73
# variable: thread — line 74
# variable: body — line 79
# variable: headers — line 79
# variable: latency — line 79
# variable: status — line 79
# definition: test_no_external_target — line 105
# parameter: path — line 105
# parameter: port — line 105
# definition: test_commands_and_failure — line 111
# parameter: monkeypatch — line 111
# parameter: tmp_path — line 111
# variable: component — line 113
# definition: broken — line 118
# parameter: args — line 118
# parameter: kwargs — line 118
# variable: error — line 123
# definition: test_owned_lifecycle — line 129
# parameter: mode — line 129
# parameter: monkeypatch — line 129
# parameter: tmp_path — line 129
# variable: calls — line 131
# definition: wait — line 133
# parameter: timeout — line 133
# variable: process — line 139
# parameter: args — line 145
# parameter: kwargs — line 145
# variable: times — line 147
# definition: reply — line 150
# parameter: args — line 150
# variable: port — line 163
# definition: test_free_port — line 173
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


@pytest.mark.parametrize("mode", ["ok", "exit", "wrong", "timeout", "kill"])
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
    times = iter([0, 16])
    monkeypatch.setattr(t.time, "monotonic", lambda: next(times))

    def reply(*args):
        """Simulate handshake outcomes only; actual native services are validated separately by integration CI."""
        if mode in ("timeout", "kill"):
            raise LabError("loopback_transport")
        return (
            200,
            {"x-lab-component": "wrong" if mode == "wrong" else "node"},
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
