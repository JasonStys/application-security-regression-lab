// Jason Stys: corrected tenant-policy HTTP fixture on numeric loopback; no vulnerable HTTP mode.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: JavaService — line 49
// symbol: main — line 51
// symbol: port — line 53
// variable: port — line 53
// variable: server — line 55
// variable: workers — line 56
// variable: policy — line 58
// symbol: origin — line 59
// variable: origin — line 59
// symbol: handle — line 71
// symbol: origin — line 71
// symbol: port — line 71
// symbol: headers — line 73
// variable: headers — line 73
// symbol: path — line 77
// variable: path — line 77
// symbol: identity — line 84
// variable: identity — line 84
// symbol: note — line 86
// variable: fields — line 88
// variable: note — line 90
// symbol: length — line 98
// variable: length — line 98
// variable: raw — line 100
// variable: fields — line 103
// variable: note — line 106
// symbol: send — line 117
// symbol: status — line 117
// symbol: value — line 117
// symbol: headers — line 118
// variable: headers — line 118
// variable: charset — line 119
// variable: data — line 125
// END CODE MAP
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/** Bounded educational HTTP adapter; not a hardened public gateway or identity provider. */
final class JavaService {
    /** Bind only loopback, fixed handler pool/backlog, and arrange shutdown of this owned listener. */
    public static void main(String[] args) throws IOException {
        if (args.length != 1) throw new IllegalArgumentException("one_loopback_port_required");
        int port = Integer.parseInt(args[0]);
        if (port < 1 || port > 65535) throw new IllegalArgumentException("port_range");
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 16);
        ThreadPoolExecutor workers = new ThreadPoolExecutor(4, 4, 0, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(16), new ThreadPoolExecutor.AbortPolicy());
        Policy policy = new Policy();
        String origin = "http://127.0.0.1:" + port;
        server.setExecutor(workers);
        server.createContext("/", exchange -> handle(exchange, policy, origin, port));
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            server.stop(0);
            workers.shutdownNow();
        }));
        server.start();
        System.out.println("Local corrected authorization fixture: " + origin);
    }

    /** Enforce exact route/header/form boundaries, normalize fixed errors and close every exchange. */
    private static void handle(HttpExchange exchange, Policy policy, String origin, int port) throws IOException {
        try {
            var headers = exchange.getRequestHeaders();
            if (!headers.getOrDefault("Host", java.util.List.of()).equals(java.util.List.of("127.0.0.1:" + port)) ||
                headers.containsKey("Origin") && !headers.get("Origin").equals(java.util.List.of(origin)) ||
                "cross-site".equals(headers.getFirst("Sec-Fetch-Site"))) throw new Policy.Failure(403);
            String path = exchange.getRequestURI().getRawPath();
            if ("GET".equals(exchange.getRequestMethod()) && "/health".equals(path)) {
                send(exchange, 200, "{\"component\":\"java\",\"synthetic\":true}");
                return;
            }
            if (!"/record".equals(path)) throw new Policy.Failure(404);
            if (headers.getOrDefault("Authorization", java.util.List.of()).size() != 1) throw new Policy.Failure(401);
            Policy.Principal identity = Policy.principal(headers.getFirst("Authorization"));
            Map<String, String> fields;
            Policy.Note note;
            if ("GET".equals(exchange.getRequestMethod())) {
                fields = Policy.form(exchange.getRequestURI().getRawQuery());
                if (!fields.keySet().equals(Set.of("id"))) throw new Policy.Failure(400);
                note = policy.read(identity, fields.get("id"));
            } else if ("POST".equals(exchange.getRequestMethod())) {
                if (!headers.getOrDefault("Origin", java.util.List.of()).equals(java.util.List.of(origin)) ||
                    !headers.getOrDefault("X-Lab-Exercise", java.util.List.of()).equals(java.util.List.of("synthetic")) ||
                    !headers.getOrDefault("Content-Type", java.util.List.of()).equals(java.util.List.of("application/x-www-form-urlencoded")) ||
                    headers.containsKey("Transfer-Encoding")) throw new Policy.Failure(403);
                if (exchange.getRequestURI().getRawQuery() != null ||
                    headers.getOrDefault("Content-Length", java.util.List.of()).size() != 1) throw new Policy.Failure(400);
                int length = Integer.parseInt(headers.getFirst("Content-Length"));
                if (length < 1 || length > 4096) throw new Policy.Failure(413);
                byte[] raw = exchange.getRequestBody().readNBytes(length);
                if (raw.length != length || new String(raw, StandardCharsets.US_ASCII).indexOf('\ufffd') >= 0)
                    throw new Policy.Failure(400);
                fields = Policy.form(new String(raw, StandardCharsets.US_ASCII));
                if (!fields.keySet().equals(Set.of("id", "version", "body"))) throw new Policy.Failure(400);
                if (!fields.get("version").matches("[1-9][0-9]{0,3}")) throw new Policy.Failure(400);
                note = policy.update(identity, fields.get("id"), Integer.parseInt(fields.get("version")), fields.get("body"));
            } else throw new Policy.Failure(405);
            send(exchange, 200, Policy.json(note));
        } catch (Policy.Failure error) {
            send(exchange, error.status, "{\"error\":\"request_rejected\"}");
        } catch (IllegalArgumentException error) {
            send(exchange, 400, "{\"error\":\"request_rejected\"}");
        } finally { exchange.close(); }
    }

    /** Emit inert/no-store JSON with component identity, no CORS or request-content logging. */
    private static void send(HttpExchange exchange, int status, String value) throws IOException {
        var headers = exchange.getResponseHeaders();
        headers.set("Content-Type", "application/json; charset=utf-8");
        headers.set("X-Lab-Component", "java");
        headers.set("Cache-Control", "no-store");
        headers.set("X-Content-Type-Options", "nosniff");
        headers.set("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'");
        headers.set("Referrer-Policy", "no-referrer");
        byte[] data = value.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, data.length);
        exchange.getResponseBody().write(data);
    }
}
