/** Jason Stys: native tenant, operation, form/JSON and edit-race tests, plus nonserved insecure comparisons. */
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: PolicyTests — line 55
// variable: CASES — line 56
// symbol: check — line 58
// symbol: condition — line 58
// symbol: id — line 58
// symbol: denied — line 63
// symbol: id — line 63
// symbol: status — line 63
// symbol: rejected — line 64
// variable: rejected — line 64
// variable: rejected — line 65
// symbol: main — line 69
// variable: policy — line 70
// symbol: owner — line 71
// variable: owner — line 71
// symbol: viewer — line 72
// variable: viewer — line 72
// symbol: beta — line 73
// variable: beta — line 73
// symbol: bad — line 83
// variable: src — line 88
// symbol: bad — line 90
// variable: a — line 90
// variable: c — line 90
// variable: e — line 90
// variable: g — line 90
// variable: i — line 90
// variable: id — line 90
// variable: k — line 90
// variable: m — line 90
// variable: o — line 90
// variable: q — line 90
// variable: body — line 94
// variable: src — line 96
// symbol: workers — line 97
// variable: workers — line 97
// symbol: operations — line 98
// variable: operations — line 98
// symbol: results — line 101
// variable: results — line 101
// symbol: insecureTenantAccepts — line 105
// variable: insecureTenantAccepts — line 105
// symbol: insecureRoleAccepts — line 108
// variable: insecureRoleAccepts — line 108
// symbol: edit — line 115
// symbol: owner — line 115
// END CODE MAP
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;

/** Fail-fast native assertions: successful JSON report is emitted only after every invariant actually holds. */
final class PolicyTests {
    private static final List<String> CASES = new ArrayList<>();
    /** Evaluate one real condition; fixed failure IDs contain no request/token contents. */
    private static void check(String id, boolean condition) {
        if (!condition) throw new AssertionError(id);
        CASES.add(id);
    }
    /** Verify precise safe status while preserving source state on rejected operations. */
    private static void denied(String id, int status, Runnable operation) {
        boolean rejected = false;
        try { operation.run(); } catch (Policy.Failure error) { rejected = error.status == status; }
        check(id, rejected);
    }
    /** Run native positive/negative/race tests without network calls or sensitive input. */
    public static void main(String[] args) throws Exception {
        Policy policy = new Policy();
        var owner = Policy.principal("Bearer fixture-alpha-owner");
        var viewer = Policy.principal("Bearer fixture-alpha-viewer");
        var beta = Policy.principal("Bearer fixture-beta-owner");
        check("J-01-read-own", policy.read(owner, "alpha-note").version() == 1);
        denied("J-02-cross-tenant", 404, () -> policy.read(owner, "beta-note"));
        denied("J-03-unknown-record", 404, () -> policy.read(owner, "missing"));
        denied("J-04-null-principal", 401, () -> policy.read(null, "alpha-note"));
        denied("J-05-bad-id", 400, () -> policy.read(owner, "../alpha"));
        denied("J-06-unknown-token", 401, () -> Policy.principal("claimed-admin"));
        denied("J-07-null-token", 401, () -> Policy.principal(null));
        denied("J-08-viewer-write", 403, () -> policy.update(viewer, "alpha-note", 1, "changed"));
        denied("J-09-cross-write", 404, () -> policy.update(beta, "alpha-note", 1, "changed"));
        for (String bad : new String[] {"", " ", "x\n", "x".repeat(1001)})
            denied("J-10-body-" + CASES.size(), 400, () -> policy.update(owner, "alpha-note", 1, bad));
        denied("J-11-null-body", 400, () -> policy.update(owner, "alpha-note", 1, null));
        denied("J-12-stale-revision", 409, () -> policy.update(owner, "alpha-note", 2, "changed"));
        check("J-13-rejections-atomic", policy.read(owner, "alpha-note").version() == 1);
        check("J-14-literal-content", policy.update(owner, "alpha-note", 1, "<img src=x>").body().equals("<img src=x>"));
        check("J-15-version-advanced", policy.read(owner, "alpha-note").version() == 2);
        for (String bad : new String[] {"id=a&id=b", "id", "=a&=b", "id=%", "id=%GG", "id=%FF", "id=é", "a=b&c=d&e=f&g=h&i=j&k=l&m=n&o=p&q=r", "x".repeat(4097)})
            denied("J-16-form-" + CASES.size(), 400, () -> Policy.form(bad));
        denied("J-17-null-form", 400, () -> Policy.form(null));
        check("J-18-empty-form", Policy.form("").isEmpty());
        check("J-19-unescape-once", Policy.form("body=%253C%2B+%E2%9C%93").get("body").equals("%3C+ ✓"));
        check("J-20-quote", Policy.quote("\"\\\n").equals("\"\\\"\\\\\\u000a\""));
        check("J-21-json-inert", Policy.json(policy.read(owner, "alpha-note")).contains("\"body\":\"<img src=x>\""));
        try (var workers = Executors.newFixedThreadPool(2)) {
            var operations = List.of(
                (java.util.concurrent.Callable<Integer>) () -> edit(policy, owner),
                (java.util.concurrent.Callable<Integer>) () -> edit(policy, owner));
            var results = workers.invokeAll(operations);
            check("J-22-race-one-success", results.get(0).get() + results.get(1).get() == 1);
        }
        // These deliberately incorrect predicates are test-only, not HTTP handlers.
        boolean insecureTenantAccepts = policy.read(owner, "alpha-note") != null;
        denied("M-J-tenant-killed", 404, () -> policy.read(owner, "beta-note"));
        check("M-J-tenant-witness", insecureTenantAccepts);
        boolean insecureRoleAccepts = viewer.tenant().equals(owner.tenant());
        check("M-J-role-witness", insecureRoleAccepts);
        denied("M-J-role-killed", 403, () -> policy.update(viewer, "alpha-note", 3, "bad"));
        System.out.println("{\"component\":\"java\",\"passed\":" + CASES.size() +
            ",\"mutants_killed\":2,\"cases\":[" + String.join(",", CASES.stream().map(Policy::quote).toList()) + "]}");
    }
    /** Apply a competing update and return one only for the winning transaction. */
    private static int edit(Policy policy, Policy.Principal owner) {
        try { policy.update(owner, "alpha-note", 2, "race"); return 1; }
        catch (Policy.Failure error) { if (error.status != 409) throw error; return 0; }
    }
}
