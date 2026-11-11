"""Jason Stys: explicit owned numeric-loopback request/process lifecycle, no external-target scan interface."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: request — line 59
# parameter: port — line 60
# parameter: path — line 61
# parameter: method — line 62
# parameter: body — line 63
# parameter: headers — line 64
# variable: started — line 75
# variable: connection — line 76
# variable: response — line 79
# variable: raw — line 80
# variable: name — line 85
# variable: value — line 85
# definition: free_port — line 95
# variable: descriptor — line 97
# definition: command — line 102
# parameter: component — line 102
# parameter: port — line 102
# parameter: root — line 102
# parameter: state — line 102
# variable: commands — line 110
# definition: service — line 131
# parameter: component — line 131
# parameter: root — line 131
# parameter: state — line 131
# variable: port — line 133
# variable: environment — line 137
# variable: environment — line 139
# variable: nonce — line 140
# variable: arguments — line 142
# variable: process — line 143
# variable: process — line 146
# variable: deadline — line 155
# variable: _ — line 160
# variable: headers — line 160
# variable: raw — line 160
# variable: status — line 160
# variable: value — line 161
# END CODE MAP

from __future__ import annotations

import http.client
import os
import secrets
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .evidence import COMPONENTS, MAX_RESPONSE, LabError, decode
from .native_spawn import isolated_dll_search


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
    if getattr(sys, "frozen", False):
        from .native_runtime import command as bundled_command

        return bundled_command(component, root, state, port)
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
    if getattr(sys, "frozen", False):
        from .native_runtime import environment as bundled_environment

        environment = bundled_environment(state, root, component)
    else:
        environment = {**os.environ, "ASRL_PHP_DB": str(state / "php.sqlite")}
    nonce = secrets.token_hex(32)
    environment["ASRL_OWNED_NONCE"] = nonce
    arguments = command(component, root, state, port)
    process = None
    try:
        with isolated_dll_search():
            process = subprocess.Popen(
                arguments,
                cwd=root,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        deadline = time.monotonic() + 15
        while True:
            if process.poll() is not None:
                raise LabError("owned_service_exited")
            try:
                status, headers, raw, _ = request(port, "/health")
                value = decode(raw)
                if getattr(sys, "frozen", False):
                    from .native_runtime import RUNTIME_VERSIONS

                    if headers.get("x-lab-runtime") != RUNTIME_VERSIONS[component]:
                        raise LabError("owned_runtime_identity")
                if (
                    status == 200
                    and headers.get("x-lab-component") == component
                    and headers.get("x-lab-owned-nonce") == nonce
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
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
