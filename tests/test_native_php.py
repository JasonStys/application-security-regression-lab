"""Actual whole-bundle admission, fixed same-byte PHP copies and child-before-cleanup ownership. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: runtime — line 129
# parameter: tmp_path — line 129
# variable: root — line 131
# variable: state — line 132
# variable: entries — line 135
# variable: index — line 136
# variable: name — line 136
# variable: path — line 143
# variable: raw — line 145
# definition: test_actual_copy_binds_original_bytes_and_closed_argv_environment — line 156
# parameter: monkeypatch — line 157
# parameter: runtime — line 157
# variable: root — line 160
# variable: state — line 160
# variable: original — line 163
# variable: p — line 165
# variable: launch — line 168
# variable: selected — line 169
# variable: row — line 194
# variable: p — line 203
# definition: test_partial_or_changed_source_never_becomes_a_new_trust_root — line 218
# parameter: fault — line 218
# parameter: runtime — line 218
# variable: root — line 220
# variable: state — line 220
# variable: manifest — line 221
# variable: port — line 222
# variable: row — line 226
# variable: row — line 235
# variable: port — line 244
# variable: state — line 246
# definition: test_late_source_change_rejected_and_only_owned_copy_cleaned — line 253
# parameter: monkeypatch — line 253
# parameter: runtime — line 253
# variable: root — line 255
# variable: state — line 255
# variable: actual — line 256
# definition: changed — line 258
# parameter: limit — line 258
# parameter: path — line 258
# definition: test_copied_bytes_and_manifest_observation_cannot_silently_diverge — line 274
# parameter: fault — line 275
# parameter: monkeypatch — line 275
# parameter: runtime — line 275
# variable: root — line 278
# variable: state — line 278
# variable: actual — line 279
# definition: altered — line 281
# parameter: limit — line 281
# parameter: path — line 281
# definition: test_unexpected_context_error_cleans_only_owned_namespace — line 299
# parameter: runtime — line 299
# variable: root — line 301
# variable: state — line 301
# variable: launch — line 303
# variable: copied — line 304
# definition: test_changed_owner_marker_refuses_cleanup_of_unknown_replacement — line 310
# parameter: runtime — line 310
# variable: root — line 312
# variable: state — line 312
# variable: launch — line 314
# variable: selected — line 315
# definition: test_real_copy_service_waits_for_exact_owned_child_before_removal — line 320
# parameter: monkeypatch — line 321
# parameter: runtime — line 321
# variable: root — line 324
# variable: state — line 324
# variable: observed — line 325
# parameter: _count — line 329
# definition: launch — line 331
# parameter: argv — line 331
# parameter: kwargs — line 331
# variable: selected — line 333
# definition: wait — line 339
# parameter: _kwargs — line 339
# parameter: _args — line 355
# variable: port — line 367
# variable: receipt — line 374
# definition: test_unproven_exit_lease_survives_context_generator_finalization — line 378
# parameter: runtime — line 378
# variable: root — line 380
# variable: state — line 380
# variable: context — line 381
# variable: launch — line 382
# attribute: cleanup_permitted — line 383
# definition: test_double_timeout_retains_worker_and_bytes_until_exact_child_completion — line 392
# parameter: monkeypatch — line 393
# parameter: runtime — line 393
# parameter: signal_error — line 393
# variable: root — line 396
# variable: state — line 396
# variable: _ — line 397
# variable: completed — line 397
# variable: finished — line 397
# variable: pending — line 397
# variable: errors — line 398
# variable: observations — line 398
# parameter: _ — line 402
# definition: signal — line 404
# definition: create — line 409
# parameter: _arguments — line 409
# parameter: kwargs — line 409
# variable: selected — line 411
# variable: calls — line 413
# definition: wait — line 415
# parameter: timeout — line 415
# variable: value — line 424
# parameter: _ — line 439
# definition: worker — line 452
# variable: thread — line 462
# END CODE MAP

import hashlib
import io
import json
import threading
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from asrl import native_php, native_runtime, transport
from asrl.desktop_io import Rejected


@pytest.fixture
def runtime(tmp_path):
    """Actual inert files satisfy full source inventory; fake executable bytes are never run by these unit fixtures."""
    root = tmp_path / "authenticated-source"
    state = tmp_path / "owned-analysis"
    root.mkdir()
    state.mkdir()
    entries = []
    for index, name in enumerate(
        sorted(
            set(native_runtime.ENTRYPOINTS.values())
            | set(native_runtime.REQUIRED_DATA)
            | set(native_php.PHP_FILES)
        )
    ):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = b"inert namespace fixture " + str(index).encode()
        path.write_bytes(raw)
        entries.append(
            {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        )
    (root / "runtime-manifest.json").write_text(
        json.dumps({"schema": 1, "entries": entries}), encoding="utf-8"
    )
    return root, state


def test_actual_copy_binds_original_bytes_and_closed_argv_environment(
    runtime, monkeypatch
):
    """Exact admitted files are copied outside the extraction root, independently read back and removed after use."""
    root, state = runtime
    monkeypatch.setenv("PATH", "UNTRUSTED-USER-DIRECTORY")
    monkeypatch.setenv("OPENAI_API_KEY", "PRIVATE-INERT")
    original = {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }
    with native_php.isolated_php(root, state, 12345) as launch:
        selected = launch.root
        assert selected.parent == state and not selected.is_relative_to(root)
        assert selected.name.startswith("owned-php-runtime-")
        assert launch.arguments == [
            str(selected / "runtime/php/php.exe"),
            "-n",
            "-d",
            "display_errors=0",
            "-d",
            "extension=" + str(selected / "runtime/php/ext/php_pdo_sqlite.dll"),
            "-S",
            "127.0.0.1:12345",
            str(selected / "services/php/router.php"),
        ]
        assert (
            "UNTRUSTED" not in launch.environment["PATH"]
            and "OPENAI_API_KEY" not in launch.environment
        )
        assert launch.environment["ASRL_PHP_DB"] == str(state / "php.sqlite")
        assert len(launch.receipt["files"]) == 9
        assert (
            launch.receipt["source_manifest_sha256"]
            == hashlib.sha256((root / "runtime-manifest.json").read_bytes()).hexdigest()
        )
        assert str(selected) not in json.dumps(launch.receipt)
        for row in launch.receipt["files"]:
            assert (selected / row["path"]).read_bytes() == original[row["path"]]
            assert (
                hashlib.sha256((selected / row["path"]).read_bytes()).hexdigest()
                == row["sha256"]
            )
    assert not selected.exists() and not list(state.iterdir())
    assert {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    } == original


@pytest.mark.parametrize(
    "fault",
    [
        "partial-source",
        "missing-closure",
        "changed-source",
        "bad-port",
        "inside-source-state",
    ],
)
def test_partial_or_changed_source_never_becomes_a_new_trust_root(runtime, fault):
    """The original all-four-program inventory remains mandatory even though only PHP is copied for this child."""
    root, state = runtime
    manifest = json.loads((root / "runtime-manifest.json").read_bytes())
    port = 12345
    if fault == "partial-source":
        manifest["entries"] = [
            row
            for row in manifest["entries"]
            if row["path"] != "runtime/java/bin/java.exe"
        ]
        (root / "runtime-manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
    elif fault == "missing-closure":
        manifest["entries"] = [
            row
            for row in manifest["entries"]
            if row["path"] != "runtime/php/libsqlite3.dll"
        ]
        (root / "runtime-manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
    elif fault == "changed-source":
        (root / "runtime/php/php8.dll").write_bytes(b"different bytes")
    elif fault == "bad-port":
        port = True
    else:
        state = root / "inside-resources"
        state.mkdir()
    with pytest.raises(Rejected), native_php.isolated_php(root, state, port):
        pytest.fail("unadmitted source cannot yield a launch")
    assert not list(state.glob("owned-php-runtime-*"))


def test_late_source_change_rejected_and_only_owned_copy_cleaned(runtime, monkeypatch):
    """A full validation result is not substituted for checking actual bytes again at the copy boundary."""
    root, state = runtime
    actual = native_php.read_source

    def changed(path, limit):
        """Change only a subsequent source observation, not the independent full bundle validator."""
        if path == root / "runtime/php/libsqlite3.dll":
            return b"changed after whole-bundle admission"
        return actual(path, limit)

    monkeypatch.setattr(native_php, "read_source", changed)
    with (
        pytest.raises(Rejected, match="changed before copying"),
        native_php.isolated_php(root, state, 12345),
    ):
        pytest.fail("late changed bytes executed")
    assert list(state.iterdir()) == []


@pytest.mark.parametrize("fault", ["copied-bytes", "source-manifest"])
def test_copied_bytes_and_manifest_observation_cannot_silently_diverge(
    runtime, monkeypatch, fault
):
    """Independent post-admission observations must bind the bytes actually copied and the declared source inventory."""
    root, state = runtime
    actual = native_php.read_source

    def altered(path, limit):
        """Interleave only the selected later copy/manifest observation while full original validation remains real."""
        if fault == "source-manifest" and path == root / "runtime-manifest.json":
            return b'{"schema":1,"entries":[]}'
        if (
            fault == "copied-bytes"
            and path.name == "libsqlite3.dll"
            and path.is_relative_to(state)
        ):
            return b"copy changed"
        return actual(path, limit)

    monkeypatch.setattr(native_php, "read_source", altered)
    with pytest.raises(Rejected), native_php.isolated_php(root, state, 12345):
        pytest.fail("divergent source/copy metadata cannot yield")
    assert list(state.iterdir()) == []


def test_unexpected_context_error_cleans_only_owned_namespace(runtime):
    """Exceptions still remove the exact nonce-marked child namespace while preserving all original source files."""
    root, state = runtime
    with pytest.raises(RuntimeError, match="authored failure"):
        with native_php.isolated_php(root, state, 12345) as launch:
            copied = launch.root
            raise RuntimeError("authored failure")
    assert not copied.exists()
    assert (root / "runtime/php/php8.dll").is_file()


def test_changed_owner_marker_refuses_cleanup_of_unknown_replacement(runtime):
    """An unexpected ownership marker is not grounds to recursively remove somebody else's directory."""
    root, state = runtime
    with pytest.raises(Rejected, match="cleanup identity changed"):
        with native_php.isolated_php(root, state, 12345) as launch:
            selected = launch.root
            (selected / "owned-runtime.json").write_bytes(b"unexpected replacement")
    assert selected.is_dir() and (selected / "runtime/php/php8.dll").is_file()


