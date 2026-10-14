"""Jason Stys: explicit owned numeric-loopback request/process lifecycle, no external-target scan interface."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: request — line 52
# parameter: port — line 53
# parameter: path — line 54
# parameter: method — line 55
# parameter: body — line 56
# parameter: headers — line 57
# variable: started — line 68
# variable: connection — line 69
# variable: response — line 72
# variable: raw — line 73
# variable: name — line 78
# variable: value — line 78
# definition: free_port — line 88
# variable: descriptor — line 90
# definition: command — line 95
# parameter: component — line 95
# parameter: port — line 95
# parameter: root — line 95
# parameter: state — line 95
# variable: commands — line 99
# definition: service — line 120
# parameter: component — line 120
# parameter: root — line 120
# parameter: state — line 120
# variable: port — line 122
# variable: environment — line 123
# variable: process — line 124
# variable: deadline — line 134
# variable: _ — line 139
# variable: headers — line 139
# variable: raw — line 139
# variable: status — line 139
# variable: value — line 140
# END CODE MAP

from __future__ import annotations

import http.client
import os
import socket
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .evidence import COMPONENTS, MAX_RESPONSE, LabError, decode


def request(
    port: int,
    path: str,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes, float]:
    """Request only numeric loopback, bounded response/time; private response text is never used as error details."""
    if (
        type(port) is not int
        or not 1 <= port <= 65535
        or not path.startswith("/")
        or path.startswith("//")
        or len(path) > 16384
    ):
        raise LabError("loopback_request")
    started = time.perf_counter()
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise LabError("response_size")
        return (
            response.status,
            {name.lower(): value for name, value in response.getheaders()},
            raw,
            round((time.perf_counter() - started) * 1000, 3),
        )
    except (OSError, http.client.HTTPException):
        raise LabError("loopback_transport") from None
    finally:
        connection.close()


def free_port() -> int:
    """Reserve/release a numeric-loopback port; the following owned-process handshake mitigates accidental port reuse."""
    with socket.socket() as descriptor:
        descriptor.bind(("127.0.0.1", 0))
        return int(descriptor.getsockname()[1])


def command(component: str, root: Path, state: Path, port: int) -> list[str]:
    """Select one fixed native adapter. No shell interpolation, caller URL or arbitrary executable command."""
    if component not in COMPONENTS:
        raise LabError("component")
    commands = {
        "java": ["java", "-cp", str(root / "out/java"), "JavaService", str(port)],
        "session": [
            "dotnet",
            str(root / "services/session/bin/Release/net10.0/SessionLab.dll"),
            str(port),
        ],
        "php": [
            "php",
            "-d",
            "display_errors=0",
            "-S",
            "127.0.0.1:" + str(port),
            str(root / "services/php/router.php"),
        ],
        "node": ["node", str(root / "services/node/server.mjs"), str(port)],
    }
    return commands[component]


@contextmanager
def service(component: str, root: Path, state: Path) -> Iterator[int]:
    """Start only an owned synthetic process, verify its component, and stop it even if assertions fail."""
    port = free_port()
    environment = {**os.environ, "ASRL_PHP_DB": str(state / "php.sqlite")}
    process = subprocess.Popen(
        command(component, root, state, port),
        cwd=root,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        deadline = time.monotonic() + 15
        while True:
            if process.poll() is not None:
                raise LabError("owned_service_exited")
            try:
                status, headers, raw, _ = request(port, "/health")
                value = decode(raw)
                if (
                    status == 200
                    and headers.get("x-lab-component") == component
                    and value == {"component": component, "synthetic": True}
                ):
                    break
                raise LabError("owned_service_identity")
            except LabError as error:
                if str(error) != "loopback_transport":
                    raise
            if time.monotonic() >= deadline:
                raise LabError("owned_service_timeout")
            time.sleep(0.05)
        yield port
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
