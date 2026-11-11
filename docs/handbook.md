# Application Security Regression Lab handbook

By Jason Stys.

Compare exact saved HTTP regression evidence across union cases, including missing execution and changed assertions.

Prevents an absent or weakened test from being reported as an application-security recovery.

## Read the documentation

| Edition                                          | Audience and contents                                                                       |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [runbook](runbook.md)
- [Windows graphical application](windows-application.md)
- [Native runtime sources and notices](native-dependencies.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)

### Security and validation

- [security](security.md)
- [testing](testing.md)

## Historical results and reproduction

The reviewed source is [`4466fed1ebed0c538cc2ea35d96c92c6299b96bf`](https://github.com/JasonStys/application-security-regression-lab/tree/4466fed1ebed0c538cc2ea35d96c92c6299b96bf). The observed functional workflow baseline is `4466fed1ebed0c538cc2ea35d96c92c6299b96bf`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/regression-review-2026-11-09.md)
- [Native workbench acceptance — 2026-11-11](reports/native-workbench-2026-11-11.md)
- [Current Actions](https://github.com/JasonStys/application-security-regression-lab/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Comparison covers saved HTTP evidence; matching labels do not prove that test implementations or assertions are equivalent.
- Missing execution and changed assertions remain distinct from verified application-security recovery.
- It is not a chronology guarantee, latency benchmark or universal application-security assessment.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