def test_real_copy_service_waits_for_exact_owned_child_before_removal(
    runtime, monkeypatch
):
    """Use real filesystem copy/admission and only an inert process boundary; verify cleanup order rather than mock it away."""
    root, state = runtime
    observed = []
    monkeypatch.setattr(transport.sys, "frozen", True, raising=False)
    monkeypatch.setattr(transport, "isolated_dll_search", nullcontext)
    monkeypatch.setattr(transport, "free_port", lambda: 12345)
    monkeypatch.setattr(transport.secrets, "token_hex", lambda _count: "a" * 64)

    def launch(argv, **kwargs):
        """Require exact copied bytes to exist throughout the created process's life."""
        selected = kwargs["cwd"]
        assert selected.parent == state and selected != root
        assert argv[0] == str(selected / "runtime/php/php.exe")
        assert (selected / "services/php/Store.php").is_file()
        observed.append(selected)

        def wait(**_kwargs):
            """The original owned wait must precede recursive copy cleanup."""
            assert selected.is_dir()
            observed.append("waited-for-exact-created-child")

        return SimpleNamespace(
            stderr=io.BufferedReader(io.BytesIO(b"")),
            poll=lambda: None,
            terminate=lambda: observed.append("terminated-exact-created-child"),
            wait=wait,
        )

    monkeypatch.setattr(transport.subprocess, "Popen", launch)
    monkeypatch.setattr(
        transport,
        "request",
        lambda *_args: (
            200,
            {
                "x-lab-component": "php",
                "x-lab-runtime": "8.5.12",
                "x-lab-owned-nonce": "a" * 64,
                "x-lab-sqlite": "available",
            },
            b'{"component":"php","synthetic":true}',
            0,
        ),
    )
    with transport.service("php", root, state) as port:
        assert port == 12345 and observed[0].is_dir()
    assert observed[1:] == [
        "terminated-exact-created-child",
        "waited-for-exact-created-child",
    ]
    assert not observed[0].exists()
    receipt = json.loads((state / "php-runtime-context.json").read_bytes())
    assert len(receipt["files"]) == 9 and "nonce" not in json.dumps(receipt)


