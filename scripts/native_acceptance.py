"""Actual frozen AppSec widgets, four real service engines and durable restart acceptance. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 134
# parameter: target — line 134
# parameter: window — line 134
# variable: load — line 140
# variable: gdi — line 141
# variable: user — line 141
# variable: pointer — line 142
# variable: arguments — line 143
# variable: library — line 143
# variable: name — line 143
# variable: result — line 143
# variable: function — line 169
# attribute: argtypes — line 170
# attribute: restype — line 170
# variable: handle — line 173
# variable: rectangle — line 174
# variable: height — line 177
# variable: width — line 177
# variable: source — line 180
# variable: destination — line 181
# variable: bitmap — line 182
# variable: previous — line 183
# variable: pixels — line 188
# variable: header — line 189
# variable: raw — line 207
# variable: scanlines — line 208
# variable: row — line 209
# variable: column — line 211
# variable: offset — line 212
# definition: chunk — line 215
# parameter: data — line 215
# parameter: name — line 215
# definition: oracle — line 237
# parameter: files — line 237
# parameter: index — line 237
# variable: value — line 240
# variable: counts — line 241
# variable: row — line 242
# variable: name — line 243
# variable: expected — line 245
# variable: selected — line 247
# variable: expected — line 248
# variable: count — line 250
# variable: name — line 250
# variable: row — line 252
# variable: by_id — line 253
# variable: row — line 253
# variable: name — line 255
# variable: status — line 255
# variable: value — line 269
# variable: row — line 275
# variable: value — line 283
# variable: row — line 284
# definition: exercise — line 304
# parameter: output — line 304
# parameter: reopen — line 304
# parameter: window — line 304
# variable: expected — line 309
# variable: started — line 309
# variable: receipt — line 310
# variable: deadline — line 327
# definition: progress — line 329
# parameter: stage — line 329
# definition: finish — line 336
# parameter: failed — line 336
# attribute: acceptance_result — line 338
# variable: name — line 346
# variable: raw — line 346
# variable: row — line 348
# definition: checked — line 353
# parameter: callback — line 353
# variable: trace — line 361
# variable: trace — line 369
# definition: callback_failed — line 372
# parameter: _traceback — line 373
# parameter: _value — line 373
# parameter: kind — line 373
# definition: wait — line 379
# parameter: callback — line 379
# definition: layout — line 389
# variable: widgets — line 394
# variable: name — line 395
# variable: widget — line 397
# definition: rejected — line 419
# definition: licenses — line 428
# variable: dialogs — line 431
# variable: child — line 433
# variable: dialog — line 437
# variable: pending — line 438
# variable: texts — line 439
# variable: widget — line 441
# variable: text — line 447
# variable: value — line 450
# definition: completed — line 455
# parameter: index — line 455
# variable: files — line 461
# variable: parent — line 480
# variable: target — line 486
# variable: path — line 487
# variable: selected — line 490
# definition: start — line 501
# parameter: index — line 501
# variable: selected — line 508
# definition: begin — line 521
# variable: identity — line 525
# attribute: report_callback_exception — line 541
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import tkinter as tk
import zlib
from pathlib import Path
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from asrl import desktop_project as project
from asrl.desktop_io import json_value
from asrl.evidence import passed

if TYPE_CHECKING:
    from asrl.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [
                pointer,
                pointer,
                ctypes.c_uint,
                ctypes.c_uint,
                pointer,
                pointer,
                ctypes.c_uint,
            ],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    # Flush this owned native window's pending control messages before reading its pixels.
    window.root.update()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                -height,
                1,
                32,
                0,
                width * height * 4,
                0,
                0,
                0,
                0,
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def oracle(index: int, files: dict[str, bytes]) -> None:
    """Use literal case counts, independent boundary IDs and cohort dispositions, not just a caller's passed flag."""
    if index < 5:
        value = json_value(files["http.json"])
        counts = {
            name: sum(row["component"] == name for row in value["cases"])
            for name in ("java", "session", "php", "node")
        }
        expected = {"java": 20, "session": 20, "php": 24, "node": 11}
        if index:
            selected = ("java", "session", "php", "node")[index - 1]
            expected = {
                name: count if name == selected else 0
                for name, count in expected.items()
            }
        assert counts == expected and all(passed(row) for row in value["cases"])
        by_id = {row["id"]: row for row in value["cases"]}
        assert len(by_id) == sum(counts.values())
        for name, status in {
            "JAVA-READ-CROSS": 404,
            "JAVA-STALE-WRITE": 409,
            "PHP-SQL-INJECTION": 200,
            "PHP-CROSS-DOWNLOAD": 404,
            "SESSION-REVOKED-COOKIE": 401,
            "NODE-TRAVERSAL": 404,
        }.items():
            if counts[name.split("-")[0].lower()]:
                assert (
                    by_id[name]["observed"] == status
                    and by_id[name]["content_ok"] is True
                )
    elif index in (5, 6):
        value = json_value(files["review.json"])
        assert (
            value["kind"] == "supplied_http_evidence_review"
            and "Fictional" in value["report"]["note"]
        )
        assert len(value["report"]["cases"]) == 6
        assert sum(not passed(row) for row in value["report"]["cases"]) == (
            2 if index == 5 else 3
        )
        assert (
            value["input_sha256"]
            == hashlib.sha256(files["supplied-http.json"]).hexdigest()
        )
    else:
        value = json_value(files["review.json"])
        assert {row["case_id"]: row["state"] for row in value["cases"]} == {
            "ADDED": "NEW_CASE",
            "CHANGED": "ASSERTION_CHANGED",
            "MISSING": "NOT_EXECUTED",
            "PERSISTENT": "STILL_FAIL",
            "RECOVERED": "RECOVERED",
            "REGRESSED": "REGRESSION",
            "STABLE": "STILL_PASS",
        }
        assert len(value["review_queue"]) == 5
        assert (
            value["baseline_sha256"]
            == hashlib.sha256(files["baseline.json"]).hexdigest()
        )
        assert (
            value["candidate_sha256"]
            == hashlib.sha256(files["candidate.json"]).hexdigest()
        )


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the same real widgets/core worker and owned service process cleanup; mock only OS file-picker selection."""
    from unittest.mock import patch

    output.mkdir(mode=0o700)
    started, expected = time.monotonic(), 8
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        "source": window.identity["source"],
        "source_dirty": window.identity["source_dirty"],
        "python_version": sys.version.split()[0],
        "python_dll_sha256": window.identity.get("python_dll_sha256"),
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
        "tcl_version": str(window.root.tk.call("info", "patchlevel")),
        "tk_version": str(window.root.tk.call("package", "require", "Tk")),
    }
    deadline = started + 65

    def progress(stage: str) -> None:
        """Keep value-free milestone evidence if a native service or UI step fails."""
        receipt["last_stage"] = stage
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def finish(failed: bool = False) -> None:
        """Request normal close and preserve exact bundle identities; failure is never replaced by success on cleanup."""
        window.acceptance_result = not failed
        receipt["passed"] = not failed
        if failed:
            receipt["safe_application_status"] = window.status.get()[:240]
        receipt["journey_elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        progress("failed-retained" if failed else "normal-close-requested")
        window.exit()

    def checked(callback: Any) -> None:
        """A failed assertion becomes a nonzero normal app exit, without private exception/body output."""
        try:
            callback()
        except Exception as error:
            receipt["failure_stage"] = callback.__name__
            receipt["failure_type"] = type(error).__name__[:60]
            receipt["failure_step"] = receipt.get("last_stage")
            trace = error.__traceback__
            while trace is not None:
                if (
                    Path(trace.tb_frame.f_code.co_filename).name
                    == "native_acceptance.py"
                ):
                    receipt["failure_function"] = trace.tb_frame.f_code.co_name[:60]
                    receipt["failure_line"] = trace.tb_lineno
                trace = trace.tb_next
            finish(True)

    def callback_failed(
        kind: type[BaseException], _value: BaseException, _traceback: Any
    ) -> None:
        """Do not lose Tk callback errors in a windowed executable without stderr."""
        receipt["failure_type"] = kind.__name__[:60]
        finish(True)

    def wait(callback: Any) -> None:
        """Wait for the actual retained worker with one fixed deadline; no audit repetition or forced child abandonment."""
        if time.monotonic() > deadline:
            receipt["failure_stage"] = "owned-workflow-deadline"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def layout() -> None:
        """Require real active controls and Exit to fit the minimum supported native window."""
        window.root.geometry("980x700")
        window.tabs.tk.call(str(window.tabs), "select", str(window.inputs_page))
        window.root.update()
        widgets: list[ttk.Widget] = [window.run_button, *window.footer_buttons.values()]
        for name in project.ACTIVE_FIELDS[window.mode.get()]:
            widgets.extend(window.field_widgets[name])
        for widget in widgets:
            assert widget.winfo_ismapped()
            assert (
                widget.winfo_rootx() >= window.root.winfo_rootx()
                and widget.winfo_rooty() >= window.root.winfo_rooty()
            )
            assert (
                widget.winfo_rootx() + widget.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                widget.winfo_rooty() + widget.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        receipt["minimum_layout"] = {
            "width": 980,
            "height": 700,
            "activeInputsRunAndLifecycleVisible": True,
        }
        window.root.geometry("1260x860")
        window.root.update()

    def rejected() -> None:
        """A duplicate-key selected report must preserve every earlier real result and produce a visible rejection."""
        assert (
            len(window.state.history()) == expected
            and "rejected" in window.status.get().lower()
        )
        receipt["steps"].append("actual-invalid-report-retains-eight-bundles")
        finish()

    def licenses() -> None:
        """Inspect the actual bundled text notice window, not a source-only declaration that licenses exist."""
        window.licenses()
        dialogs = [
            child
            for child in window.root.winfo_children()
            if isinstance(child, tk.Toplevel)
        ]
        assert len(dialogs) == 1
        dialog = dialogs[0]
        pending: list[tk.Misc] = [dialog]
        texts: list[tk.Text] = []
        while pending:
            widget = pending.pop()
            if isinstance(widget, tk.Text):
                texts.append(widget)
            pending.extend(widget.winfo_children())
            assert len(pending) < 1000
        assert len(texts) == 1
        text = texts[0].get("1.0", "end")
        assert all(
            value in text
            for value in ("Python", "Tcl", "Tk", "Node.js", "PHP", ".NET", "OpenJDK")
        )
        dialog.destroy()
        receipt["steps"].append("actual-bundled-runtime-license-window")

    def completed(index: int) -> None:
        """Read actual original outputs and inspect real rows; no service response or analysis result is mocked."""
        assert (
            len(window.state.history()) == index + 1
            and window.selected_run == index + 1
        )
        files = window.state.files(index + 1)
        oracle(index, files)
        if index in (0, 7):
            window.table.selection_set("0")
            window.inspect()
            assert json.loads(window.details.get("1.0", "end"))
            window.root.update()
            capture(
                window,
                output
                / ("selected-evidence.png" if index == 0 else "cohort-review.png"),
            )
        receipt["steps"].append("actual-workflow-" + str(index + 1))
        if index + 1 < expected:
            start(index + 1)
        else:
            progress("runtime-license-window")
            licenses()
            progress("exact-export")
            parent = output / "exact-export"
            parent.mkdir()
            with patch(
                "asrl.desktop.filedialog.askdirectory", return_value=str(parent)
            ):
                window.export_button.invoke()
            target = next(parent.iterdir())
            assert {path.name: path.read_bytes() for path in target.iterdir()} == files
            receipt["steps"].append("actual-exact-export")
            progress("invalid-report-retention")
            selected = output / "duplicate-key.json"
            selected.write_text('{"schema":1,"schema":2}', encoding="utf-8")
            window.mode.set(project.MODES[1])
            with patch(
                "asrl.desktop.filedialog.askopenfilename", return_value=str(selected)
            ):
                window.choose("report", "file")
            window.authorized.set(True)
            window.run_button.invoke()
            wait(rejected)

    def start(index: int) -> None:
        """Prepared scenarios set ordinary controls; a real copied external report is selected through the same chooser."""
        progress("workflow-" + str(index + 1))
        window.prepared.set(project.SCENARIOS[index])
        window.load_prepared()
        assert not window.authorized.get()
        if index == 5:
            selected = output / "authorized-report.json"
            selected.write_bytes(
                (project.ROOT / "examples/desktop/baseline.json").read_bytes()
            )
            with patch(
                "asrl.desktop.filedialog.askopenfilename", return_value=str(selected)
            ):
                window.choose("report", "file")
        layout()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(lambda: completed(index))

    def begin() -> None:
        """A separate real process reopens all exact bundles without rerunning services or recomputing a prior report."""
        if reopen:
            assert len(window.state.history()) == expected
            for identity in range(1, expected + 1):
                window.history_table.selection_set(str(identity))
                window.open_button.invoke()
                assert window.selected_run == identity
                oracle(identity - 1, window.state.files(identity))
            receipt["steps"].append("actual-process-reopen-eight-exact-bundles")
            finish()
        else:
            assert not window.state.history()
            window.run_button.invoke()
            assert (
                not window.state.history()
                and "permission" in window.status.get().lower()
            )
            start(0)

    window.root.report_callback_exception = callback_failed
    checked(begin)
