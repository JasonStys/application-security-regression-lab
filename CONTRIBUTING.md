# Contributing

Author: Jason Stys. Use owned synthetic state only. Never add real account/password handling, public exposure, target URL options, unsafe HTTP modes or test imports into served code without a separate approved design.

Describe each function/class and meaningful boundaries. Use small typed modules/explicit limits and checked symbol headers. After edits: Ruff format/lint, dotnet format whitespace, Prettier; regenerate python scripts/code_map.py and npm run code-map. Stage reviewed nonprivate files, then python scripts/file_guide.py. Recheck format/maps for stable exact lines and run all native/core/browser/HTTP/security gates.

Record actual failures/fixes/results, not canned success. Do not lower coverage, ignore CodeQL findings or disable protections. JSON/config/lock purposes reside in README because comments are not valid JSON.