def test_unproven_exit_lease_survives_context_generator_finalization(runtime):
    """Even explicit generator close cannot recursively remove a namespace leased by an unproven child."""
    root, state = runtime
    context = native_php.isolated_php(root, state, 12345)
    launch = context.__enter__()
    launch.cleanup_permitted = False
    context.gen.close()
    assert launch.root.is_dir()
    assert (launch.root / "runtime/php/php.exe").read_bytes() == (
        root / "runtime/php/php.exe"
    ).read_bytes()


@pytest.mark.parametrize("signal_error", [False, True])
def test_double_timeout_retains_worker_and_bytes_until_exact_child_completion(
    runtime, monkeypatch, signal_error
):
    """Two expired waits and failed signals must neither finish the worker nor delete live owned resources."""
    root, state = runtime
    pending, completed, finished = (threading.Event() for _ in range(3))
    observations, errors = [], []
    monkeypatch.setattr(transport.sys, "frozen", True, raising=False)
    monkeypatch.setattr(transport, "isolated_dll_search", nullcontext)
    monkeypatch.setattr(transport, "free_port", lambda: 12345)
    monkeypatch.setattr(transport.secrets, "token_hex", lambda _: "a" * 64)

    def signal():
        """A concurrently exited/slow child can make a signal unavailable; that is not exit proof."""
        if signal_error:
            raise OSError("inert signal unavailable")

    def create(_arguments, **kwargs):
        """Only the created inert process handle is observed; no compiler, PHP or external process is run."""
        selected = kwargs["cwd"]
        observations.append(selected)
        calls = []

        def wait(timeout):
            """Keep the exact child pending after both original five-second attempts until the test releases it."""
            calls.append(timeout)
            assert selected.is_dir()
            if len(calls) <= 2:
                raise transport.subprocess.TimeoutExpired("inert-owned-child", timeout)
            pending.set()
            if not completed.wait(0.02):
                raise OSError("inert wait still unavailable")
            assert calls[:2] == [5, 5] and all(value == 1 for value in calls[2:])
            return 0

        return SimpleNamespace(
            stderr=io.BufferedReader(io.BytesIO(b"")),
            poll=lambda: None,
            terminate=signal,
            kill=signal,
            wait=wait,
        )

    monkeypatch.setattr(transport.subprocess, "Popen", create)
    monkeypatch.setattr(
        transport,
        "request",
        lambda *_: (
            200,
            {
                "x-lab-component": "php",
                "x-lab-runtime": "8.5.12",
                "x-lab-owned-nonce": "a" * 64,
                "x-lab-sqlite": "available",
            },
            b'{"component":"php","synthetic":true}',
            0,
        ),
    )

    def worker():
        """Represent the retained GUI worker: returning would release its profile/stage ownership."""
        try:
            with transport.service("php", root, state):
                pass
        except BaseException as error:
            errors.append(error)
        finally:
            finished.set()

    thread = threading.Thread(target=worker)
    thread.start()
    try:
        assert pending.wait(3), errors
        assert thread.is_alive() and not finished.is_set()
        assert observations[0].is_dir()
        assert (observations[0] / "runtime/php/php8.dll").is_file()
    finally:
        completed.set()
        thread.join(3)
    assert not thread.is_alive() and finished.is_set() and errors == []
    assert not observations[0].exists()
