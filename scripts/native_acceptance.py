"""Actual frozen AppSec widgets, four real service engines and durable restart acceptance. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 142
# parameter: target — line 142
# parameter: window — line 142
# variable: load — line 148
# variable: gdi — line 149
# variable: user — line 149
# variable: pointer — line 150
# variable: arguments — line 151
# variable: library — line 151
# variable: name — line 151
# variable: result — line 151
# variable: function — line 177
# attribute: argtypes — line 178
# attribute: restype — line 178
# variable: handle — line 181
# variable: rectangle — line 182
# variable: height — line 185
# variable: width — line 185
# variable: source — line 188
# variable: destination — line 189
# variable: bitmap — line 190
# variable: previous — line 191
# variable: pixels — line 196
# variable: header — line 197
# variable: raw — line 215
# variable: scanlines — line 216
# variable: row — line 217
# variable: column — line 219
# variable: offset — line 220
# definition: chunk — line 223
# parameter: data — line 223
# parameter: name — line 223
# definition: oracle — line 245
# parameter: files — line 245
# parameter: index — line 245
# variable: value — line 248
# variable: counts — line 249
# variable: row — line 250
# variable: name — line 251
# variable: expected — line 253
# variable: selected — line 255
# variable: expected — line 256
# variable: count — line 258
# variable: name — line 258
# variable: row — line 260
# variable: by_id — line 261
# variable: row — line 261
# variable: name — line 263
# variable: status — line 263
# variable: value — line 277
# variable: row — line 283
# variable: value — line 291
# variable: row — line 292
# variable: copied — line 311
# variable: row — line 314
# definition: exercise — line 327
# parameter: output — line 327
# parameter: reopen — line 327
# parameter: window — line 327
# variable: expected — line 332
# variable: started — line 332
# variable: receipt — line 333
# variable: deadline — line 350
# definition: progress — line 352
# parameter: stage — line 352
# definition: finish — line 359
# parameter: failed — line 359
# attribute: acceptance_result — line 361
# variable: name — line 369
# variable: raw — line 369
# variable: row — line 371
# definition: checked — line 376
# parameter: callback — line 376
# variable: trace — line 384
# variable: trace — line 392
# definition: callback_failed — line 395
# parameter: _traceback — line 396
# parameter: _value — line 396
# parameter: kind — line 396
# definition: wait — line 402
# parameter: callback — line 402
# definition: layout — line 412
# variable: widgets — line 417
# variable: name — line 418
# variable: widget — line 420
# definition: rejected — line 442
# definition: licenses — line 451
# variable: dialogs — line 454
# variable: child — line 456
# variable: dialog — line 460
# variable: pending — line 461
# variable: texts — line 462
# variable: widget — line 464
# variable: text — line 470
# variable: value — line 473
# definition: completed — line 478
# parameter: index — line 478
# variable: files — line 484
# variable: parent — line 503
# variable: target — line 509
# variable: path — line 510
# variable: selected — line 513
# definition: start — line 524
# parameter: index — line 524
# variable: selected — line 531
# definition: begin — line 544
# variable: direct — line 551
# variable: port — line 556
# variable: control_rows — line 557
# variable: row — line 560
# variable: category — line 568
# variable: suffix — line 571
# variable: identity — line 589
# attribute: report_callback_exception — line 605
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
    if index in (0, 3):
        copied = json_value(files["php-runtime-context.json"])
        assert copied["namespace"] == "fresh-owned-outside-frozen-extraction"
        assert len(copied["files"]) == 9
        assert {row["path"] for row in copied["files"]} == {
            "runtime/php/php.exe",
            "runtime/php/php8.dll",
            "runtime/php/libsqlite3.dll",
            "runtime/php/ext/php_pdo_sqlite.dll",
            "runtime/php/vcruntime140.dll",
            "runtime/php/vcruntime140_1.dll",
            "services/php/router.php",
            "services/php/Store.php",
            "sql/schema.sql",
        }


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
        if not reopen:
            from asrl.cases import exercise as actual_cases
            from asrl.evidence import LabError
            from asrl.transport import service

            direct = output / "owned-extraction-control"
            direct.mkdir(mode=0o700)
            try:
                with service(
                    "php", project.ROOT, direct, _direct_frozen_php=True
                ) as port:
                    control_rows = actual_cases("php", port)
                assert len(control_rows) == 24 and all(
                    row["observed"] == row["expected"] and row["content_ok"] is True
                    for row in control_rows
                )
                receipt["direct_php_namespace_control"] = {
                    "passed": True,
                    "http_cases": 24,
                    "scope": "Direct extraction namespace comparative observation; separate from the full isolated-runtime user acceptance.",
                }
            except LabError as error:
                category = str(error)
                if category not in {
                    "owned_php_driver_" + suffix
                    for suffix in (
                        "module_missing",
                        "procedure_missing",
                        "bad_image",
                        "access_denied",
                        "startup_other",
                        "unclassified",
                    )
                }:
                    raise
                receipt["direct_php_namespace_control"] = {
                    "passed": False,
                    "category": category,
                    "scope": "Historical/direct runtime boundary remains failed; not retroactively passed. The copied-runtime full150HTTP acceptance below is independently mandatory.",
                }
            progress("direct-namespace-control-recorded")
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
