# Primary sources and selected control references

Reviewed 2026-10-14 by Jason Stys. Standards references guide specific testable boundaries, not certification or full requirements coverage.

- [OWASP ASVS 5.0.0](https://owasp.org/projects/asvs): selected themes—server-side authorization, session lifecycle, injection prevention and permitted file handling. The lab's cases are its own synthetic examples; no complete ASVS requirements text copied. References use a fixed version because identifiers can change.
- [PDO prepared statements](https://www.php.net/manual/en/pdo.prepared-statements.php): bind data values, never construct SQL structure from untrusted inputs. Literal LIKE handling is separate from SQL syntax protection.
- [PHP development server](https://www.php.net/manual/en/features.commandline.webserver.php): appropriate for isolated exercises, not production network hosting.
- [JDK HttpServer](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html): explicit loopback binding and executor; context-prefix matching motivates exact path checks.
- [Microsoft RandomNumberGenerator](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.randomnumbergenerator?view=net-10.0), [Kestrel limits](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel?view=aspnetcore-10.0): established entropy/platform controls; no custom cryptographic algorithm.
- [Node HTTP](https://nodejs.org/docs/latest-v24.x/api/http.html), [OWASP DOM XSS](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html): safe text sinks/explicit routes/headers complement runtime JSON validation. CSP is defense in depth, not the sole protection.
- [GitHub maintained Ubuntu runner image](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md): real PHP/SQLite and compiler availability; workflow versions still explicitly selected.
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions): included usage differs from live artifact/cache occupancy. No artifact/cache uploads here; logs/security results remain distinct.

Source changes/upstream versions can alter results. Native tests and accepted-source reports are evidence of these bounded implementations, not real-world identity or public-gateway assurance.
