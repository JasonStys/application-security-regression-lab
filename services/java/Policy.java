/** Jason Stys: authoritative tenant/operation policy, atomic revisions and bounded literal form parsing. */
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: policy — line 70
// definition: Policy — line 71
// definition: Principal — line 73
// symbol: owner — line 73
// symbol: tenant — line 73
// definition: Note — line 75
// symbol: body — line 75
// symbol: id — line 75
// symbol: tenant — line 75
// symbol: version — line 75
// symbol: or — line 76
// definition: Failure — line 77
// symbol: serialVersionUID — line 78
// variable: serialVersionUID — line 78
// symbol: status — line 79
// symbol: status — line 81
// variable: status — line 81
// variable: notes — line 83
// variable: FIXTURES — line 86
// symbol: authorization — line 92
// symbol: principal — line 92
// symbol: value — line 93
// variable: value — line 93
// symbol: id — line 99
// symbol: identity — line 99
// symbol: read — line 99
// symbol: value — line 102
// variable: value — line 102
// symbol: body — line 108
// symbol: expected — line 108
// symbol: id — line 108
// symbol: identity — line 108
// symbol: update — line 108
// symbol: current — line 109
// variable: current — line 109
// symbol: changed — line 115
// variable: changed — line 115
// symbol: raw — line 121
// variable: fields — line 123
// symbol: item — line 125
// variable: pair — line 126
// symbol: key — line 128
// variable: key — line 128
// symbol: raw — line 135
// symbol: unescape — line 135
// variable: bytes — line 136
// symbol: index — line 137
// variable: index — line 137
// variable: value — line 138
// symbol: high — line 141
// variable: high — line 141
// symbol: low — line 142
// variable: low — line 142
// symbol: quote — line 157
// symbol: value — line 157
// variable: result — line 158
// symbol: json — line 168
// symbol: value — line 168
// END CODE MAP
import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/** A synthetic record policy. Caller-supplied tenant/role fields never determine identity. */
final class Policy {
    /** Synthetic asserted principal used only by the closed fixture token table. */
    record Principal(String tenant, boolean owner) {}
    /** Immutable response snapshot; revisions refer to the entire record, not a client-side guess. */
    record Note(String id, String tenant, String body, int version) {}
    /** Fixed safe status category; never includes an input string or private note content. */
    static final class Failure extends RuntimeException {
        private static final long serialVersionUID = 1L;
        final int status;
        /** Construct a fixed boundary error from a numeric status. */
        Failure(int status) { super("request_rejected"); this.status = status; }
    }
    private final Map<String, Note> notes = new HashMap<>(Map.of(
        "alpha-note", new Note("alpha-note", "alpha", "Fictional Alpha maintenance", 1),
        "beta-note", new Note("beta-note", "beta", "Fictional Beta maintenance", 1)));
    private static final Map<String, Principal> FIXTURES = Map.of(
        "Bearer fixture-alpha-owner", new Principal("alpha", true),
        "Bearer fixture-alpha-viewer", new Principal("alpha", false),
        "Bearer fixture-beta-owner", new Principal("beta", true));

    /** Authenticate only public synthetic fixture IDs; these are not production credentials. */
    static Principal principal(String authorization) {
        Principal value = FIXTURES.get(authorization == null ? "" : authorization);
        if (value == null) throw new Failure(401);
        return value;
    }

    /** Return an immutable same-tenant record; missing/cross-tenant IDs both produce 404. */
    synchronized Note read(Principal identity, String id) {
        if (identity == null) throw new Failure(401);
        if (id == null || !id.matches("[a-z][a-z-]{0,63}")) throw new Failure(400);
        Note value = notes.get(id);
        if (value == null || !identity.tenant().equals(value.tenant())) throw new Failure(404);
        return value;
    }

    /** Atomically enforce tenant then operation authorization and expected version before changing any body. */
    synchronized Note update(Principal identity, String id, int expected, String body) {
        Note current = read(identity, id);
        if (!identity.owner()) throw new Failure(403);
        if (body == null || body.isBlank() || body.length() > 1000 ||
            body.codePoints().anyMatch(value -> value < 32)) throw new Failure(400);
        if (expected < 1 || expected != current.version() || current.version() >= 1000)
            throw new Failure(409);
        Note changed = new Note(id, current.tenant(), body, current.version() + 1);
        notes.put(id, changed);
        return changed;
    }

    /** Parse bounded URL-encoded ASCII transport into strict UTF8 fields; reject duplicates rather than overwrite. */
    static Map<String, String> form(String raw) {
        if (raw == null || raw.length() > 4096) throw new Failure(400);
        Map<String, String> fields = new HashMap<>();
        if (raw.isEmpty()) return fields;
        for (String item : raw.split("&", -1)) {
            String[] pair = item.split("=", 2);
            if (pair.length != 2 || fields.size() >= 8) throw new Failure(400);
            String key = unescape(pair[0]);
            if (fields.putIfAbsent(key, unescape(pair[1])) != null) throw new Failure(400);
        }
        return fields;
    }

    /** Decode once with malformed-UTF8 rejection; never recursively reinterpret percent-encoded user content. */
    private static String unescape(String raw) {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        for (int index = 0; index < raw.length(); index++) {
            char value = raw.charAt(index);
            if (value == '%') {
                if (index + 2 >= raw.length()) throw new Failure(400);
                int high = Character.digit(raw.charAt(++index), 16);
                int low = Character.digit(raw.charAt(++index), 16);
                if (high < 0 || low < 0) throw new Failure(400);
                bytes.write(high * 16 + low);
            } else {
                if (value > 127) throw new Failure(400);
                bytes.write(value == '+' ? 32 : value);
            }
        }
        try {
            return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes.toByteArray())).toString();
        } catch (CharacterCodingException error) { throw new Failure(400); }
    }

    /** Encode bounded valid Unicode as a JSON string, including controls/quotes/backslashes without HTML use. */
    static String quote(String value) {
        StringBuilder result = new StringBuilder("\"");
        for (char item : value.toCharArray()) {
            if (item == '"' || item == '\\') result.append('\\').append(item);
            else if (item < 32) result.append(String.format("\\u%04x", (int)item));
            else result.append(item);
        }
        return result.append('"').toString();
    }

    /** Produce a fixed-field JSON response, not interpolated HTML or executable JavaScript. */
    static String json(Note value) {
        return "{\"id\":" + quote(value.id()) + ",\"body\":" + quote(value.body()) +
            ",\"version\":" + value.version() + "}";
    }
}
