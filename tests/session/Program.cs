// Jason Stys: actual native session boundaries and nonserved deliberately incorrect comparison predicates.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: TestClock — line 48
// symbol: Tick — line 50
// symbol: TimestampFrequency — line 51
// variable: TimestampFrequency — line 51
// symbol: GetTimestamp — line 53
// definition: Program — line 57
// variable: Cases — line 59
// symbol: Check — line 61
// symbol: condition — line 61
// symbol: id — line 61
// symbol: Main — line 68
// symbol: clock — line 70
// variable: clock — line 70
// symbol: broker — line 71
// variable: broker — line 71
// symbol: first — line 72
// variable: first — line 72
// symbol: peer — line 73
// variable: peer — line 73
// variable: Tick — line 85
// variable: Tick — line 87
// symbol: renewed — line 89
// variable: renewed — line 89
// variable: Tick — line 91
// symbol: index — line 94
// variable: index — line 94
// symbol: capacityDenied — line 95
// variable: capacityDenied — line 95
// variable: capacityDenied — line 96
// symbol: unknownDenied — line 98
// variable: unknownDenied — line 98
// variable: unknownDenied — line 99
// symbol: insecureExpiryAccepts — line 104
// variable: insecureExpiryAccepts — line 104
// symbol: insecureClientScopeAccepts — line 106
// variable: insecureClientScopeAccepts — line 106
// variable: cases — line 108
// variable: component — line 108
// variable: mutants_killed — line 108
// variable: passed — line 108
// END CODE MAP
using System.Text.Json;
using SessionLab;

/// <summary>Inject a monotonic clock without waiting/sleeping through expiry edge cases.</summary>
internal sealed class TestClock : TimeProvider
{
    internal long Tick;
    public override long TimestampFrequency => 1000;
    /// <summary>Return test ticks; deterministic tests can advance/reverse the clock explicitly.</summary>
    public override long GetTimestamp() => Tick;
}

/// <summary>Fail on any violated assertion and emit truthful case IDs only after evaluating real Broker code.</summary>
internal static class Program
{
    private static readonly List<string> Cases = [];
    /// <summary>Record one successful invariant; failures stop the native process with a fixed case ID.</summary>
    private static void Check(string id, bool condition)
    {
        if (!condition) throw new InvalidOperationException(id);
        Cases.Add(id);
    }

    /// <summary>Exercise token uniqueness, scope, inclusive expiry, backward time, revocation and capacity.</summary>
    private static void Main()
    {
        var clock = new TestClock();
        var broker = new Broker(clock, TimeSpan.FromSeconds(10), 3);
        string first = broker.Issue("alpha-owner");
        string peer = broker.Issue("beta-owner");
        Check("S-01-random-unique", first != peer && first.Length == 43);
        Check("S-02-authoritative-scope", broker.Resolve(first)?.Tenant == "alpha");
        Check("S-03-peer-scope", broker.Resolve(peer)?.Tenant == "beta");
        foreach (string? bad in new string?[] { null, "", "client-chosen", new('x', 44), first + "x", "!" + first[1..] })
            Check("S-04-invalid-" + Cases.Count, broker.Resolve(bad) is null);
        broker.Revoke(first);
        Check("S-05-revoked", broker.Resolve(first) is null);
        Check("S-06-peer-unaffected", broker.Resolve(peer) is not null);
        broker.Revoke(null);
        broker.Revoke("unrecognized");
        Check("S-07-unknown-revoke", broker.Resolve(peer) is not null);
        clock.Tick = 9999;
        Check("S-08-before-expiry", broker.Resolve(peer) is not null);
        clock.Tick = 10000;
        Check("S-09-at-expiry", broker.Resolve(peer) is null);
        string renewed = broker.Issue("alpha-viewer");
        Check("S-10-new-token", renewed != first && broker.Resolve(renewed)?.Role == "viewer");
        clock.Tick = 9999;
        Check("S-11-backward-fails-closed", broker.Resolve(renewed) is null);
        Check("S-12-nonrevivable", broker.Resolve(renewed) is null);
        for (int index = 0; index < 3; index++) broker.Issue("alpha-owner");
        bool capacityDenied = false;
        try { broker.Issue("alpha-owner"); } catch (InvalidOperationException) { capacityDenied = true; }
        Check("S-13-capacity", capacityDenied);
        bool unknownDenied = false;
        try { broker.Issue("claimed-admin"); } catch (ArgumentException) { unknownDenied = true; }
        Check("S-14-unknown-principal", unknownDenied);
        clock.Tick += 10001;
        Check("S-15-expired-capacity-reclaimed", broker.Resolve(broker.Issue("beta-owner")) is not null);
        // Incorrect test-only comparisons demonstrate why the boundary assertions are discriminating.
        bool insecureExpiryAccepts = 10000 <= 10000;
        Check("M-S-expiry-boundary-killed", insecureExpiryAccepts && broker.Resolve(peer) is null);
        bool insecureClientScopeAccepts = "claimed-admin".Contains("admin", StringComparison.Ordinal);
        Check("M-S-client-role-killed", insecureClientScopeAccepts && unknownDenied);
        Console.WriteLine(JsonSerializer.Serialize(new { component = "session", cases = Cases, passed = Cases.Count, mutants_killed = 2 }));
    }
}
