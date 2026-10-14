#!/usr/bin/env bash
# Jason Stys: strict conformance/evidence core and complete maintained source/documentation gates.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# END CODE MAP
set -euo pipefail
mkdir -p out
python -m ruff check asrl scripts tests
python -m ruff format --check asrl scripts tests
python -m mypy
python -m pytest --cov=asrl --cov-report=term-missing --cov-report=json:out/coverage.json
python scripts/code_map.py --check
python scripts/file_guide.py --check
python scripts/validate_repo.py
npm run code-map:check
npm run format:check
