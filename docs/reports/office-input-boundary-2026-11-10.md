# Documentation input boundary review — 2026-11-10

By Jason Stys. This is a repository documentation-policy correction, not an application-runtime or released-download change.

## Observation and correction

The Word documentation reader rejected encrypted members and VBA payloads but did not reject a non-XML embedded-package member. Its XML-only privacy inspection would therefore leave that binary part uninspected. The reader does not execute Office files; this observation is not evidence of application code execution. Independent inspection found no VBA, OLE or embedded-package parts in the actual published guide.

The same existing guard now refuses any member whose case-normalized name contains `/embeddings/`. An actual inert ZIP fixture containing `word/embeddings/inert.bin` must raise an error rather than become empty or silently skipped text. Ordinary Word XML and relationships remain visible to the original credential patterns. All original workflow and source checks remain enabled.

## Observed local validation

- `63` Python tests passed, including six real Word/privacy cases; combined runtime statement/branch coverage was **98.54%**, retaining the 95% floor for `asrl`.
- Ruff lint and formatting, strict mypy, and regenerated source locations passed. The negative cases cover missing main XML, a macro part, an embedded package, invalid UTF-8 and excessive expansion; the positive case checks actual XML/relationship visibility.
- These observations concern the local corrective candidate derived from [main `8ae8432407a17d538068cc4ee0f5bc226d9d20d7`](https://github.com/JasonStys/application-security-regression-lab/tree/8ae8432407a17d538068cc4ee0f5bc226d9d20d7). Hosted checks on the final commit are separate required evidence; this report does not declare them passed in advance.

## Scope and limits

Reviewed Word bytes and their immutable source/page-review manifest are unchanged. This scanner reads documentation as bounded text for repository checks; it is not an Office antivirus engine, complete DLP system or proof that arbitrary documents are safe. Existing application and native acceptance lanes continue to test their own contracts.
