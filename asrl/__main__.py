"""Jason Stys: explicit component/all conformance runner and new-directory inert reports; owned synthetic fixtures only."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 30
# definition: main — line 33
# parameter: argv — line 33
# variable: parser — line 35
# variable: args — line 47
# variable: output — line 49
# variable: path — line 52
# variable: source — line 57
# variable: source — line 65
# variable: cases — line 66
# variable: component — line 67
# variable: port — line 70
# variable: report — line 72
# variable: case — line 82
# variable: successes — line 82
# END CODE MAP

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from .cases import exercise
from .evidence import COMPONENTS, LabError, canonical, passed, render, validate
from .transport import service

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    """Run only selected native fixture adapters and fail nonzero if any expected security boundary disagrees."""
    parser = argparse.ArgumentParser(
        description="Jason Stys AppSec regression evidence; no external-target option"
    )
    parser.add_argument(
        "--component", choices=["all", *sorted(COMPONENTS)], default="all"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New private result directory, existing parents only",
    )
    args = parser.parse_args(argv)
    try:
        output = args.output.absolute()
        if any(
            path.is_symlink() or path.is_junction()
            for path in (output, *output.parents)
        ):
            raise LabError("linked_output")
        output.mkdir(mode=0o700)
        try:
            source = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL
                )
                .decode()
                .strip()
            )
        except subprocess.CalledProcessError:
            source = "uncommitted"
        cases = []
        for component in (
            sorted(COMPONENTS) if args.component == "all" else [args.component]
        ):
            with service(component, ROOT, output) as port:
                cases.extend(exercise(component, port))
        report = validate(
            {
                "schema": 1,
                "source": source,
                "note": "Owned loopback synthetic fixtures only; independent services, not a certified system. Native core and browser results are separate. No external target accepted.",
                "cases": cases,
            }
        )
        (output / "http.json").write_bytes(canonical(report))
        (output / "http.html").write_text(render(report), encoding="utf-8")
        successes = sum(passed(case) for case in cases)
        print(
            f"Actual HTTP cases: {successes}/{len(cases)} passed; private reports saved locally"
        )
        return 0 if successes == len(cases) else 1
    except (OSError, LabError, subprocess.SubprocessError):
        print(
            "Rejected: owned_fixture_or_report_failed; check installed native runtimes and build commands"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
