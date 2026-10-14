"""Jason Stys: generate exact definition/variable line maps and verify Python function/class contracts."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 49
# definition: mapped — line 52
# parameter: source — line 52
# parameter: suffix — line 52
# variable: prefix — line 54
# variable: begin — line 61
# variable: end — line 61
# variable: source — line 62
# variable: lines — line 68
# variable: records — line 69
# variable: tree — line 71
# variable: first — line 72
# variable: insertion — line 73
# variable: node — line 80
# variable: insertion — line 92
# variable: insertion — line 94
# variable: line — line 95
# variable: number — line 95
# variable: name — line 98
# variable: name — line 100
# variable: name — line 102
# variable: name — line 104
# variable: name — line 107
# variable: name — line 111
# variable: name — line 116
# variable: count — line 118
# variable: header — line 119
# variable: kind — line 123
# variable: name — line 123
# variable: number — line 123
# parameter: item — line 124
# definition: main — line 133
# variable: parser — line 135
# variable: args — line 137
# variable: paths — line 138
# variable: stale — line 152
# variable: path — line 153
# variable: original — line 154
# variable: expected — line 155
# END CODE MAP

import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mapped(source: str, suffix: str) -> str:
    """Parse Python AST or declarative SQL/YAML/shell symbols without executing any authored source."""
    prefix = (
        "--"
        if suffix == ".sql"
        else "//"
        if suffix in {".java", ".cs", ".php"}
        else "#"
    )
    begin, end = prefix + " BEGIN CODE MAP", prefix + " END CODE MAP"
    source = re.sub(
        r"^" + re.escape(begin) + r"[^\n]*\n.*?^" + re.escape(end) + r"\n",
        "",
        source,
        flags=re.M | re.S,
    )
    lines = source.splitlines(keepends=True)
    records = set()
    if suffix == ".py":
        tree = ast.parse(source)
        first = tree.body[0] if tree.body else None
        insertion = (
            first.end_lineno
            if isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
            else 0
        )
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    raise ValueError(f"Missing function/class description: {node.name}")
                records.add(("definition", node.name, node.lineno))
            elif isinstance(node, ast.arg):
                records.add(("parameter", node.arg, node.lineno))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                records.add(("variable", node.id, node.lineno))
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                records.add(("attribute", node.attr, node.lineno))
    else:
        insertion = 1 if source.startswith(("#!", "<?php", "/**", "//")) else 0
        while insertion < len(lines) and lines[insertion].startswith(prefix):
            insertion += 1
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith(prefix):
                continue
            for name in re.findall(r"^\s*(?:- )?([\w-]+):", line):
                records.add(("parameter", name, number))
            for name in re.findall(r"CREATE (?:TABLE|TRIGGER|INDEX) (\w+)", line):
                records.add(("SQL object", name, number))
            for name in re.findall(r"\b(\w+) (?:INTEGER|TEXT|BLOB)\b", line):
                records.add(("column", name, number))
            for name in re.findall(r"\$([A-Za-z_][A-Za-z0-9_]*)", line):
                records.add(("variable", name, number))
            if suffix in {".java", ".cs", ".php"}:
                for name in re.findall(
                    r"\b(?:class|record|interface)\s+([A-Za-z_]\w*)", line
                ):
                    records.add(("definition", name, number))
                for name in re.findall(
                    r"\b(?:function|void|int|string|bool|String|boolean|long|var|Principal|Note|Broker|PDO|TimeSpan)\s+([A-Za-z_]\w*)",
                    line,
                ):
                    records.add(("symbol", name, number))
                for name in re.findall(r"\b([A-Za-z_]\w*)\s*=(?!=)", line):
                    records.add(("variable", name, number))
    count = len(records) + 2
    header = [
        begin + " (generated; python scripts/code_map.py)",
        *[
            f"{prefix} {kind}: {name} — line {number + count if number > insertion else number}"
            for kind, name, number in sorted(
                records, key=lambda item: (item[2], item[0], item[1])
            )
        ],
        end,
    ]
    lines.insert(insertion, "\n".join(header) + "\n")
    return "".join(lines)


def main() -> int:
    """Generate/check all authored Python and operational declarative files; stale headers fail CI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    paths = [
        *(ROOT / "asrl").glob("*.py"),
        *(ROOT / "scripts").glob("*.py"),
        *(ROOT / "tests").glob("*.py"),
        *(ROOT / "scripts").glob("*.sh"),
        *(ROOT / ".github/workflows").glob("*.yml"),
        *(ROOT / "sql").glob("*.sql"),
        *(ROOT / "services/java").glob("*.java"),
        *(ROOT / "services/session").glob("*.cs"),
        *(ROOT / "services/php").glob("*.php"),
        *(ROOT / "tests/java").glob("*.java"),
        *(ROOT / "tests/session").glob("*.cs"),
        *(ROOT / "tests/php").glob("*.php"),
    ]
    stale = []
    for path in paths:
        original = path.read_text(encoding="utf-8")
        expected = mapped(original, path.suffix)
        if original != expected:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(expected, encoding="utf-8", newline="\n")
    print("Code maps current" if not stale else "Code maps: " + ", ".join(stale))
    return int(args.check and bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
