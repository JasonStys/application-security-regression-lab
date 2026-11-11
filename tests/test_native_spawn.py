"""DLL-directory lifecycle refusal/cleanup and actual inert Windows child inheritance controls. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: windows_api — line 72
# parameter: monkeypatch — line 72
# definition: read — line 75
# parameter: buffer — line 75
# parameter: size — line 75
# attribute: value — line 78
# variable: kernel — line 82
# definition: test_source_and_nonwindows_runtime_do_not_change_search — line 97
# parameter: monkeypatch — line 97
# definition: test_parent_directory_restored_after_create_or_create_failure — line 115
# parameter: failed — line 115
# parameter: windows_api — line 115
# variable: call — line 124
# definition: test_bad_search_state_never_silently_passes — line 140
# parameter: category — line 141
# parameter: fault — line 141
# parameter: monkeypatch — line 141
# parameter: windows_api — line 141
# attribute: side_effect — line 145
# attribute: side_effect — line 147
# attribute: return_value — line 148
# attribute: side_effect — line 150
# attribute: return_value — line 152
# attribute: side_effect — line 154
# definition: test_restore_failure_still_drains_created_owned_service — line 160
# parameter: monkeypatch — line 161
# parameter: tmp_path — line 161
# parameter: windows_api — line 161
# variable: calls — line 166
# attribute: side_effect — line 167
# parameter: _args — line 169
# parameter: _args — line 175
# parameter: _kwargs — line 175
# parameter: _kwargs — line 177
# definition: test_actual_inert_child_directory_is_cleared_and_parent_restored — line 190
# parameter: monkeypatch — line 191
# parameter: tmp_path — line 191
# variable: kernel — line 194
# variable: get — line 195
# variable: set_directory — line 195
# attribute: argtypes — line 196
# attribute: restype — line 196
# attribute: argtypes — line 197
# attribute: restype — line 197
# variable: buffer — line 198
# variable: old_size — line 199
# variable: previous — line 201
# variable: probe — line 202
# variable: environment — line 203
# variable: key — line 205
# definition: child — line 209
# variable: result — line 211
# variable: inherited_length — line 223
# END CODE MAP

import ctypes
import os
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from asrl import native_spawn as module
from asrl.evidence import LabError


@pytest.fixture
def windows_api(monkeypatch):
    """Model only Win32 call results to test fail-closed control flow, not claim native DLL resolution."""

    def read(size, buffer):
        """Return one stable explicit pre-existing directory through the real buffer object."""
        if size:
            buffer.value = "old"
            return 3
        return 4

    kernel = SimpleNamespace(
        GetDllDirectoryW=Mock(side_effect=read), SetDllDirectoryW=Mock(return_value=1)
    )
    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(module.sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        module.ctypes, "WinDLL", Mock(return_value=kernel), raising=False
    )
    monkeypatch.setattr(module.ctypes, "set_last_error", Mock(), raising=False)
    monkeypatch.setattr(
        module.ctypes, "get_last_error", Mock(return_value=0), raising=False
    )
    return kernel


def test_source_and_nonwindows_runtime_do_not_change_search(monkeypatch):
    """Ordinary source execution and unsupported platforms never call the Windows API."""
    monkeypatch.setattr(
        module.ctypes,
        "WinDLL",
        Mock(side_effect=AssertionError("must not load")),
        raising=False,
    )
    monkeypatch.setattr(module.sys, "frozen", False, raising=False)
    with module.isolated_dll_search():
        pass
    monkeypatch.setattr(module.sys, "frozen", True)
    monkeypatch.setattr(module.sys, "platform", "linux")
    with module.isolated_dll_search():
        pass


@pytest.mark.parametrize("failed", [False, True])
def test_parent_directory_restored_after_create_or_create_failure(windows_api, failed):
    """The exact original setting is restored even when the owned CreateProcess operation raises."""
    if failed:
        with pytest.raises(OSError, match="authored startup failure"):
            with module.isolated_dll_search():
                raise OSError("authored startup failure")
    else:
        with module.isolated_dll_search():
            assert windows_api.SetDllDirectoryW.call_args.args == (None,)
    assert [call.args for call in windows_api.SetDllDirectoryW.call_args_list] == [
        (None,),
        ("old",),
    ]


@pytest.mark.parametrize(
    "fault,category",
    [
        ("oversize", "read"),
        ("read-error", "read"),
        ("changed", "changed"),
        ("clear", "clear"),
        ("restore", "restore"),
    ],
)
def test_bad_search_state_never_silently_passes(
    windows_api, monkeypatch, fault, category
):
    """Unreadable/truncated API state and failed reset/restore remain errors, never successful launches."""
    if fault == "oversize":
        windows_api.GetDllDirectoryW.side_effect = [32769]
    elif fault == "read-error":
        windows_api.GetDllDirectoryW.side_effect = [0]
        module.ctypes.get_last_error.return_value = 5
    elif fault == "changed":
        windows_api.GetDllDirectoryW.side_effect = [4, 0]
    elif fault == "clear":
        windows_api.SetDllDirectoryW.return_value = 0
    else:
        windows_api.SetDllDirectoryW.side_effect = [1, 0]
    with pytest.raises(LabError, match="owned_dll_search_" + category):
        with module.isolated_dll_search():
            assert fault == "restore"


def test_restore_failure_still_drains_created_owned_service(
    windows_api, tmp_path, monkeypatch
):
    """A failure AFTER Popen cannot bypass cleanup or leave an owned fixture process behind."""
    from asrl import transport

    calls = []
    windows_api.SetDllDirectoryW.side_effect = [1, 0]
    monkeypatch.setattr(
        transport, "command", lambda *_args: ["fixed-authored-test-command"]
    )
    monkeypatch.setattr(transport, "free_port", lambda: 12345)
    monkeypatch.setattr(
        transport.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SimpleNamespace(
            terminate=lambda: calls.append("terminate"),
            wait=lambda **_kwargs: calls.append("wait"),
        ),
    )
    with pytest.raises(LabError, match="owned_dll_search_restore"):
        with transport.service("php", tmp_path, tmp_path):
            pytest.fail("restore failure cannot make a service ready")
    assert calls == ["terminate", "wait"]


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Actual Windows process-local DLL inheritance control; portable API-failure fixtures remain active",
)
def test_actual_inert_child_directory_is_cleared_and_parent_restored(
    tmp_path, monkeypatch
):
    """Observe real GetDllDirectory in an isolated inert child; touch only this test process's owned directory state."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True, winmode=0x800)
    get, set_directory = kernel.GetDllDirectoryW, kernel.SetDllDirectoryW
    get.argtypes, get.restype = [ctypes.c_uint, ctypes.c_wchar_p], ctypes.c_uint
    set_directory.argtypes, set_directory.restype = [ctypes.c_wchar_p], ctypes.c_int
    buffer = ctypes.create_unicode_buffer(32769)
    old_size = get(len(buffer), buffer)
    assert old_size < len(buffer)
    previous = buffer.value if old_size else None
    probe = "import ctypes;k=ctypes.WinDLL('kernel32',winmode=0x800);f=k.GetDllDirectoryW;f.argtypes=[ctypes.c_uint,ctypes.c_wchar_p];f.restype=ctypes.c_uint;b=ctypes.create_unicode_buffer(32769);print(f(len(b),b))"
    environment = {
        key: os.environ[key]
        for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP")
        if key in os.environ
    }

    def child():
        """Run only fixed inert source that reports a numeric directory length, no paths/environment contents."""
        result = subprocess.run(
            [sys.executable, "-I", "-c", probe],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            check=True,
            timeout=10,
        )
        return int(result.stdout.strip())

    try:
        assert set_directory(str(tmp_path))
        inherited_length = child()
        assert inherited_length > 0
        monkeypatch.setattr(module.sys, "frozen", True, raising=False)
        with module.isolated_dll_search():
            assert child() == 0
        assert get(len(buffer), buffer) > 0 and buffer.value == str(tmp_path)
    finally:
        assert set_directory(previous)
