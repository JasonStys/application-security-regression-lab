"""Temporarily isolate fixed native children from inherited PyInstaller Windows DLL search state. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: SPAWN_LOCK — line 29
# definition: isolated_dll_search — line 33
# variable: kernel — line 41
# variable: get — line 42
# attribute: argtypes — line 43
# attribute: restype — line 43
# variable: set_directory — line 44
# attribute: argtypes — line 45
# attribute: restype — line 45
# variable: size — line 48
# variable: previous — line 51
# variable: buffer — line 53
# variable: actual — line 55
# variable: previous — line 58
# END CODE MAP

from __future__ import annotations

import ctypes
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock

from .evidence import LabError

SPAWN_LOCK = Lock()


@contextmanager
def isolated_dll_search() -> Iterator[None]:
    """Clear only this process's frozen DLL directory for CreateProcess; restore before waiting for a child."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        yield
        return
    # Environment/PATH alone cannot clear bootloader SetDllDirectory state.
    # The single worker starts after Python/Tk extension imports. This tiny
    # clear/create/restore section contains no HTTP or child-completion wait.
    kernel = ctypes.WinDLL("kernel32", use_last_error=True, winmode=0x800)
    get = kernel.GetDllDirectoryW
    get.argtypes, get.restype = [ctypes.c_uint, ctypes.c_wchar_p], ctypes.c_uint
    set_directory = kernel.SetDllDirectoryW
    set_directory.argtypes, set_directory.restype = [ctypes.c_wchar_p], ctypes.c_int
    with SPAWN_LOCK:
        ctypes.set_last_error(0)
        size = get(0, None)
        if size > 32768 or (size == 0 and ctypes.get_last_error()):
            raise LabError("owned_dll_search_read")
        previous = None
        if size:
            buffer = ctypes.create_unicode_buffer(size + 1)
            ctypes.set_last_error(0)
            actual = get(len(buffer), buffer)
            if actual + 1 != size or actual >= len(buffer) or ctypes.get_last_error():
                raise LabError("owned_dll_search_changed")
            previous = buffer.value if actual else None
        if not set_directory(None):
            raise LabError("owned_dll_search_clear")
        try:
            yield
        finally:
            if not set_directory(previous):
                raise LabError("owned_dll_search_restore")
