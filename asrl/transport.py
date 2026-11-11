"""Jason Stys: explicit owned numeric-loopback request/process lifecycle, no external-target scan interface."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: request — line 79
# parameter: port — line 80
# parameter: path — line 81
# parameter: method — line 82
# parameter: body — line 83
# parameter: headers — line 84
# variable: started — line 95
# variable: connection — line 96
# variable: response — line 99
# variable: raw — line 100
# variable: name — line 105
# variable: value — line 105
# definition: free_port — line 115
# variable: descriptor — line 117
# definition: command — line 122
# parameter: component — line 122
# parameter: port — line 122
# parameter: root — line 122
# parameter: state — line 122
# variable: commands — line 130
# definition: service — line 151
# parameter: _direct_frozen_php — line 152
# parameter: component — line 152
# parameter: root — line 152
# parameter: state — line 152
# variable: port — line 157
# variable: contexts — line 158
# variable: process — line 159
# variable: diagnostic — line 160
# variable: launch — line 161
# variable: capture_startup — line 162
# variable: working_root — line 164
# variable: launch — line 169
# variable: arguments — line 170
# variable: environment — line 170
# variable: working_root — line 170
# variable: receipt — line 175
# variable: environment — line 181
# variable: environment — line 183
# variable: arguments — line 184
# variable: nonce — line 185
# attribute: cleanup_permitted — line 188
# variable: process — line 190
# variable: diagnostic — line 202
# variable: deadline — line 203
# variable: _ — line 208
# variable: headers — line 208
# variable: raw — line 208
# variable: status — line 208
# variable: value — line 209
# variable: category — line 219
# variable: child_completed — line 245
# variable: child_completed — line 266
# attribute: cleanup_permitted — line 269
# variable: pipe — line 273
# attribute: cleanup_permitted — line 278
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
from contextlib import ExitStack, contextmanager
from pathlib import Path

from .evidence import COMPONENTS, MAX_RESPONSE, LabError, decode
from .native_spawn import isolated_dll_search
from .native_stderr import StartupDiagnostic


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
def service(
    component: str, root: Path, state: Path, *, _direct_frozen_php: bool = False
) -> Iterator[int]:
    """Start only an owned fixed service; PHP copies the exact admitted closure outside the freezer namespace."""
    if type(_direct_frozen_php) is not bool:
        raise LabError("owned_php_namespace_control")
    port = free_port()
    contexts = ExitStack()
    process = None
    diagnostic = None
    launch = None
    capture_startup = component == "php" and getattr(sys, "frozen", False)
    try:
        working_root = root
        if capture_startup and not _direct_frozen_php:
            from .desktop_io import canonical
            from .native_php import isolated_php

            launch = contexts.enter_context(isolated_php(root, state, port))
            arguments, environment, working_root = (
                launch.arguments,
                launch.environment,
                launch.root,
            )
            with (state / "php-runtime-context.json").open("xb") as receipt:
                receipt.write(canonical(launch.receipt))
        else:
            if getattr(sys, "frozen", False):
                from .native_runtime import environment as bundled_environment

                environment = bundled_environment(state, root, component)
            else:
                environment = {**os.environ, "ASRL_PHP_DB": str(state / "php.sqlite")}
            arguments = command(component, root, state, port)
        nonce = secrets.token_hex(32)
        environment["ASRL_OWNED_NONCE"] = nonce
        if launch is not None:
            launch.cleanup_permitted = False
        with isolated_dll_search():
            process = subprocess.Popen(
                arguments,
                cwd=working_root,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE if capture_startup else subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        if capture_startup:
            if process.stderr is None:
                raise LabError("owned_php_diagnostic_pipe")
            diagnostic = StartupDiagnostic(process.stderr)
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
                        component == "php"
                        and headers.get("x-lab-sqlite") != "available"
                    ):
                        category = (
                            diagnostic.category() if diagnostic else "unavailable"
                        )
                        raise LabError("owned_php_driver_" + category)
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
        try:
            if process is not None:
                try:
                    process.terminate()
                except OSError:
                    pass  # The exact child may have exited between observation and signal.
                child_completed = False
                try:
                    try:
                        process.wait(timeout=5)
                    except (subprocess.TimeoutExpired, OSError):
                        try:
                            process.kill()
                        except OSError:
                            pass
                        try:
                            process.wait(timeout=5)
                        except (subprocess.TimeoutExpired, OSError):
                            # Neither a timeout nor an issued kill proves completion.
                            # Retain the same GUI worker/profile lock/copy until the
                            # exact created child is reaped; never finish with an orphan.
                            while True:
                                try:
                                    process.wait(timeout=1)
                                    break
                                except (subprocess.TimeoutExpired, OSError):
                                    time.sleep(0.05)
                    child_completed = True
                finally:
                    if launch is not None:
                        launch.cleanup_permitted = child_completed
                    if diagnostic is not None:
                        diagnostic.close()
                    elif capture_startup:
                        pipe = getattr(process, "stderr", None)
                        if pipe is not None:
                            pipe.close()
        finally:
            if launch is not None and process is None:
                launch.cleanup_permitted = True  # Popen returned no owned child.
            # Exiting the copy context comes strictly AFTER owned child wait/drain.
            contexts.close()
