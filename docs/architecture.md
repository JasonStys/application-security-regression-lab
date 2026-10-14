# ADR-001: independent native boundaries, not a fake production federation

Status: accepted. Date: 2026-10-14. Author/decider: Jason Stys.

## Context

Demonstrate security reasoning in Java, C#, PHP and JavaScript with observable expected versus actual outcomes. Avoid unsafe public services, real identities and decorative language wrappers. The local machine lacks Java/PHP; native hosted jobs supply those checks without modifying Docker.

## Decision

Four focused loopback adapters, each backed by real native code: Java tenant/operation/revision policy; C# ephemeral sessions; PHP PDO/SQLite literal queries/text-upload quotas; Node/TypeScript literal DOM. A Python-owned runner starts selected processes, verifies component identity, evaluates exact statuses/content/headers, then terminates only its children and emits inert evidence.

    Native core assertions + test-only vulnerable comparisons
                      ↓
    Actual corrected loopback HTTP services → expected/observed cases
                      ↓
    Strict evidence schema → JSON/hash/inert HTML

Browser UI tests separately execute actual DOM behavior. It does not pretend to unify independent services or authenticate real users. Test comparisons never become server modes/routes.

## Options/tradeoffs

One generic Python simulator is faster but cannot prove native-language behavior. A production multi-service app adds identity federation, signed tokens, TLS, storage/tenant and operational duties outside a portfolio exercise. Containers are reproducible but not needed for these platform-only examples and local Docker remains unchanged. Native CI verifies actual compilers and PDO instead.

## Consequences

Native dependency surface is small, boundaries/readability clear, and expected failures remain observable. Four contracts require separate tests. No claim of complete ASVS compliance, real authentication, public gateway robustness or shared/federated identity. Revisit managed identity, TLS/proxy timeouts, encrypted state and operational review before any real-data/public use; changing the bind address is not an upgrade path.
