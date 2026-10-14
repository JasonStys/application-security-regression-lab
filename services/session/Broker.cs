// Jason Stys: bounded random-token lifecycle with hashed storage, explicit expiry, revocation and fixture scope.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: Principal — line 38
// symbol: Role — line 38
// symbol: Tenant — line 38
// definition: Broker — line 41
// symbol: capacity — line 41
// symbol: lifetime — line 41
// variable: capacity — line 41
// definition: Entry — line 43
// symbol: Issued — line 43
// symbol: Principal — line 43
// variable: entries — line 44
// variable: gate — line 45
// variable: Fixtures — line 46
// symbol: Issue — line 55
// symbol: principal — line 55
// symbol: key — line 61
// variable: pair — line 61
// symbol: token — line 65
// variable: token — line 65
// symbol: key — line 79
// variable: key — line 79
// symbol: Revoke — line 92
// symbol: Expired — line 101
// symbol: age — line 103
// variable: age — line 103
// symbol: Fingerprint — line 108
// symbol: token — line 108
// END CODE MAP
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

namespace SessionLab;

/// <summary>An asserted synthetic principal; tenant/role never come from resource requests.</summary>
internal sealed record Principal(string Tenant, string Role);

/// <summary>Opaque 256-bit sessions. Clock and TTL are injected for deterministic boundary tests.</summary>
internal sealed class Broker(TimeProvider clock, TimeSpan lifetime, int capacity = 100)
{
    private sealed record Entry(Principal Principal, long Issued);
    private readonly Dictionary<string, Entry> entries = new(StringComparer.Ordinal);
    private readonly object gate = new();
    private static readonly IReadOnlyDictionary<string, Principal> Fixtures =
        new Dictionary<string, Principal>
        {
            ["alpha-owner"] = new("alpha", "owner"),
            ["alpha-viewer"] = new("alpha", "viewer"),
            ["beta-owner"] = new("beta", "owner")
        };

    /// <summary>Issue only closed synthetic identities; reject capacity and never accept an old/client token.</summary>
    internal string Issue(string principal)
    {
        if (!Fixtures.TryGetValue(principal, out Principal? identity))
            throw new ArgumentException("fixture_identity");
        lock (gate)
        {
            foreach (string key in entries.Where(pair => Expired(pair.Value)).Select(pair => pair.Key).ToArray())
                entries.Remove(key);
            if (entries.Count >= capacity)
                throw new InvalidOperationException("session_capacity");
            string token = Convert.ToBase64String(RandomNumberGenerator.GetBytes(32))
                .TrimEnd('=').Replace('+', '-').Replace('/', '_');
            entries.Add(Fingerprint(token), new(identity, clock.GetTimestamp()));
            return token;
        }
    }

    /// <summary>Resolve a well-shaped token only while live; expiration permanently removes the fingerprint.</summary>
    internal Principal? Resolve(string? token)
    {
        if (token is null || !Regex.IsMatch(token, "^[A-Za-z0-9_-]{43}$", RegexOptions.CultureInvariant))
            return null;
        lock (gate)
        {
            string key = Fingerprint(token);
            if (!entries.TryGetValue(key, out Entry? entry))
                return null;
            if (Expired(entry))
            {
                entries.Remove(key);
                return null;
            }
            return entry.Principal;
        }
    }

    /// <summary>Revoke exactly the presented session; missing/unknown tokens are harmless, never affect peers.</summary>
    internal void Revoke(string? token)
    {
        if (token is null)
            return;
        lock (gate)
            entries.Remove(Fingerprint(token));
    }

    /// <summary>Use monotonic elapsed time, inclusive expiry and fail closed on a clock that moves backward.</summary>
    private bool Expired(Entry entry)
    {
        TimeSpan age = clock.GetElapsedTime(entry.Issued, clock.GetTimestamp());
        return age < TimeSpan.Zero || age >= lifetime;
    }

    /// <summary>Store only SHA256 fingerprints of high-entropy tokens, never plaintext cookie values.</summary>
    private static string Fingerprint(string token) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(token)));
}
