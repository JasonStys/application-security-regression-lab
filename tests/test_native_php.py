"""Actual whole-bundle admission, fixed same-byte PHP copies and child-before-cleanup ownership. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: runtime — line 96
# parameter: tmp_path — line 96
# variable: root — line 98
# variable: state — line 99
# variable: entries — line 102
# variable: index — line 103
# variable: name — line 103
# variable: path — line 110
# variable: raw — line 112
# definition: test_actual_copy_binds_original_bytes_and_closed_argv_environment — line 123
# parameter: monkeypatch — line 124
# parameter: runtime — line 124
# variable: root — line 127
# variable: state — line 127
# variable: original — line 130
# variable: p — line 132
# variable: launch — line 135
# variable: selected — line 136
# variable: row — line 161
# variable: p — line 170
# definition: test_partial_or_changed_source_never_becomes_a_new_trust_root — line 185
# parameter: fault — line 185
# parameter: runtime — line 185
# variable: root — line 187
# variable: state — line 187
# variable: manifest — line 188
# variable: port — line 189
# variable: row — line 193
# variable: row — line 202
# variable: port — line 211
# variable: state — line 213
# definition: test_late_source_change_rejected_and_only_owned_copy_cleaned — line 220
# parameter: monkeypatch — line 220
# parameter: runtime — line 220
# variable: root — line 222
# variable: state — line 222
# variable: actual — line 223
# definition: changed — line 225
# parameter: limit — line 225
# parameter: path — line 225
# definition: test_copied_bytes_and_manifest_observation_cannot_silently_diverge — line 241
# parameter: fault — line 242
# parameter: monkeypatch — line 242
# parameter: runtime — line 242
# variable: root — line 245
# variable: state — line 245
# variable: actual — line 246
# definition: altered — line 248
# parameter: limit — line 248
# parameter: path — line 248
# definition: test_unexpected_context_error_cleans_only_owned_namespace — line 266
# parameter: runtime — line 266
# variable: root — line 268
# variable: state — line 268
# variable: launch — line 270
# variable: copied — line 271
# definition: test_changed_owner_marker_refuses_cleanup_of_unknown_replacement — line 277
# parameter: runtime — line 277
# variable: root — line 279
# variable: state — line 279
# variable: launch — line 281
# variable: selected — line 282
# definition: test_real_copy_service_waits_for_exact_owned_child_before_removal — line 287
# parameter: monkeypatch — line 288
# parameter: runtime — line 288
# variable: root — line 291
# variable: state — line 291
# variable: observed — line 292
# parameter: _count — line 296
# definition: launch — line 298
# parameter: argv — line 298
# parameter: kwargs — line 298
# variable: selected — line 300
# definition: wait — line 306
# parameter: _kwargs — line 306
# parameter: _args — line 322
# variable: port — line 334
# variable: receipt — line 341
# END CODE MAP

import hashlib
import io
import json
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
