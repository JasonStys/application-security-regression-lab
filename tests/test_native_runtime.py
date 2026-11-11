"""Independent bundled-runtime boundaries without executing any fixture or modifying global tools. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: manifest — line 62
# parameter: tmp_path — line 62
# variable: rows — line 64
# variable: index — line 65
# variable: name — line 65
# variable: path — line 68
# variable: raw — line 70
# variable: value — line 75
# definition: test_fixed_commands_and_cleared_injection_environment — line 80
# parameter: manifest — line 80
# parameter: monkeypatch — line 80
# variable: root — line 82
# variable: value — line 82
# variable: name — line 84
# variable: command — line 85
# variable: item — line 87
# variable: key — line 88
# variable: environment — line 98
# definition: test_manifest_path_refusal — line 135
# parameter: manifest — line 135
# parameter: name — line 135
# variable: root — line 137
# variable: value — line 137
# definition: test_manifest_identity_and_closed_schema — line 160
# parameter: manifest — line 160
# parameter: mutation — line 160
# variable: root — line 162
# variable: value — line 162
# variable: row — line 170
# variable: path — line 185
# definition: test_total_bound_and_entry_shape_are_independently_enforced — line 192
# parameter: manifest — line 192
# parameter: monkeypatch — line 192
# variable: root — line 194
# variable: value — line 194
# definition: test_missing_fixed_program_cannot_be_replaced_by_an_extra_program — line 205
# parameter: manifest — line 205
# variable: root — line 207
# variable: value — line 207
# variable: row — line 208
# variable: before — line 209
# definition: test_missing_authored_sql_schema_fails_before_service_start — line 217
# parameter: manifest — line 217
# variable: root — line 219
# variable: value — line 219
# variable: row — line 221
# END CODE MAP

import hashlib
import json
import os

import pytest

from asrl import native_runtime as module
from asrl.desktop_io import Rejected


@pytest.fixture
def manifest(tmp_path):
    """Actual inert program/data files establish identity; fake program bytes are never executed."""
    rows = []
    for index, name in enumerate(
        [*module.ENTRYPOINTS.values(), *sorted(module.REQUIRED_DATA)]
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = b"inert fixture " + bytes([index])
        path.write_bytes(raw)
        rows.append(
            {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        )
    value = {"schema": 1, "entries": rows}
    (tmp_path / "runtime-manifest.json").write_text(json.dumps(value))
    return tmp_path, value


def test_fixed_commands_and_cleared_injection_environment(manifest, monkeypatch):
    """A manifest cannot choose executable argv; provider/runtime configuration is absent from the child."""
    root, value = manifest
    assert module.validate(root) == value
    for name in module.ENTRYPOINTS:
        command = module.command(name, root, root / "scratch", 12345)
        assert command[0] == str(root / module.ENTRYPOINTS[name])
        assert all("evil.invalid" not in item for item in command)
    for key in (
        "OPENAI_API_KEY",
        "AWS_SECRET_ACCESS_KEY",
        "JAVA_TOOL_OPTIONS",
        "NODE_OPTIONS",
        "PHPRC",
        "DOTNET_ADDITIONAL_DEPS",
        "PYTHONPATH",
    ):
        monkeypatch.setenv(key, "private inert fixture")
    environment = module.environment(root / "scratch")
    assert set(environment) <= {
        "SYSTEMROOT",
        "WINDIR",
        "TEMP",
        "TMP",
        "PATH",
        "ASRL_PHP_DB",
        "DOTNET_EnableDiagnostics",
        "DOTNET_ROLL_FORWARD",
        "DOTNET_CLI_HOME",
        "HOME",
        "USERPROFILE",
        "DOTNET_MULTILEVEL_LOOKUP",
    }
    assert environment["ASRL_PHP_DB"] == str(root / "scratch/php.sqlite")
    assert environment["DOTNET_ROLL_FORWARD"] == "Disable"
    with pytest.raises(Rejected):
        module.command("arbitrary-command", root, root, 12345)
    with pytest.raises(Rejected):
        module.command("java", root, root, True)


@pytest.mark.parametrize(
    "name",
    [
        "../escape.exe",
        "/runtime/x.exe",
        "runtime/../escape.exe",
        "runtime//x.exe",
        "runtime/x:ads",
        "runtime\\x.exe",
        "source/foreign.exe",
        "runtime/./x.exe",
        "runtime/x\x00.exe",
    ],
)
def test_manifest_path_refusal(manifest, name):
    """Cross-platform traversal, alternate streams and unauthored source prefixes fail before any executable admission."""
    root, value = manifest
    value["entries"][0]["path"] = name
    (root / "runtime-manifest.json").write_text(json.dumps(value))
    with pytest.raises(Rejected):
        module.validate(root)


@pytest.mark.parametrize(
    "mutation",
    [
        "schema-bool",
        "extra",
        "empty",
        "duplicate",
        "case-alias",
        "size-bool",
        "oversize",
        "bad-hash",
        "changed-bytes",
        "missing-entrypoint",
        "hardlink",
    ],
)
def test_manifest_identity_and_closed_schema(manifest, mutation):
    """Actual bytes and closed inventory matter, not labels or a caller-reported success field."""
    root, value = manifest
    if mutation == "schema-bool":
        value["schema"] = True
    elif mutation == "extra":
        value["accepted"] = True
    elif mutation == "empty":
        value["entries"] = []
    elif mutation in ("duplicate", "case-alias"):
        row = dict(value["entries"][0])
        if mutation == "case-alias":
            row["path"] = row["path"].upper()
        value["entries"].append(row)
    elif mutation == "size-bool":
        value["entries"][0]["bytes"] = True
    elif mutation == "oversize":
        value["entries"][0]["bytes"] = module.MAX_RESOURCE + 1
    elif mutation == "bad-hash":
        value["entries"][0]["sha256"] = "g" * 64
    elif mutation == "changed-bytes":
        (root / value["entries"][0]["path"]).write_bytes(b"changed")
    elif mutation == "missing-entrypoint":
        value["entries"][0]["path"] = "runtime/other.exe"
    elif mutation == "hardlink":
        path = root / value["entries"][0]["path"]
        os.link(path, root / "outside-fixture")
    (root / "runtime-manifest.json").write_text(json.dumps(value))
    with pytest.raises((Rejected, OSError)):
        module.validate(root)


def test_total_bound_and_entry_shape_are_independently_enforced(manifest, monkeypatch):
    """Actual closed entries cannot evade the aggregate ceiling or masquerade as typed per-file identities."""
    root, value = manifest
    monkeypatch.setattr(module, "MAX_TOTAL", 1)
    with pytest.raises(Rejected, match="total"):
        module.validate(root)
    monkeypatch.setattr(module, "MAX_TOTAL", 768 * 1024 * 1024)
    value["entries"][0] = {"path": "runtime/unknown"}
    (root / "runtime-manifest.json").write_text(json.dumps(value))
    with pytest.raises(Rejected, match="entry"):
        module.validate(root)


def test_missing_fixed_program_cannot_be_replaced_by_an_extra_program(manifest):
    """Even correctly hashed inert bytes at a different relative name cannot become a new native entrypoint."""
    root, value = manifest
    row = value["entries"][0]
    before = root / row["path"]
    row["path"] = "runtime/java/bin/foreign.exe"
    before.rename(root / row["path"])
    (root / "runtime-manifest.json").write_text(json.dumps(value))
    with pytest.raises(Rejected, match="entrypoint"):
        module.validate(root)


def test_missing_authored_sql_schema_fails_before_service_start(manifest):
    """The real first candidate's omitted-schema defect must be detected even when all four program hashes are valid."""
    root, value = manifest
    value["entries"] = [
        row for row in value["entries"] if row["path"] != "sql/schema.sql"
    ]
    (root / "runtime-manifest.json").write_text(json.dumps(value))
    with pytest.raises(Rejected, match="required_data_missing"):
        module.validate(root)
