"""Bounded volatile startup classification for owned PHP; raw errors and paths never escape. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: StartupDiagnostic — line 34
# definition: __init__ — line 37
# parameter: self — line 37
# parameter: stream — line 37
# attribute: stream — line 39
# attribute: buffer — line 40
# attribute: lock — line 41
# attribute: failed — line 42
# attribute: thread — line 43
# definition: drain — line 46
# parameter: self — line 46
# variable: read — line 49
# variable: raw — line 50
# attribute: failed — line 54
# definition: category — line 58
# parameter: self — line 58
# variable: raw — line 61
# variable: category — line 64
# variable: marker — line 64
# definition: close — line 74
# parameter: self — line 74
# END CODE MAP

from __future__ import annotations

from threading import Lock, Thread
from typing import IO

from .evidence import LabError


class StartupDiagnostic:
    """Drain only an owned child's pipe; retain at most 16 KiB in memory and expose fixed classes only."""

    def __init__(self, stream: IO[bytes]) -> None:
        """Start the retained drain thread after successful CreateProcess; no output file or user environment is read."""
        self.stream = stream
        self.buffer = bytearray()
        self.lock = Lock()
        self.failed = False
        self.thread = Thread(target=self.drain, name="owned-php-startup-diagnostic")
        self.thread.start()

    def drain(self) -> None:
        """Discard later data while consuming the pipe, avoiding both child backpressure and unbounded retention."""
        try:
            read = getattr(self.stream, "read1", self.stream.read)
            while raw := read(4096):
                with self.lock:
                    self.buffer.extend(raw[: max(0, 16384 - len(self.buffer))])
        except (OSError, ValueError):
            self.failed = True
        finally:
            self.stream.close()

    def category(self) -> str:
        """Return only a closed startup class, independent of path/SQL/body contents; missing output remains unknown."""
        with self.lock:
            raw = bytes(self.buffer).lower()
        if b"unable to load dynamic library" not in raw:
            return "unclassified"
        for marker, category in (
            (b"the specified module could not be found", "module_missing"),
            (b"the specified procedure could not be found", "procedure_missing"),
            (b"not a valid win32 application", "bad_image"),
            (b"access is denied", "access_denied"),
        ):
            if marker in raw:
                return category
        return "startup_other"

    def close(self) -> None:
        """After owned child termination, require its drainer to finish and erase private in-memory text."""
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise LabError("owned_php_diagnostic_drain")
        with self.lock:
            self.buffer.clear()
        if self.failed:
            raise LabError("owned_php_diagnostic_read")
