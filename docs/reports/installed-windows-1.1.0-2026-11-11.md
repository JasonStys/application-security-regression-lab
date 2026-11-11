# Installed Windows 1.1.0 validation - 11 November 2026

By Jason Stys. Observations below refer to the independently downloaded, published **1.1.0** application built from `34e40cf6657f3f1ddf8f9d059b5d09ab3c1b193c`. Historical Office editions and published assets remain unchanged.

## Observed validation

**Actual installed workflows: Passed.** Eight real installed workflows retained eight exact bundles; all 150 mandatory HTTP assertions across four actual services passed. Both installed launches ended normally.

**Original core and source gates: Passed.** 208 source tests and original Java/C#/PHP/Node cases, browser journeys, static types and dependency checks passed. The 95% source-coverage floor was retained; measured aggregate was 95.60%.

**Assets and current security: Passed.** Provider/download hashes, complete installed-byte identity, current exact-main workflows and processed raw CodeQL results passed with zero open main alerts.

**Launch and data boundary: Passed.** Individual Desktop and Start-menu targets verified. Only synthetic profiles were exercised; installed EXE tests are distinct from ordinary default-profile shortcut activation.

## Illustrated workflow and implementation

The [four-page application guide](windows-application-guide-1.1.0.docx) contains two actual installed-app screenshots, a worked user journey, an immutable-source excerpt and observed results/limits. Every final page was peer-reviewed and OOXML schema validation passed. The [manifest](windows-application-guide-1.1.0.json) binds the document, figures, source and reviewed pages. Prepared examples are inputs inside the actual application.

## Installation, data and limits

Download the AppSec Windows EXE, its SHA-256 sidecar, runtime notices and project license. Verify the hash and launch the one-file EXE. Keep notices, stopped-profile backups and earlier app versions.

Use the individual Desktop icon and the app's Help. Quit through its owner controls. No Python setup or Docker change is required; examples are input data inside the full application.

This is an owner-local synthetic/reference regression workbench, not a general production scanner, identity service, ASVS certification or guarantee of secure third-party code.

Unsigned Windows x64 portable app; saved evidence is plaintext trusted-OS-owner data. JRE source/build references and original runtime terms are retained; no whole-JDK rebuild or legal-certification claim.

Individual Desktop and Start-menu targets were read-back verified. Actual installed-executable testing is distinct from ordinary default-profile shortcut activation, which was not independently exercised. Normal profiles and Docker were unchanged. This documentation revision requires its own fresh hosted workflows and processed security analysis; earlier runtime observations do not certify future source.
