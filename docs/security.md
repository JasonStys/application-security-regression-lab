# Threat model and review boundaries

Author: Jason Stys. Assets are fictional records and transient fixture sessions. Trusted operator, OS and native runtimes; no real credentials/HR/business data or public hosting.

| Threat | Control | Residual limit |
| --- | --- | --- |
| Cross-tenant read/write | authoritative native principal, tenant check, uniform missing/cross404 | fixture selectors not production identities |
| Forged operation/client role | closed principal tables; exact request schemas; owner checks | local operator can create any synthetic bootstrap identity |
| Stale/revoked/fixed session | cryptographic tokens, fingerprints, monotonic expiry, revocation/uniqueness tests | OS admins/malware/process memory trusted |
| SQL/LIKE injection | PDO parameters, literal wildcards, authoritative tenant | trusted schema/OS/runtime, not every arbitrary SQL query |
| Upload traversal/execution | portable logical .txt names, bounded UTF8, DB text, attachment download | not antivirus; arbitrary/rich file formats unsupported |
| Stored/reflected DOM XSS | runtime shape/byte checks, textContent, CSP, self assets | hostile extensions/host/dependencies outside scope |
| Lost edits/partial quota writes | Java synchronized expected revision; SQLite transaction rollback | process crash/OS/storage faults not certified away |
| Cross-site/request confusion | exact numeric Host/Origin/custom headers, no CORS | local attackers can call loopback; stacks differ in framing |
| Resource exhaustion | byte/count/capacity/time limits; bounded Java executor | small JDK/PHP development servers not public gateways |
| Supply chain/publication | platform-only runtime, exact tool locks/full action SHAs, scans, ignored state | dependency/runtime advisories best effort, no absence proof |

Test-only comparisons intentionally demonstrate chosen defects against isolated synthetic state. They are never imported/served as routes. No scan target, exploit service or unsafe startup switch. No actual victims/equipment touched.

Records/uploads are plaintext synthetic SQLite data; host ownership/ACL controls privacy. Real information must not be entered. No production login, password recovery, encryption, federation, MFA, external AI or telemetry. Logs/results never contain issued session cookies. Console startup URLs/fixture IDs are nonsecret.

CodeQL supports Python/JavaScript/Java/C# here, not PHP. Native PHP syntax and real PDO tests plus manual parameter/tenant/upload review are explicit complementary checks—not a claim PHP was analyzed by CodeQL. Do not suppress findings or weaken guards for green CI. No compliance/security certification.
